import socket
import threading
import ftplib
import tkinter
import smtplib
import email
import imaplib
import tkinter.scrolledtext
from tkinter import StringVar, Toplevel, simpledialog
from tkinter import filedialog

HOST = '127.0.0.1'
PORT = 9090
HOSTNAME = "ftp.dlptest.com"
USERNAME = "dlpuser"
PASSWORD = "rNrKYTX9g7z3RgJRmxWuGHbeu"

# ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)

class Client:

    def __init__(self, host, port, hostname, user, password):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        # connect FTP server
        self.ftp_server = ftplib.FTP(hostname, user, password)
        self.ftp_server.encoding = "utf-8"
        self.arr = []

        self.msg = tkinter.Tk()
        self.msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Choose a nickname", parent=self.msg)
        self.mail = simpledialog.askstring("Mail", "Please enter your mail", parent=self.msg)
        self.mail_pass = simpledialog.askstring("Mail", "Please enter your mail password", show='*', parent=self.msg)

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

        self.send_button = tkinter.Button(self.win, text = "Send Mail", command=self.send_mail)
        self.send_button.config(font=("Times New Roman", 12))
        self.send_button.pack(padx=20, pady=5)

        self.open_button = tkinter.Button(self.win, text = "Open Mailbox", command=self.open_mail)
        self.open_button.config(font=("Times New Roman", 12))
        self.open_button.pack(padx=20, pady=5)


        self.gui_done = True

        self.win.protocol("WH_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def send_message(self, message):
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

        # SMTP

    def send_mail(self):
        # get the receiver gmail
        receiver = simpledialog.askstring("Receiver", "Please write the receiver's mail", parent=self.msg)
        # get the message
        message = simpledialog.askstring("Message", "Please write your mail here", parent=self.msg)
        # connect to the server address with port 587
        server = smtplib.SMTP('smtp.gmail.com', 587)
        # start the connection
        server.starttls()
        # login into the server
        server.login(self.mail, self.mail_pass)
        mesaj = self.nickname + ' logged in successful into the mail ' + self.mail
        print(mesaj)
        # send the email
        server.sendmail(self.mail, receiver, message)
        msg1 = '\n' + self.nickname + ' sent an email to ' + receiver + '\n'
        self.send_message(msg1)

        # IMAP

    def open_mail(self):
        # create a new window over the main one (self.msg)
        new_window = Toplevel(self.msg)
        new_window.title("Your Mailbox")
        new_window.geometry("400x400")
        T = tkinter.scrolledtext.ScrolledText(new_window, width=120, height=100)
        T.pack()

        # open our connection to gmail
        # IMAP4_SSL is a subclass derived from IMAP4 that connects over an SSL encrypted socket
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        # login
        mail.login(self.mail, self.mail_pass)
        mesaj = self.nickname + ' logged in successful into the mail ' + self.mail
        print(mesaj)
        # choose the "inbox"
        mail.select('inbox')

        _, data = mail.uid('search', None, "ALL")
        # split the byte string list with mails' ids
        inbox_item_list = data[0].split()
        for item in inbox_item_list:
            _, email_data = mail.uid('fetch', item, '(RFC822)')
            # decode the mail
            raw_email = email_data[0][1].decode('utf-8')
            # get the message
            email_message = email.message_from_string(raw_email)

            # to_ = email_message['To']
            from_ = email_message['From']
            subject_ = email_message['Subject']
            t_msg = '\nMail ' + str(item.decode('utf-8')) + ':\nFrom: ' + str(from_) + '\nSubject: ' + str(
                subject_) + '\n'

            counter = 1
            # go through email message
            for part in email_message.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                filename = part.get_filename()
                if not filename:
                    ext = '.html'
                    filename = 'msg-part-%08d%s' % (counter, ext)
                counter += 1  # in case of multiple parts

                # save file
                content_type = part.get_content_type()
                print('Subject: ', subject_)
                print('Content type:', content_type)
                if "plain" in content_type:
                    print('Message: ', part.get_payload())
                    t_msg += 'Content: ' + str(part.get_payload())
                else:
                    print(content_type)
            T.insert(tkinter.INSERT, t_msg)

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
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                self.sock.close()
                break

    def upload_file(self):
        filename = filedialog.askopenfilename().replace('/', "\\")
        name_file = filename.split('\\')[-1]

        # read file in binary mode
        with open(filename, "rb") as file:
            self.ftp_server.storbinary(f"STOR {name_file}", file)
        self.send_message(f"{self.nickname} sent file: {name_file} ")

        with open(filename, "wb") as file:
            # command for downloading the file
            self.ftp_server.retrbinary(f"RETR {name_file}", file.write)

        # file = open(filename, "r")
        # self.send_message(f"\nFile Content: {file.read()}")
        # print('File Content: ', file.read())

        # close the connection
        # self.ftp_server.quit()


client = Client(HOST, PORT, HOSTNAME, USERNAME, PASSWORD)