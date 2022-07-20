import tkinter as tk
from tkinter import simpledialog
import tkinter.scrolledtext as scrolledtext
import socket
import threading
import sys

class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        msg = tk.Tk()
        msg.withdraw()

        user_flag = False
        while not user_flag:
            self.username = simpledialog.askstring('Username', 'Please enter a username', parent = msg)
            if self.username != '':
                user_flag = True

        self.active = True
        self.gui_flag = False

        receive_thread = threading.Thread(target = self.receive)
        gui_thread = threading.Thread(target = self.gui_loop)

        receive_thread.start()
        gui_thread.start()

    def write(self):
        msg = f'<{self.username}> {self.input.get("1.0", "end")}'.strip()
        self.sock.send(msg.encode())
        self.input.delete("1.0", "end")
        self.chat.config(state = 'normal')
        self.chat.insert('end', f'{msg}\n')
        self.chat.config(state = 'disabled')

    def gui_loop(self):
        self.win = tk.Tk()
        self.win.bind('<Return>', lambda event: self.write())
        self.win['bg'] = '#FFF'

        # self.send = tk.Button(self.win, text='Send', bg='#8B8C8F', fg='#00FF00', command=self.write())
        # self.send.pack(padx=20, pady=5)

        self.chat = scrolledtext.ScrolledText(self.win, bg = '#8B8C8F', fg = '#000')
        self.chat.config(state = 'disabled')
        self.chat.pack(padx = 20, pady = 5)

        self.input = tk.Text(self.win, width = 80, height = 1, bg = '#8B8C8F', fg = '#000')
        self.input.pack(padx = 20, pady = 5)
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
                        self.chat.config(state = 'normal')
                        self.chat.insert('end', f'{msg}\n')
                        self.chat.config(state = 'disabled')
            except:
                self.sock.close()
                raise Exception('An error has occured.')
        msg = tk.Tk()
        self.winmainloop()
        msg.withdraw()


client = Client("172.16.48.191", 1234)
