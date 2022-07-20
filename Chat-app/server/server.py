import socket
import json
from threading import Thread
import time

SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 1234
seperator_token = "<SEP>"

with open("data\keys.json") as f:
    keys = json.load(f)

client_sockets = {}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((SERVER_HOST, SERVER_PORT))
s.listen()
print(f"[*] Listen as {SERVER_HOST}:{SERVER_PORT}")

def broadcast(msg):
    for client_socket in client_sockets:
        client_socket.send(msg.encode())
        # print("sending message")

def listen(cs):
    person = False
    while not person:
        contact_name = cs.recv(1024).decode()
        if contact_name in keys.keys():
            person = True
            cs.send("Valid".encode())
        else:
            cs.send("Invalid".encode())
    time.sleep(0.3)
    cs.send(keys[contact_name].to_bytes(256, "big"))

    while True:
        try:
            data = cs.recv(1024)
            print(f"{data} from {client_sockets[cs]}")

            for socket in client_sockets:
                if socket != cs:
                    socket.send(data)
                    
        
        except Exception as e:
            print(f"[!] Error: {e}")
            del client_sockets[cs]



while True:
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    client_name = client_socket.recv(1024).decode()
    client_sockets[client_socket] = client_name
    key = int.from_bytes(client_socket.recv(1024), "big")
    keys[client_name] = key
    with open('data/keys.json', 'w') as f:
        json.dump(keys,f, indent=2)
    

    t = Thread(target=listen, args=(client_socket,))
    t.daemon = True
    t.start()

for cs in client_sockets:
    cs.close()