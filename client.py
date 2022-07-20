import socket
import threading
# import binascii
# from ctypes import c_uint32
import pyDH
import time

username = input()

Sk = pyDH.DiffieHellman()
Pk = Sk.gen_public_key()

socketObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketObject.connect(("localhost", 1234))
print("Connected to localhost")

socketObject.send(username.encode())
time.sleep(0.2)
socketObject.send(Pk.to_bytes(256, "big"))

def reciever():
    while True:
        try:
            msg = socketObject.recv(1024).decode()
            print(msg)
        except socket.error as e:
            print("Error", e)
            break

t = threading.Thread(target=reciever)
t.daemon = True
t.start()

while True:
    str_to_send = input()
    # str_to_send_encoded = bytes(str_to_send,'utf-8')
    socketObject.send(str_to_send.encode())
    # print("sent")

socketObject.close()