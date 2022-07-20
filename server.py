import socket
import json
from threading import Thread

SERVER_HOST = "0.0.0.0"
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
    while True:
        try:
            msg = cs.recv(1024).decode()
            print(f"{msg} from {client_sockets[cs]}")
        except Exception as e:
            print(f"[!] Error: {e}")
            del client_sockets[cs]
        else:
            msg = msg.replace(seperator_token, ": ")
        
        for socket in client_sockets:
            if socket != cs:
                socket.send(msg.encode())




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