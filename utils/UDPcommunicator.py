import socket

class UDPcommunicator:

    def __init__(self, recv_port:int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Send broadcast
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Receive broadcast
        self.socket.bind(("", recv_port))
        self.socket.settimeout(4)

    def recv_msg(self):
        try:
            data, addr = self.socket.recvfrom(1024)
            return data, addr
        except self.socket.timeout:
                print("Timeout")
        
    def send_msg(self, data, ip:str, port:int) -> None:
        self.socket.sendto(data, (ip, port))

    def close(self):
        self.socket.close()


