import Messages_pb2
from Messages_pb2 import MessageType as m_type
from google.protobuf.json_format import MessageToDict



def encode_msg(data_dict:dict, msg_type:int):
    msg_wrapper = Messages_pb2.Wrapper()
    msg_wrapper.type = msg_type

    if msg_type == m_type.SYSTEM:
        msg = Messages_pb2.System()
        msg.whoami, msg.status  = data_dict["whoami"], data_dict["status"]
        msg_wrapper.sys_msg.CopyFrom(msg)

    elif msg_type == m_type.INFORMATION:
        msg = Messages_pb2.Information()
        msg.info = data_dict["info"]
        msg_wrapper.info_msg.CopyFrom(msg) 
    
    elif msg_type == m_type.MOTORS:
        msg = Messages_pb2.Motors()
        msg.alpha, msg.beta = data_dict["alpha"], data_dict["beta"]
        msg_wrapper.motors_msg.CopyFrom(msg)

    elif msg_type == m_type.TRANSMIT:
        msg = Messages_pb2.Transmit()
        msg.frequency, msg.power = data_dict["frequency"], data_dict["power"]
        msg.wavetype, msg.onoff = data_dict["wavetype"], data_dict["onoff"]
        msg_wrapper.tx_msg.CopyFrom(msg)

    elif msg_type == m_type.SET_FREQUENCY:
        msg = Messages_pb2.SetFrequency()
        msg.frequency = data_dict["frequency"]
        msg_wrapper.freq_msg.CopyFrom(msg)   

    elif msg_type == m_type.SAMPLING:
        msg = Messages_pb2.Sampling()
        msg.onoff = data_dict["onoff"]
        msg_wrapper.sample_msg.CopyFrom(msg)
    
    elif msg_type == m_type.GET_RSSI:
        msg = Messages_pb2.GetRssi()
        msg.rssi = data_dict["rssi"]
        msg.samples = data_dict["samples"]
        msg.std = data_dict["std"]
        msg_wrapper.rssi_msg.CopyFrom(msg)

    return msg_wrapper.SerializeToString()
        
def decode_msg(serialized_data):
    msg_wrapper = Messages_pb2.Wrapper()
    msg_wrapper.ParseFromString(serialized_data)
    msg_type = int(repr(msg_wrapper.type))

    if msg_type == m_type.SYSTEM:
        msg_contents = MessageToDict(msg_wrapper.sys_msg)

    elif msg_type == m_type.INFORMATION:
        msg_contents = MessageToDict(msg_wrapper.info_msg)

    elif msg_type == m_type.MOTORS:
        msg_contents = MessageToDict(msg_wrapper.motors_msg)

    elif msg_type == m_type.TRANSMIT:
        msg_contents = MessageToDict(msg_wrapper.tx_msg)

    elif msg_type == m_type.SET_FREQUENCY:
        msg_contents = MessageToDict(msg_wrapper.freq_msg)

    elif msg_type == m_type.SAMPLING:
        msg_contents = MessageToDict(msg_wrapper.tx_msg)

    elif msg_type == m_type.GET_RSSI:

        msg_contents = MessageToDict(msg_wrapper.rssi_msg)
    return msg_type, msg_contents    

