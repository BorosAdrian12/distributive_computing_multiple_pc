import socket
import struct
import pickle
import inspect
import inspect
import time 
from packet import Packet



class HQ:
    #aici am sa am nevoie de doua threaduri , unu care trimite si altul care primeste
    def __init__(self,host,port):
        self.host=host
        self.port=port
        self.client_socket=None
        self.counterStartFunction=0
    def s_send(self,command,data):
        packet=Packet(command,data)
        packet=pickle.dumps(packet)
        self.client_socket.sendall(struct.pack("!Q", len(packet)))
        self.client_socket.sendall(packet)
        print("sent")
        print("astept raspuns")
        packet_size=self.client_socket.recv(8)
        packet_size = struct.unpack("!Q", packet_size)[0]

        pa=self.client_socket.recv(packet_size)
        pa=pickle.loads(pa)

    def send(self,command,data):
        pachet=Packet(command,data)
        pachet=pickle.dumps(pachet)

        self.client_socket.sendall(struct.pack("!Q", len(pachet)))
        self.client_socket.sendall(pachet)

        pachet_size=self.client_socket.recv(8)
        pachet_size = struct.unpack("!Q", pachet_size)[0]

        pa=self.client_socket.recv(pachet_size)
        pa=pickle.loads(pa)
        print(f"Received data (size:{pa.command}): {pa.data}")
        print("sent")
    def connect(self):
        try:
            # establish a connection
            print(f"Connecting to {self.host}:{self.port}")
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            command_input=""
            data_input=""
            while command_input!="exit":
                
                command_input = input("Enter your command (type 'exit' to quit): ")
                

                if command_input=="<STOP>":
                    #ar trebuii sa fie ceva cu "am iesit , peace"
                    break
                elif command_input=="sendFunction":
                    with open("function.txt", 'r') as file:
                        data_input = file.read()
                elif command_input=="updateStatus":
                    data_input = input("Enter your data: ")
                elif command_input=="startFunction":
                    data_input="the function is starting"
                    pass
                elif command_input=="shareFunction":
                    command_input="updateStatus"
                    data_input="sendFunction"
                    pass
                elif command_input=="shareInterval":
                    command_input="updateStatus"
                    data_input="loadInterval"
                    pass
                elif command_input=="sendInterval":
                    data_input=[[1,10],[10,20],[20,30]]
                    pass
                
                self.send(command_input,data_input)
            self.client_socket.close()
        except Exception as e:
            print("a esuat")
            print(e)
if __name__ == "__main__":
    HQ=HQ('localhost',18003)
    HQ.connect()