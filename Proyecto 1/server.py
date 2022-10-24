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
# after receiving each connection from reverse proxy/client
def newClient(clientsocket,addr):
    while True:
        msg = clientsocket.recv(2048)
        if not msg:
            print_lock.release()
            break

        jsonMsg = json.loads(msg.decode())
        
        t = f"Received a message from client {jsonMsg['srcid']} payload {jsonMsg['payload']}"
        log(t,file)

        payload = jsonMsg["payload"]
        newMsg = hashlib.sha1()
        newMsg.update(payload.encode())
        hashedPayload = newMsg.hexdigest()
        newJsonMsg = {"type":"2", "srcid": config.ID, "destid": jsonMsg["srcid"],"payloadsize": len(hashedPayload), "payload": hashedPayload}
        
        t = f"Sending a message to the client {newJsonMsg['destid']} payload {newJsonMsg['payload']}"
        log(t,file)

        clientsocket.send(json.dumps(newJsonMsg).encode())
    clientsocket.close()


# Connect to the Reverse Proxy
def rpConnection():
    jsonMsg = {"type":"1", "id": config.ID, "listenport": config.PORT}
    rpName = config.RPHOST
    rpPort = config.RPPORT

    rpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rpSocket.connect((rpName, rpPort))

    rpSocket.send(json.dumps(jsonMsg).encode())
    rpSocket.close()

if __name__ == "__main__":
    s = socket.socket()
    global file
    file = f"logs/S-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}"
    


    

    t = f"Server running with id {config.ID}\n"
    log(t,file)

    t = f"Listening on port {config.PORT}\n"
    log(t,file)

    rpConnection()
    t = f"Connecting to the reverse proxy on port {config.RPPORT}\n"
    log(t,file)

    s.bind((config.HOST, config.PORT))     
    s.listen(10)                 

    while True:
        c, addr = s.accept()
        print_lock.acquire()
        t = f"Received a message from client {addr} payload\n"
        log(t,file)
        _thread.start_new_thread(newClient,(c,addr))
        
    s.close()