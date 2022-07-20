import tkinter as tk
from tkinter import simpledialog
import tkinter.scrolledtext as scrolledtext
import socket
import threading
import sys
import pyDH
import time
import json
import base64
import hashlib
import binascii
from Crypto.Cipher import AES

class Client:

    def __init__(self, host, port):
        Sk = ""
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

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        msg = tk.Tk()
        msg.withdraw()

        user_flag = False

        while not user_flag:
            self.username = simpledialog.askstring('Username', 'Please enter a username', parent=msg)

            if self.username != '':
                user_flag = True

        self.active = True
        self.gui_flag = False

        receive_thread = threading.Thread(target=self.receive)
        gui_thread = threading.Thread(target=self.gui_loop)

        receive_thread.start()
        gui_thread.start()
        self.validRecieved = False
        while self.validRecieved == False:
            self.conversation = input("Who do you want to talk to? ")
            self.sock.send(self.conversation.encode())
            time.sleep(0.2)
            self.response = self.sock.recv(1024).decode()
            if self.response == "Valid":
                self.validRecieved = True
                print("Valid")
                with open("keys\keys.json") as f:
                    self.keys = json.load(f)
            else:
                print("Invalid response from server")

        self.partnerPublicKey =  int.from_bytes(self.sock.recv(1024), "big")
        self.sharedKey = Sk.gen_shared_key(self.partnerPublicKey)
        self.keys[self.conversation] = self.sharedKey
        with open('keys/keys.json', 'w') as f:
            json.dump(self.keys,f, indent=2)
        print(f"{self.conversation}'s shared key is: {self.sharedKey}") 
        self.cipher = AES.new(binascii.unhexlify(self.sharedKey), AES.MODE_EAX)

    def receive(self):
        self.data = self.sock.recv(1024)
        self.nonce = self.data[:16]
        self.tag = self.data[16:32]
        self.ciphertext = self.data[32:]
        self.cipher = AES.new(binascii.unhexlify(self.sharedKey), AES.MODE_EAX, nonce=self.nonce)
        self.plaintext = self.cipher.decrypt(self.ciphertext).decode("utf-8")
        try:
            self.cipher.verify(self.tag)
            print("The message is authentic:", self.plaintext)
            return self.plaintext
        except ValueError:
            print("Key incorrect or message corrupted")

    def write(self):
        msg = f'<{self.username}> {self.input.get("1.0", "end")}'.strip()
        self.sock.send(msg.encode())
        self.input.delete("1.0", "end")
        self.chat.config(state='normal')
        self.chat.insert('end', f'{msg}\n')
        self.chat.config(state='disabled')

    def gui_loop(self):
        self.win = tk.Tk()
        self.win.bind('<Return>', lambda event: self.write())
        self.win['bg'] = '#030526'

        # self.send = tk.Button(self.win, text='Send', bg='#8B8C8F', fg='#00FF00', command=self.write())

        # self.send.pack(padx=20, pady=5)

        self.chat = scrolledtext.ScrolledText(self.win, bg='#272840', fg='#F2F2F2')
        self.chat.config(state='disabled')

        self.chat.pack(padx=20, pady=5)
        self.input = tk.Text(self.win, width=80, height=1, bg='#272840', fg='#F2F2F2')

        self.input.pack(padx=20, pady=5)
        self.gui_flag = True
        self.win.mainloop()

    def stop(self):
        self.active = False
        self.sock.close()
        self.win.destroy()
        sys.exit()

    def receive(self):
        while self.active:
            try:
                msg = self.sock.recv(1024).decode('utf-8')
                if msg == 'USER':
                    self.sock.send(self.username.encode('utf-8'))
                else:
                    if self.gui_flag:
                        self.chat.config(state='normal')
                        self.chat.insert('end', f'{msg}\n')
                        self.chat.config(state='disabled')
            except:
                self.sock.close()
                raise Exception('An error has occured.')

        msg = tk.Tk()
        self.winmainloop()
        msg.withdraw()


client = Client("172.16.48.191", 1234)
