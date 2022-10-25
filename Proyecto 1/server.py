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
# after receiving each connection from reverse proxy/client
def newClient(clientsocket,addr):
    global ID
    while True:
        msg = clientsocket.recv(2048)
        if not msg:
            print_lock.release()
            break

        t = f"Sending a message to the client"
        log(t,file)
        res = """HTTP/1.1 200 OK
                Content-Type: text/html

                <html><body>PONG - Server ID:"""+str(ID)+"""</body></html>
            """
        clientsocket.send(bytes(res, 'utf-8'))
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