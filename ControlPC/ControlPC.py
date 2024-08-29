import time, threading, logging
import pandas as pd
import threading
import os, sys
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)
from dataclasses import dataclass
from UDPcommunicator import UDPcommunicator
from ProtobufTransformer import encode_msg, decode_msg
from Messages_pb2 import SYSTEM, INFORMATION, MOTORS, TRANSMIT, SET_FREQUENCY, SAMPLING, GET_RSSI, NOTHING 
from plotter import plot_3d_antenna, plot_heatmap_antenna
from tools import read_toml_conf_controlPC, Logger
from typing import Callable
from functools import partial

@dataclass
class UnitStatus:
    operable: bool
    status: str



class ControlPC:
    def __init__(self, control_port=4444, target_port=5555, toml_conf_file_path="Conf_ControlPC.toml") -> None:
        self.unit_status = {"TxUUT": UnitStatus(False, "Not connected"), "RxMeas": UnitStatus(False, "Not connected")}
        self.conf_file = toml_conf_file_path
        self.broadcast_address = '192.168.2.255'
        self.logger = Logger('ControlPC').get_logger()
        self.control_port = control_port
        self.comm = UDPcommunicator(self.control_port)
        self.target_port = target_port
        self.unit_addrs = {"TxUUT": "", "RxMeas": ""}
        self.idx_fail = 0
        self.init_params()
        self.init_events()
        self.init_results_file()
        self.active = True
        self.results = []
        self.broadcast_systems(txt="Ready?")
        self.ready_event.wait(timeout=0.2)

    def init_events(self):
        self.ready_event = threading.Event()
        self.motors_event = threading.Event()
        self.freq_event = threading.Event()
        self.sample_event = threading.Event()
        self.transmit_event = threading.Event()
        self.no_transmit_event = threading.Event()
        self.rssi_event = threading.Event()

    def init_params(self):
        self.data = read_toml_conf_controlPC(self.conf_file)
        self.change_freq = True
        self.curr_freq = self.data["freq"]["start"]
        self.curr_az = self.data["azimuth"]["start"]
        self.curr_pitch = self.data["pitch"]["start"]

    def init_results_file(self):
        self.csv_file = f"{self.data['results_file_name']}.csv"
        df = pd.DataFrame(columns=['Azimuth', 'Pitch', 'Frequency', 'RSSI', 'Samples', 'STD'])
        df.to_csv(self.csv_file, index=False)

    def handle_recv_msg(self):
        while True:
            try:
                ser_data, addr = self.comm.recv_msg()
                msg_type, msg_dict = decode_msg(ser_data)
            except:
                print("Can't resolve message")
                continue
            if msg_type == SYSTEM:
                whoami, status = msg_dict["whoami"], msg_dict["status"]
                if whoami == "ControlPC":
                    self.active = False
                    break
                self.handle_recv_sys_msg(whoami, status, addr)
            elif msg_type == INFORMATION:
                info = msg_dict["info"]
                if info == "Finished":
                    self.active = False
                    break
                else:
                    self.handle_recv_info_msg(info, addr)
            elif msg_type == GET_RSSI:
                self.handle_recv_rssi_msg(msg_dict)
    
    def handle_recv_sys_msg(self, whoami: str, status: str, addr: tuple):
        if whoami == "TxUUT":
            self.unit_addrs["TxUUT"] = addr[0]
        else:
            self.unit_addrs["RxMeas"] = addr[0]
        # If the unit is ready
        if status == "Ready":
            self.unit_status[whoami].operable = True
            self.unit_status[whoami].status = status
            self.logger.info(f"{whoami} is Ready\n")
            if self.unit_status["TxUUT"].operable and self.unit_status["RxMeas"].operable:
                self.logger.info("TxUUT & RxMeas are both active")
                self.ready_event.set()
        else:
            self.unit_status[whoami].operable = False
            self.unit_status[whoami].status = status
            self.logger.error(f"{whoami} is not operational, {status}\n")

    def handle_recv_info_msg(self, info, addr):
        if addr[0] == self.unit_addrs["TxUUT"]:
            if "Motors" in info:
                self.motors_event.set()
            elif "Stopped" in info:
                self.no_transmit_event.set()
            else:
                self.transmit_event.set()
        else:
            if "Changed" in info:
                self.freq_event.set()
            elif "Sampling already" in info or "Started" in info:
                self.sample_event.set()
    
    def handle_recv_rssi_msg(self, msg_dict):
        if not bool(msg_dict):
            self.rssi, self.samples, self.std = 0, 0, 0
        else:
            if "rssi" not in msg_dict.keys():
                self.rssi = 0
            else:
                self.rssi = msg_dict["rssi"]
            if "samples" not in msg_dict.keys():
                self.samples = 0
            else:
                self.samples = msg_dict["samples"]
            if "std" not in msg_dict.keys():
                self.std = 0
            else:
                self.std = msg_dict["std"]
        self.logger.info(f"RSSI = {self.rssi} dBm, Samples = {self.samples}, STD = {self.std}")
        self.rssi_event.set()

    def send_task(self, op_fcn : Callable, event:threading.Event, log_req_str:str, log_ack_str:str, log_fail_str:str):
        idx_fail_message = 0
        while idx_fail_message < 10:
                self.logger.info(log_req_str + f"{idx_fail_message + 1}/10 times")
                op_fcn()
                flag = event.wait(timeout = 5)
                if flag is False:
                    self.logger.warning(f"Didn't receive an ack, sending again")
                    idx_fail_message += 1
                else:
                    event.clear()
                    self.logger.info(log_ack_str)
                    break
        else:
            self.logger.error(log_fail_str)
        

    def tx_rx(self, freq: float=900e6, power: float=0, wave_type: str="CW", on_off: bool=False, sleep: float=0.3):
        if self.change_freq:
            if self.unit_status["RxMeas"].operable:
                self.change_freq = False
                op_fcn = partial(self.set_freq, freq)
                self.send_task(op_fcn, self.freq_event, 
                                log_req_str=f'Request to set freq: {self.curr_freq:.3f} Hz\n',
                                log_ack_str="Set freq\n", log_fail_str="Can't set freq!\n")
            else:
                self.logger.error("CaribouLite is not connected, continuous operation stops")            
                return False
            
        if self.unit_status["TxUUT"].operable:
            op_fcn = partial(self.transmit, freq, power, wave_type, True)
            self.send_task(op_fcn, self.transmit_event, 
                            log_req_str=f'Request to Tx:\nF: {freq:.3f} Hz, Pow: {power:.3f} dB, Type: {wave_type}\n',
                            log_ack_str="Transmitting\n", log_fail_str="Can't transmit!\n")
        else:
            self.logger.error("Transmitter is not connected, continuous operation stops")
            return False
        
        if self.unit_status["RxMeas"].operable:
            op_fcn = partial(self.sample, True)
            self.send_task(op_fcn, self.sample_event, 
                            log_req_str=f'Request to sample',
                            log_ack_str="Sampling", log_fail_str="Can't sample!")
        else:
            self.logger.error("CaribouLite is not connected, continuous operation stops")
            return False

        self.rssi_event.wait()
        time.sleep(0.1)

        if self.unit_status["TxUUT"].operable:
            op_fcn = partial(self.transmit, freq, power, wave_type, False)
            self.send_task(op_fcn, self.no_transmit_event, 
                            log_req_str=f'Request to stop Tx:\nF: {freq:.3f} Hz, Pow: {power:.3f} dB, Type: {wave_type}\n',
                            log_ack_str="Stop transmitting\n", log_fail_str="Can't transmit!\n")
        else:
            self.logger.error("Transmitter is not connected, continuous operation stops")
            return False
        
        self.write_results_to_file()
        return True

    def continuous_tx_rx(self):

        while(self.curr_freq <= self.data["freq"]["stop"]):
            if self.unit_status["TxUUT"].operable:
                op_fcn = partial(self.move_motors, self.curr_az, self.curr_pitch)
                self.send_task(op_fcn, self.motors_event, 
                                log_req_str=f'Request to move motors to: Azimuth = {self.curr_az:.2f}, Pitch = {self.curr_pitch:.2f}\n',
                                log_ack_str="Moved motors", log_fail_str="Can't move motors!")
            else:
                self.logger.error("Motors are not connected, continuous operation stops")
                break
            #time.sleep(5)
        
            if not self.tx_rx(self.curr_freq, self.data["power"], self.data["wave_type"], True, self.data["sleep"]):
                break

            if self.curr_pitch < self.data["pitch"]["stop"]:
                self.curr_pitch += self.data["pitch"]["step"] #  Increase pitch

            elif self.curr_az < self.data["azimuth"]["stop"] and self.curr_pitch == self.data["pitch"]["stop"]:
                self.curr_az += self.data["azimuth"]["step"] # Increase azimuth
                self.curr_pitch = self.data["pitch"]["start"] #  Reset pitch

            elif self.curr_freq <= self.data["freq"]["stop"] and self.curr_az == self.data["azimuth"]["stop"]  and self.curr_pitch == self.data["pitch"]["stop"]:
                plot_heatmap_antenna(csv_path=self.csv_file, title=f"{self.curr_freq:.2f} Hz")
                #plot_3d_antenna(csv_path=self.csv_file, title=f"{self.curr_freq:.2f} Hz")
                self.curr_freq += self.data["freq"]["step"] #  Increase freq
                self.curr_az = self.data["azimuth"]["start"] #  Reset azimuth
                self.curr_pitch = self.data["pitch"]["start"] #  Reset pitch
                self.change_freq = True

            self.logger.info('Finished Iteration\n')
        self.logger.info('Finished all\n') 
        self.init_params()

    def broadcast_systems(self, txt):
        msg = encode_msg({"whoami" : "ControlPC", "status": txt}, SYSTEM)
        self.comm.send_msg(data=msg, ip=self.broadcast_address, port=self.target_port)
         
    def move_motors(self, azimuth: float, pitch: float):
        self.msg = encode_msg({"alpha" : azimuth, "beta": pitch}, MOTORS)
        self.comm.send_msg(data=self.msg, ip=self.unit_addrs["TxUUT"], port=self.target_port)

    def transmit(self, freq: float=900e6, power: float=0, wave_type: str="CW", onoff: bool=False):
        self.msg = encode_msg({"frequency":freq, "power":power, "wavetype":wave_type, "onoff":onoff}, TRANSMIT)
        self.comm.send_msg(data=self.msg, ip=self.unit_addrs["TxUUT"], port=self.target_port)
        
    def set_freq(self, freq: float):
        self.msg = encode_msg({"frequency":freq}, SET_FREQUENCY)
        self.comm.send_msg(data=self.msg, ip=self.unit_addrs["RxMeas"], port=self.target_port)
        
    def sample(self, onoff: bool=False):
        self.msg = encode_msg({"onoff":onoff}, SAMPLING)
        self.comm.send_msg(data=self.msg, ip=self.unit_addrs["RxMeas"], port=self.target_port)
        
    def get_status(self):
        return self.active
    
    def write_results_to_file(self):
        results = {"Azimuth" :self.curr_az, "Pitch" : self.curr_pitch, 'Frequency' : self.curr_freq,
                    "RSSI": self.rssi, "samples": self.samples, "STD": self.std}
        df = pd.DataFrame([results])
        df.to_csv(self.csv_file, mode='a', header=False, index=False)
        
    def start(self):
        self.recv_thread = threading.Thread(target=self.handle_recv_msg)
        self.recv_thread.start()
    
    def inner_off(self):
        msg = encode_msg({"whoami" : "ControlPC", "status": "Inner_off"}, SYSTEM)
        self.comm.send_msg(data=msg, ip="", port=self.control_port)

    def close(self):
        self.recv_thread.join() # Close thread
        self.comm.close()


