import threading
import os, sys, time
from ServoController import MotorsController
from transmitter_interface import Transmitter
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)
from UDPcommunicator import UDPcommunicator
from ProtobufTransformer import encode_msg, decode_msg
from Messages_pb2 import SYSTEM, INFORMATION, MOTORS, TRANSMIT, SET_FREQUENCY, SAMPLING, GET_RSSI, NOTHING 


class TxUUT:
    def __init__(self) -> None:
        self.control_port = 4444
        self.comm = UDPcommunicator(5555)
        self.motors = MotorsController(channel1=0, channel2=1)
        self.active = True
        self.transmitter = Transmitter() # Implanment your own transmitter!
        self.transmitter.connect()
        self.recv_thread = threading.Thread(target=self.handle_recv_msg)
        self.recv_thread.start()
        self.stop_recv_loop = False
                
    def handle_recv_msg(self):
        while True:
            try:
                if self.stop_recv_loop is True:
                    try:
                        resp = {"whoami" : "TxUUT", "status": "Shutdown"}
                        self.comm.send_msg(encode_msg(resp, SYSTEM), self.control_ip, self.control_port)
                    except:
                        print("No connections to ControlPC")
                    self.active = False
                    break
                ser_data, addr = self.comm.recv_msg()
                self.control_ip = addr[0]
                msg_type, msg_dict = decode_msg(ser_data)
            except:
                print("Can't resolve message")
                continue
            if msg_type == SYSTEM:
                self.operational = True
                print(f"Whoami: {msg_dict['whoami']}, status: {msg_dict['status']}")
                if msg_dict["status"]  == "Ready?":
                    resp = {"whoami" : "TxUUT", "status": "Ready"}
                    self.comm.send_msg(encode_msg(resp, SYSTEM), self.control_ip, self.control_port)
                else:
                    self.active = False
                    resp = {"info" : "Finished"}
                    self.comm.send_msg(encode_msg(resp, INFORMATION), self.control_ip, self.control_port)
                    break
            elif msg_type == MOTORS:
                if bool(msg_dict) is False:
                    azimuth, pitch = 0, 0
                elif "alpha" not in msg_dict:
                    azimuth, pitch = 0, msg_dict["beta"]
                elif "beta" not in msg_dict:
                    azimuth, pitch = msg_dict["alpha"] , 0
                else:
                    azimuth, pitch = msg_dict["alpha"] , msg_dict["beta"]
                if azimuth > 180:
                    azimuth -= 180
                    pitch = 180 - pitch
                print(f"Moving to azimuth: {azimuth}, pitch: {pitch}")
                self.motors.run(azimuth, pitch)
                time.sleep(0.8)
                resp = {"info" : "Motors Moved"}
                self.comm.send_msg(encode_msg(resp, INFORMATION), self.control_ip, self.control_port)
            elif msg_type == TRANSMIT:
                try:
                    if "onoff" in msg_dict.keys():
                        self.curr_freq, self.curr_power, self.curr_wave_type = msg_dict["frequency"], msg_dict["power"], msg_dict["wavetype"]
                        self.transmitter.transmit(msg_dict["frequency"], msg_dict["power"], msg_dict["wavetype"], msg_dict["onoff"])
                        info = "Transmission"
                        print(f"Transmit: f = {msg_dict['frequency']}, p = {msg_dict['power']}, wave type = {msg_dict['wavetype']}")
                    else:
                        self.transmitter.transmit(msg_dict["frequency"], msg_dict["power"], msg_dict["wavetype"], False)
                        info = "Stopped Transmission"
                        print(f"Stop transmit: f = {msg_dict['frequency']}, p = {msg_dict['power']}, wave type = {msg_dict['wavetype']}")
                    resp = {"info" : info}
                    self.comm.send_msg(encode_msg(resp, INFORMATION), self.control_ip, self.control_port)
                except:
                    self.transmitter.transmit(msg_dict["frequency"], msg_dict["power"], msg_dict['wavetype'], False)
                    resp = {"info": "Can't control transmission"}
                    self.comm.send_msg(encode_msg(resp, INFORMATION), self.control_ip, self.control_port)

   
    def get_status(self):
        return self.active


    def shutdown_msg(self):
        resp = {"info": "Shutdown"}
        self.comm.send_msg(encode_msg(resp, INFORMATION), self.control_ip, self.control_port)
                
    def stop(self):
        print("TxUUT shutdown")
        self.recv_thread.join() # Close thread
        try:
            self.transmitter.transmit(self.curr_freq, self.curr_power, self.curr_wave_type, False) # Stop trasmittion
        except:
            print("No transmission")
        finally:
            self.transmitter.disconnect()
            self.motors.default() # Reset motors
            self.comm.close() # Close socket
        
