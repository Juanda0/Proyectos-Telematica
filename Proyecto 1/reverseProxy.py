
from datetime import date, datetime
import json
import socket
import _thread
import threading
import config
from utils import log
printLock = threading.Lock()
servers = []
pos = 0

def availableServer(msg):
    global servers
    servers.append([msg["id"],msg["ip_addr"],msg["listenport"]])

def roundRobin():
    global servers
    global pos
    host = servers[pos]
    pos += 1
    if pos >= len(servers):
        pos = 0
    return host

# Establish connection with new client
def newClient(clientsocket,addr):
    while True:
        msg = clientsocket.recv(2048)
        if not msg:
            printLock.release()
            break
        
        jsonMsg = json.loads(msg.decode())
        if jsonMsg["type"] == "1":
            ip, port = clientsocket.getpeername()
            jsonMsg["ip_addr"] = ip
            t = f"Received setup message from server id {jsonMsg['id']} ip {jsonMsg['ip_addr']} port {jsonMsg['listenport']} \n"
            log(t,file)
            
            availableServer(jsonMsg)
        elif jsonMsg["type"] == "0":
            t = f"Received a message from client {jsonMsg['srcid']} payload {jsonMsg['payload']}\n"
            log(t,file)
            
            
            targetHost = roundRobin()
            serverName = targetHost[1]
            serverPort = int(targetHost[2])

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((serverName,serverPort))

            t = f"Forwarding a data message to server id {targetHost[0]} server ip  {serverName} port {serverPort} payload {jsonMsg['payload']} \n"
            log(t,file)
            
            server_socket.send(json.dumps(jsonMsg).encode())
            recvMsg = server_socket.recv(2048)
            recvMsg = json.loads(recvMsg.decode())
            t = f"Received a data message from server id {recvMsg['srcid']} payload {recvMsg['payload']} \n"
            log(t,file)
            
            server_socket.close()

            clientsocket.send(json.dumps(recvMsg).encode())
        else:
            pass
    clientsocket.close()

if __name__ == "__main__":
    global file
    file = f"logs/RP-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}"

    s = socket.socket()
    t = f"Running the reverse proxy on port {config.RPPORT}\n"
    log(t,file)
    

    s.bind((config.RPHOST, config.RPPORT))     
    s.listen(100)

    while True:
        c, addr = s.accept()
        printLock.acquire()
        _thread.start_new_thread(newClient,(c,addr))
    s.close()