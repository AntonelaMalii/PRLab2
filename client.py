import socket
import threading
import ftplib
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import filedialog


HOST = '127.0.0.1'
PORT = 9090
HOSTNAME = "ftp.dlptest.com"
USERNAME = "dlpuser"
PASSWORD = "rNrKYTX9g7z3RgJRmxWuGHbeu"


class Client:

    def __init__(self, host, port, hostname, user, password):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        # connect FTP server
        self.ftp_server = ftplib.FTP(hostname, user, password)
        self.ftp_server.encoding = "utf-8"
        msg = tkinter.Tk()
        msg.withdraw()
        self.nickname = simpledialog.askstring("Nickname", "Choose a nickname", parent=msg)
        self.gui_done = False
        self.running = True
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        self.gui_loop()


    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.title('Chat')
        self.win.configure(bg='#856ff8')

        self.chat_label = tkinter.Label(self.win, text = "Chat", bg='#856ff8')
        self.chat_label.config(font=("Times New Roman", 16))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx = 20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text = "Message", bg="lightgray")
        self.msg_label.config(font=("Times New Roman", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)
        
        self.send_button = tkinter.Button(self.win, text="Send Message", command=self.write)
        self.send_button.config(font=("Times New Roman", 12))
        self.send_button.pack(padx=20, pady=5)
    
        self.file_button = tkinter.Button(self.win, text = "Send File", command=self.upload_file)
        self.file_button.config(font=("Times New Roman", 12))
        self.file_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WH_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def send_message(self, message):
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.send_message(message)

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.sock.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        print(message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disable')
            except ConnectionAbortedError:
                break
            except:
                self.sock.close()
                break
    
    def upload_file(self):
        filename = filedialog.askopenfilename().replace('/', "\\")
    
        # read file in binary mode
        with open(filename, "rb") as file:
            self.ftp_server.storbinary(f"STOR {filename}", file)
        self.send_message(f"{self.nickname} sent file: {file} " )

        with open(filename, "wb") as file:
            # command for downloading the file
            self.ftp_server.retrbinary(f"RETR {filename}", file.write)
    

client = Client(HOST, PORT, HOSTNAME, USERNAME, PASSWORD)