# Import required modules
import socket 
import hashlib
import json
import sys
import config

def optionCheck():
    global args 

    availOptions = ["-pkt"]

    options = [opt for opt in sys.argv[1:] if opt.startswith("-")]

    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    for i in options:
        if i not in availOptions:
            raise SystemExit(f"Usage: {sys.argv[0]} -pkt <argument>...")

    if len(options) != 1 or len(args) != 1:
        raise SystemExit(f"Usage: {sys.argv[0]} -pkt <argument>...")

def readJson(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    optionCheck()
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((config.RPHOST,config.RPPORT))

    sendMsg = readJson(args[0])

    print("Sending message", sendMsg["payload"],  "through reverse proxy running on port", config.RPPORT)

    clientSocket.send(json.dumps(sendMsg).encode())
    recvMsg = clientSocket.recv(2048).decode()
    recvMsg = json.loads(recvMsg)
    hashedSent = hashlib.sha1(sendMsg["payload"].encode()).hexdigest()

    print ("Receiving a response from the server payload:", recvMsg["payload"])

    if hashedSent == recvMsg["payload"]:
        print ("Hash of payload is correct")
    else:
        print ("Hash of payload is not correct")