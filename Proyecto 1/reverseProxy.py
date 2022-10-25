
from datetime import date, datetime
import json
import socket
import _thread
import threading
import config
from utils import log
printLock = threading.Lock()
availableServers = []
pos = 0

def availableServer():
    for server in config.SERVERS:
        t = f"Connecting to the server with id {server[0]} on port {server[2]}\n"
        log(t,file)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server[1],server[2]))

        jsonMsg = {"type":"1","listenport": config.RPPORT}
        server_socket.send(json.dumps(jsonMsg).encode())
        recvMsg = server_socket.recv(2048)
        recvMsg = json.loads(recvMsg.decode())
        if recvMsg["id"] == server[0]:
            availableServers.append(server)
            t = f"Conneted to the server with id {server[0]} on port {server[2]} succesful\n"
            log(t,file)
        else:
            t = f"Connection to the server with id {server[0]} on port {server[2]} fail\n"
            log(t,file)
        server_socket.close()

def roundRobin():
    global availableServer
    global pos
    host = availableServers[pos]
    pos += 1
    if pos >= len(availableServers):
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


    clientsocket.close()

if __name__ == "__main__":
    global file
    file = f"logs/RP-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    t = f"Running the reverse proxy on port {config.RPPORT}\n"
    log(t,file)
    

    s.bind((config.RPHOST, config.RPPORT))     
    s.listen(100)
    availableServer()
    while True:
        c, addr = s.accept()
        printLock.acquire()
        _thread.start_new_thread(newClient,(c,addr))
    s.close()