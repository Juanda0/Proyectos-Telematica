import socket
import _thread
import threading
import hashlib
import json
import sys
import config
from utils import log
from datetime import date, datetime

print_lock = threading.Lock()
# Connect to the Reverse Proxy
def rpConnection(rpSocket):
    global ID,PORT
    jsonMsg = {"type":"1", "id": ID, "listenport": PORT}
    t = f"Connetion with reverse proxy\n"
    log(t,file)
    
    rpSocket.send(json.dumps(jsonMsg).encode())

# after receiving each connection from reverse proxy/client
def newClient(clientsocket,addr):
    global ID
    while True:
        msg = clientsocket.recv(2048)
        if not msg:
            print_lock.release()
            break

        jsonMsg = json.loads(msg.decode())
        if jsonMsg["type"] == "1":
            rpConnection(clientsocket)
        else:
            t = f"Received a message from client {jsonMsg['srcid']} payload {jsonMsg['payload']}"
            log(t,file)

            payload = jsonMsg["payload"]
            newMsg = hashlib.sha1()
            newMsg.update(payload.encode())
            hashedPayload = newMsg.hexdigest()
            newJsonMsg = {"type":"2", "srcid": ID, "destid": jsonMsg["srcid"],"payloadsize": len(hashedPayload), "payload": hashedPayload}
            
            t = f"Sending a message to the client {newJsonMsg['destid']} payload {newJsonMsg['payload']}"
            log(t,file)

            clientsocket.send(json.dumps(newJsonMsg).encode())
    clientsocket.close()

if __name__ == "__main__":
    s = socket.socket()
    global file,ID,HOST,PORT
    file = f"logs/S-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}"

    ID = config.SERVERS[2][0]
    HOST = config.SERVERS[2][1]
    PORT = config.SERVERS[2][2]
    
    t = f"Server running with id {ID}\n"
    log(t,file)

    t = f"Listening on port {PORT}\n"
    log(t,file)

    # rpConnection()
    # t = f"Connecting to the reverse proxy on port {config.RPPORT}\n"
    # log(t,file)

    s.bind((HOST, PORT))     
    s.listen(10)                 

    while True:
        c, addr = s.accept()
        print_lock.acquire()
        t = f"Received a message from client {addr} payload\n"
        log(t,file)
        _thread.start_new_thread(newClient,(c,addr))
        
    s.close()