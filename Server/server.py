import socket
import struct
import pickle
import inspect
import time 
import threading as th
import multiprocessing as mp
import os
from packet import Packet
from random import randint

class Com:
    def __init__(self, conn=None, addr=None, pipe=None, a=1,b=1):
        self.conn = conn
        self.addr = addr
        self.pipe = pipe
        self.intervalSend=a
        self.maxInterval=b
    def __str__(self):
        return f"Com(addr={self.addr}, internalSend={self.intervalSend}, maxInternal={self.maxInterval})"

class Server:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ext_server_socket = None
        self.int_server_socket = None
        self.listConn = []
        
        self.manager = mp.Manager()
        self.shared_dict = self.manager.dict()
        self.ConnectionList=self.manager.list()
        self.Interval=self.manager.list()
        self.shared_dict["stateExternalServer"]=True
        self.shared_dict["listConn"]=[]
        self.shared_dict["function_source"]=""
        self.shared_dict["interval"]=[]
        self.shared_dict["statusExternalServer"]={"state":"idle","data":[],"counterStartServer":0}
        self.shared_dict["intervals"]=[]
        self.Semaphore_from_Intern_Server=True
        self.Semaphore_FOR_Intern_Server=True
        self.shared_dict["counterStartServer"]=0
        self.thread_intern_server = None
        self.thread_extern_server = None
        self.lockVariables = mp.Lock()
        #UNDEVA IN DICTIONAR TREBUIE SA ADAUGI FUCTIA CARE TREBUIE TRIMISA
        #TOT IN DICTIONAR TREBUIE SA ADAUGI CARE SUNT INTERVALELE PENTRU FIECARE

    def find_connection_by_address(self, conn):
        for c in self.listConn:
            if c.conn == conn:
                return c
        return None
    
    def remove_conn_in_list(self,conn):
        for c in self.shared_dict["listConn"]:
            if c.conn == conn:
                print("am gasit conexiunea")
                pass
                # return c
    
    
    def recieve_data_from_client(self,packet):
        print("===recieve data from client===")
        try:
            f=pickle.loads(packet)
            print("=packet=")
            print(f)
            if os.path.exists(f["path"])!=True:
                print("CREATE THE PATH")
                os.makedirs(f["path"])
            
            with open(f["path"]+f["filename"],'wb') as file:
                file.write(pickle.dumps(f["data"]))
            # format_data=pickle.loads(packet.data)

            # print("===data recived from client===")
            # print(format_data)
            
        except Exception as e:
            print(f"Error: {e}")

        #trebuie sa fie salvat ce este in packet


        # packet_size = conn.recv(8)
        # packet_size = struct.unpack("!Q", packet_size)[0]
        # packet = conn.recv(packet_size)
        

        pass
    
    def find_Com_by_addr(self,instances, addr):
        print("{")
        # print(f"len listConn is : {len(self.ConnectionList)}")
        # for i in range(len())

        for instance in self.ConnectionList:
            print(f"instance is : {instance.addr}")
            if instance.addr == addr:
                return instance
        print("}")
        return None
        print("}")

    def find_and_modify_Com_by_addr(self, addr, mod_com):
        
        for i, instance in enumerate(self.ConnectionList):
            # print(f"instance is : {instance.addr}")
            if instance.addr == addr:
                self.ConnectionList[i] = mod_com  # Update the element in the managed list by index
                break
                # return instance
        # print("Instance not found.")

    def send_interval_to_client(self,addr):
        print(f"send interval to client {addr}")
        ComVar=self.find_Com_by_addr(self.ConnectionList,addr)
        print(f"ComVar is : {ComVar}")
        ret_var=[]
        if ComVar!=None:
            if len(self.Interval)>0 and ComVar.intervalSend<ComVar.maxInterval:
                print("===SCOT ACUMA DIN INTERVAL===")
                with self.lockVariables:
                
                    x=self.Interval.pop(0)
                    print(f"interval send is : {x}")
                    ret_var=x
                    
                    # intervalSend[0]+=1
                    ComVar.intervalSend+=1
            self.find_and_modify_Com_by_addr(addr,ComVar)

        format_data={
            "interval":ret_var,
            "maxInterval":ComVar.maxInterval,
            "intervalSend":ComVar.intervalSend
        }
        print(f"interval send is : {format_data}\n\n")
        return format_data
        pass
    def H_handle_connection(self, conn, addr, child_conn):
        print("TEST_HANDLE_CONNECTION")
        try:
            not_exit=True
            while not_exit and self.shared_dict["stateExternalServer"]:
                # print(f"        avem atatea conexiuni : {len(self.listConn)}")
                
                ###
                #
                #   ADAUGA AICI CEVA PENTRU A TRIMITE STATUS
                #
                ###
                
                packet_size = conn.recv(8)
                if not packet_size:
                    break
                if self.shared_dict["stateExternalServer"]==False:
                    continue
                    
                
                packet_size = struct.unpack("!Q", packet_size)[0]
                #trebuie modificat sa poata sa acepte chestii mai mari

                packet = conn.recv(packet_size)
                packet = pickle.loads(packet)
                

                response_to_send_back="recieved"
                data_to_send_back="recieved"

                if packet.command == "test":
                    data_to_send_back = "Test received"

                elif packet.command == "statusUpdate":
                    data_to_send_back = self.shared_dict["statusExternalServer"]
                    response_to_send_back="statusUpdate"
                    pass

                elif packet.command == "connection":
                    print(f"Received data (size:{packet_size}): {packet.data}")
                    data_to_send_back = "Connection received"
                
                elif packet.command == "saveDataFunction":
                    #aici primesti pachetul ala complex
                    #il trimiti in functia aia 
                    print(f"===saveDataFunction {addr}===")
                    self.recieve_data_from_client(packet.data)
                    #functia trebuie sa returneze un raspuns
                    #se oaseaza la send back 
                    pass
                
                elif packet.command == "exit":
                    print(f"Received data (size:{packet_size}): {packet.data}")
                    print("closing connection ...")
                    not_exit=False
                    # raise Exception("exit")

                elif packet.command == "sendData":
                    print(f"Received data {addr} (size:{packet_size}): {packet.data}")
                    # self.recieve_data_from_client(conn,packet)
                    pass

                elif packet.command == "statusServer":
                    data_to_send_back = self.shared_dict["statusExternalServer"]
                    response_to_send_back="statusServer"

                elif packet.command == "loadInterval":
                    data_to_send_back = self.send_interval_to_client(addr)
                    pass

                elif packet.command == "sendFunction":
                    #TREBUIE SA ADAUGI CUMVA SA ASTEPTI DIN PIPE SAU CEVA
                    
                    data_to_send_back = self.shared_dict["function_source"]

                    pass
                
                # print(f"---==={addr} a apelat functia {packet.command} cu parametrii {packet.data}===---")
                # # Process function_source
                # # ...
                response_packet=Packet(response_to_send_back,data_to_send_back)
                response_packet=pickle.dumps(response_packet)
                conn.send(struct.pack("!Q", len(response_packet)))
                conn.send(response_packet)


        except Exception as e:
                print(f"Error: {e}")
        # finally:
                # find_conn=self.find_connection_by_address(conn)
                # self.remove_conn_in_list(conn)
                # if find_conn:
                #     self.listConn.remove(find_conn)
        conn.close()
        print(f"Connection from {addr} closed")
    
    def handle_connection(self, conn, addr, child_conn):   
        try:
            while True and self.shared_dict["stateExternalServer"]:
                print(f"        avem atatea conexiuni : {len(self.listConn)}")
                packet_size = conn.recv(8)
                if not packet_size:
                    break
                if self.shared_dict["stateExternalServer"]==False:
                    continue
                packet_size = struct.unpack("!Q", packet_size)[0]
                packet = conn.recv(packet_size)
                packet = pickle.loads(packet)

                if packet.command == "test":
                    print(f"Received data (size:{packet_size}): {packet.data}")
                    ret = "Client , am primit mesajul tau"
                    p = Packet("test", f"mesajul tau a fost primit random {randint(0,100)}")
                    p = pickle.dumps(p)
                    conn.send(struct.pack("!Q", len(p)))
                    conn.send(p)

                if packet.command == "exit":
                    print(f"Received data (size:{packet_size}): {packet.data}")
                    print("closing connection ...")
                    # raise Exception("exit")
                # # Process function_source
                # # ...
        except Exception as e:
                print(f"Error: {e}")
        # finally:
                # find_conn=self.find_connection_by_address(conn)
                # self.remove_conn_in_list(conn)
                # if find_conn:
                #     self.listConn.remove(find_conn)
        conn.close()
        print(f"Connection from {addr} closed")
            
    def stop_external_server(self):

        self.shared_dict["stateExternalServer"]=False
        self.Semaphore_from_Intern_Server=False
        
        for c in self.ConnectionList:
            c.conn.close()
        self.listConn.clear()
        self.ext_server_socket.close()
        print("external server stopped")
        pass
    
    def stop_internal_server(self):
        self.Semaphore_FOR_Intern_Server=False
        self.int_server_socket.close()
        print("internal server stopped")
        pass

    def external_server(self):
        self.ext_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ext_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ext_server_socket.bind((self.host, self.port))
        self.ext_server_socket.listen()
        print(f"External server listening on {self.host}:{self.port}")

        while self.Semaphore_from_Intern_Server:
            conn, addr = self.ext_server_socket.accept()

            if self.Semaphore_from_Intern_Server==False:
                break #this is for the case when the server is stopped
            parent_conn, child_conn = mp.Pipe()

            self.shared_dict["listConn"].append(Com(conn, addr, parent_conn))
            self.listConn.append(Com(conn, addr, parent_conn))


            self.ConnectionList.append(Com(conn, addr, parent_conn,0,1))
            
            print(f"len listConn is : {len(self.ConnectionList)}")
            print(f"[ext] Connection from {addr}")
            p = mp.Process(target=self.H_handle_connection, args=(conn, addr, child_conn))
            p.start()
            print(f"Process {p.pid} started")
    
    def internal_server(self):
        self.int_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.int_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.int_server_socket.bind(("127.0.0.1", 18003))
        self.int_server_socket.listen()
        print(f"Internal server listening on 127.0.0.1:18003")

        try:
            while True and self.Semaphore_FOR_Intern_Server:
                conn, addr = self.int_server_socket.accept()
                print(f"[int] Connection from {addr}")
                still_connected = True
                while still_connected :
                    try:
                        #recieve data
                        data_to_send_back="recieved"
                        packet_size = conn.recv(8)
                        if not packet_size:
                            break
                        packet_size = struct.unpack("!Q", packet_size)[0]
                        
                        data = conn.recv(packet_size)
                        data = pickle.loads(data)
                        print(f"[int]->Received data (size:{packet_size}): {data.data}")
                        #decisions
                        if data.command == "exit":
                            print(f"disconnecting {addr}")
                            data_to_send_back = "Closing connection"
                            still_connected = False
                        
                        elif data.command == "test":
                            data_to_send_back = "Test received"
                            print(f"Received data (size:{packet_size}): {data.data}")
                        
                        elif data.command  == "list":
                            data_to_send_back=f"List of connections ({len(self.listConn)}):"
                            for c in self.ConnectionList:
                                data_to_send_back+=f"\n    {c.addr}"
                        
                        elif data.command == "stopExsv":
                            print("Stopping external server")
                            self.stop_external_server()
                            data_to_send_back="Stopping external server"
                        
                        elif data.command == "stopInsv":
                            print("Stopping internal server")
                            self.stop_external_server()
                            self.stop_internal_server()
                            data_to_send_back="Stopping internal and external server"
                        
                        elif data.command == "sendFunction":
                            self.shared_dict["function_source"]=data.data
                            data_to_send_back="Function received"
                            pass

                        elif data.command == "sendInterval":
                            try:
                                for i in data.data:
                                    self.Interval.append(i)
                            except Exception as e:
                                print(f"Error: {e}")
                            # self.shared_dict["interval"]=data.data
                            data_to_send_back="Interval received"
                            print("Interval received are :")
                            print(self.Interval)

                        elif data.command == "startFunction":
                            temp=self.shared_dict["statusExternalServer"].copy()
                            temp["counterStartServer"]+=1
                            temp["state"]="startFunction"
                            self.shared_dict["statusExternalServer"]=temp
                            
                            print("Starting function")
                            data_to_send_back="Starting function"
                            #here i need to add function to start all clients
                            pass
                        
                        elif data.command == "updateStatus":
                            temp=self.shared_dict["statusExternalServer"].copy()
                            temp["state"]=f"{data.data}"
                            self.shared_dict["statusExternalServer"]=temp

                            # time.sleep(0.3)
                            print("===update Status server ===")
                            print(self.shared_dict["statusExternalServer"])
                            print(f"data for status recieve is : {data.data}")
                            data_to_send_back="Status updated"
                        else:
                            data_to_send_back="Unknown command"
                        
                        #response
                        packet=Packet("response",data_to_send_back)
                        packet=pickle.dumps(packet)
                        conn.send(struct.pack("!Q", len(packet)))
                        conn.send(packet)

                        if self.Semaphore_from_Intern_Server==False and self.Semaphore_FOR_Intern_Server==False: 
                            raise Exception("exit")

                    except Exception as e:
                        print(f"Error: {e}")
                        data_to_send_back = f"Error: {e}"
                        still_connected = False
                        break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()

    def startServer(self):
        self.thread_extern_server  = th.Thread(target=self.external_server)
        self.thread_intern_server = th.Thread(target=self.internal_server)
        
        self.thread_intern_server.start()
        self.thread_extern_server.start()

        
        # while True:
        #     if False:
        #         self.thread_intern_server.join()
        #         self.thread_extern_server.join()
        #     pass
if __name__ == "__main__":
    Sv = Server('0.0.0.0', 18001)
    Sv.startServer()