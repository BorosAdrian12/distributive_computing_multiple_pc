import socket
import struct
import pickle
import inspect
import time 
import random
from packet import Packet
import threading as th

dataFromFunc=[]
intervalList=[]

def test():
    print("<inca nu am primit functie>")
    

class client:
    
    def __init__(self,host,port):
        self.id=random.randint(0,100000)#this could be a username
        self.host=host
        self.port=port
        self.client_socket=None
        self.counterStartServer=0
        self.counterNewStartFunction=0
        self.Function=""
        self.flagExecWork=False
        self.queueResponse=[]
        self.countFile=0
    
    def send(self,command,data):
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

            print(f"Received data (size:{pa.command}): {pa.data}")
    
    def send_data_to_store(self,data):
        # data_serielized=pickle.dumps(data)
        print("  >>suntem in send_data_to_store")
        
        # #i've send the packet with data size
        global dataFromFunc
            
        try:
            while self.flagExecWork==True or len(dataFromFunc)>0:
                print("  >>suntem in while")
                if(len(dataFromFunc)>0):
                    print("  >>exista date de trimis")
                    format_data={
                        "path":f"store/client_{self.id}",
                        "filename":f"/file_{self.countFile}.txt",
                        "data":dataFromFunc.pop(0)
                    }
                    print(f"format_data={format_data}")
                    format_data=pickle.dumps(format_data)
                    self.countFile+=1
                    packet=Packet("saveDataFunction",format_data)
                    print("  >>se trimite pachetul")
                    self.send_and_recieve_packet(packet)
                else:
                    time.sleep(0.5)
        except Exception as e:
            print("a esuat")
            print(e)
        pass
    
    def send_and_recieve_packet(self,packet):
        packet=pickle.dumps(packet)
        self.client_socket.sendall(struct.pack("!Q", len(packet)))
        self.client_socket.sendall(packet)


        packet_size=self.client_socket.recv(8)
        packet_size = struct.unpack("!Q", packet_size)[0]
        p=self.client_socket.recv(packet_size)
        p=pickle.loads(p)
        return p

        #send the packet
        pass
    
    def execute_function_definition(self,code):
        try:
            print("->se executa functia")
            # run=None
            print(f"counterStartServer={self.counterStartServer}")
            print(f"counterNewStartFunction={self.counterNewStartFunction}")
            if self.Function!="" and self.counterStartServer>self.counterNewStartFunction:
                str_func=self.Function
                print("=== AR TREBUII SA RULEZE FUNCTIA ===")
                print(str_func)
                exec(str_func, globals())
                global flagExecWork , dataFromFunc
                self.flagExecWork=True
                thread_send_data=th.Thread(target=self.send_data_to_store,args=(dataFromFunc,))
                thread_send_data.start()
                test()
                self.flagExecWork=False
                thread_send_data.join()
                #aici trebuie sa reintre threadul pentru transmitere date
                self.counterNewStartFunction+=1
        except Exception as e:
            print("a esuat functia")
            print(e)
    
    def C_Connect(self):
        try: 
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))

            establish_connection=Packet("connection","i have connected")
            establish_connection=self.send_and_recieve_packet(establish_connection)

            first_response_packet = Packet("statusServer","")
            print("->se trimite cererea pentru status")
            print(first_response_packet.command,first_response_packet.data)
            xx = self.send_and_recieve_packet(first_response_packet)
            self.counterStartServer=xx.data["counterStartServer"]

            self.counterNewStartFunction=self.counterStartServer
            print(f"counterStartServer={xx.data['counterStartServer']}")
            {
                #AR TREBUII SA FIE UN FELUL URMATOR
            #1. intrebi care este status server
            #2. in functie de status executi comanda , daca zice ca ii idle nu faci nimic
            #3. tot o sa intrebi din 5 in 5 secunde de status dar in functie de status o sa faci chestii
            #4. o sa fie in faze , adica prima data ii idle , dupa sendFunctions , dupa loadIntervals (in viitor si dataseturi), si dupa executare cu return
            #5. se repeta procesul de la 1
            #extra , daca serverul trimite ceva cu close atunci aia ye
            # server    status->    client
            # server    <-executa status   client
            # server    send function->    client
            # server    <-return confirmation   client
            # server    send intervals->    client
            # server    <-return process data   client

            }
            counter=0
            client_still_running=True

            while client_still_running==True: 
                time.sleep(3)
                print("1)->se trimite cererea pentru status")

                response_packet = Packet("statusServer","")
                response_packet = self.send_and_recieve_packet(response_packet)
                self.counterStartServer=response_packet.data["counterStartServer"]

                print("1)->se asteapta raspunsul STATUS")

                print(f"=- ce am primit de la status = (command:{response_packet.command}), data:`{response_packet.data}`")
                if response_packet.command=="statusServer":
                    print(f"response_packet.data['state']={response_packet.data['state']}")
                    if response_packet.data["state"]=="idle":
                        x=self.send_and_recieve_packet(Packet("test",""))
                        print(f">>>am primit raspunsul de la test {x.data}")
                        
                    elif response_packet.data["state"]=="close":
                        client_still_running=False
                        print("->serverul a inchis")
                        print("->se inchide clientul")

                    elif response_packet.data["state"]=="sendFunction":
                        #get the function
                        
                        pass
                        func_pack=self.send_and_recieve_packet(Packet("sendFunction",""))
                        self.Function=func_pack.data
                        print(f"len of function: {len(self.Function)}")

                    elif response_packet.data["state"]=="startFunction":
                        self.execute_function_definition(self.Function)
                        
                    elif response_packet.data["state"]=="loadInterval":
                        global intervalList
                        response_packet=self.send_and_recieve_packet(Packet("loadInterval",""))
                        if response_packet.data["intervalSend"]<=response_packet.data["maxInterval"]:
                            intervalList.append(response_packet.data["interval"])
                        print(f"intervalList existent={intervalList}")
                        print(f"data din pachet={response_packet.data}")
                        # print(f"intervalList={intervalList}")
                        pass
                    
                            
                        
                        
                {
                # if False:
                #     print("->se trimite cererea pentru functie")
                #     request_function=Packet("sendFunction","")
                #     request_function=pickle.dumps(request_function)
                #     self.client_socket.sendall(struct.pack("!Q", len(request_function)))
                #     self.client_socket.sendall(request_function)

                #     print("->se asteapta raspunsul")

                #     response_size = self.client_socket.recv(8)
                #     response_size = struct.unpack("!Q", response_size)[0]
                #     response_packet = self.client_socket.recv(response_size)
                #     response_packet = pickle.loads(response_packet)

                #     # print(f"Received function (command:{response_packet.command}): `{response_packet.data}`")
                #     print(f"len of function: {len(response_packet.data)}")
                #     print(f"function: {response_packet.data}")
                #     #AICI AR TREBUII SA INTREBI DE PARAMETRII , DAR MAI BINE AR TREBUII SA VEZI DE STATUS AL SERVERULUI

                #     #CE II MAI JOS II DOAR UN TEST
                #     try:
                #         print("->se executa functia")
                #         # run=None
                #         if response_packet.data!="":
                #             str_func=response_packet.data
                #             exec(str_func, globals())
                #             test()
                #     except Exception as e:
                #         print("a esuat functia")
                #         print(e)
                #         pass
                #     print(f"counter : {counter}")
                
                # if response_packet.data["state"]=="idle":
                #     print("->serverul este idle")
                #     print("->se asteapta 5 secunde")
                #     # time.sleep(5)
                #     # continue}
                }
                counter+=1
                print(f"counter : {counter}")
                print("========================= END OF LOOP =========================")
                time.sleep(3)
            
        except Exception as e:
            print("a esuat")
            print(e)
            self.client_socket.close()
        pass
        
Cl=client('127.0.0.1',18001)
Cl.C_Connect()