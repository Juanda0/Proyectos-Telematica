
from datetime import datetime
import json
import socket
import _thread
import threading
import config
from utils import log
printLock = threading.Lock()
pos = 0

def roundRobin():
    global pos
    host = config.SERVERS[pos]
    pos += 1
    if pos >= len(config.SERVERS):
        pos = 0
    return host

# Establish connection with new client
def newClient(clientsocket,addr):
    while True:
        msg = clientsocket.recv(2048)
        msgD = msg.decode()
        log(msgD,file)
        with open("cache.json", 'r') as f:
            cache = json.load(f)
        if not msg:
            printLock.release()
            break  

        #Caching strategy
        if msgD in cache.keys():
            #Calculates diference between saved datetime and current time in seconds, and then sustracts the parameter TTL
            TTLLeft = config.TTL - (datetime.now() - datetime.strptime(cache[msgD]["TTL"], '%d-%m-%Y-%H-%M-%S')).total_seconds() 
            if TTLLeft > 0:
                t = f"Forwarding data message from cache. Resource's TTL left: {TTLLeft} \n"
                log(t,file)
                response = cache[msgD]["response"]
                log(response,file)
                clientsocket.send(response.encode())
                continue
        
        
        t = f"Received a message from client {addr}\n"
        log(t,file)
            
        targetHost = roundRobin()
        serverName = targetHost[1]
        serverPort = int(targetHost[2])

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((serverName,serverPort))

        t = f"Forwarding a data message to server id {targetHost[0]} server ip  {serverName} port {serverPort} \n"
        log(t,file)
            
        server_socket.send(msg)
        recvMsg = server_socket.recv(2048)

        t = f"Received a data message from server id {targetHost[0]}\n"
        log(t,file)

        #save the cache
        cache[msgD] = {"response":recvMsg.decode(),"TTL":datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}
        log(recvMsg.decode(),file)
        with open("cache.json", 'w') as f:
            json.dump(cache, f)
        
        server_socket.close()
        
        clientsocket.send(recvMsg)


    clientsocket.close()

if __name__ == "__main__":
    global file
    file = f"logs/RP-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    t = f"Running the reverse proxy on port {config.RPPORT}\n"
    log(t,file)
    

    s.bind((config.RPHOST, config.RPPORT))     
    s.listen(100)
    try:
        while True:
            c, addr = s.accept()
            printLock.acquire()
            _thread.start_new_thread(newClient,(c,addr))
    except KeyboardInterrupt:
        s.close()