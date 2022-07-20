import socket
import threading
import pyDH
import time
import json
import base64
import hashlib
import binascii
from Crypto.Cipher import AES
# from Crypto import Random
username = input()

Sk = ""
# BLOCK_SIZE = 16
# pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
# unpad = lambda s: s[:-ord(s[len(s) - 1:])]


with open('keys\key.txt') as f:
    try:
        Sk = pyDH.DiffieHellman(Sk=int(f.read()))
    except:
        pass



if Sk == "":
    Sk = pyDH.DiffieHellman() 
    print(Sk.get_private_key())
    with open('keys\key.txt', 'w') as f:
        f.write(str(Sk.get_private_key()))


Pk = Sk.gen_public_key()


socketObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketObject.connect(("172.16.48.191", 1234))
print("Connected to localhost")

socketObject.send(username.encode())
time.sleep(0.2)
socketObject.send(Pk.to_bytes(256, "big"))

validRecieved = False

while validRecieved == False:
    conversation = input("Who do you want to talk to? ")
    socketObject.send(conversation.encode())
    time.sleep(0.2)
    response = socketObject.recv(1024).decode()
    if response == "Valid":
        validRecieved = True
        print("Valid")
        with open("keys\keys.json") as f:
            keys = json.load(f)
    else:
        print("Invalid response from server")

partnerPublicKey =  int.from_bytes(socketObject.recv(1024), "big")
sharedKey = Sk.gen_shared_key(partnerPublicKey)
keys[conversation] = sharedKey
with open('keys/keys.json', 'w') as f:
    json.dump(keys,f, indent=2)
print(f"{conversation}'s shared key is: {sharedKey}") 
cipher = AES.new(binascii.unhexlify(sharedKey), AES.MODE_EAX)

# while conversation not in users:
#     print("Please choose a valid name")
#     conversation = input("Who do you want to talk to? ")
def receive():
    data = socketObject.recv(1024)
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    cipher = AES.new(binascii.unhexlify(sharedKey), AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext).decode("utf-8")
    try:
        cipher.verify(tag)
        print("The message is authentic:", plaintext)
        return plaintext
    except ValueError:
        print("Key incorrect or message corrupted")


def reciever():
    while True:
        try:
            msg = receive()
            print(msg)
        except socket.error as e:
            print("Error", e)
            break

# def encrypt(plain_text, key):
#     private_key = hashlib.sha256(key.encode("utf-8")).digest()
#     plain_text = pad(plain_text)
#     print("After padding:", plain_text)
#     iv = Random.new().read(AES.block_size)
#     cipher = AES.new(private_key, AES.MODE_CBC, iv)
#     return base64.b64encode(iv + cipher.encrypt(plain_text))

# def decrypt(cipher_text, key):
#     private_key = hashlib.sha256(key.encode("utf-8")).digest()
#     cipher_text = base64.b64decode(cipher_text)
#     iv = cipher_text[:16]
#     cipher = AES.new(private_key, AES.MODE_CBC, iv)
#     return unpad(cipher.decrypt(cipher_text[16:]))

t = threading.Thread(target=reciever)
t.daemon = True
t.start()\

while True:
    str_to_send = input()
    nonce = cipher.nonce
    cipher = AES.new(binascii.unhexlify(sharedKey), AES.MODE_EAX, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(str_to_send.encode("utf-8"))   
    socketObject.send(nonce + tag + ciphertext)

socketObject.close()