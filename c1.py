import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import time
import os
from tkinter import filedialog
from tkinter import font
import pickle
import cv2
import struct
from vidstream import ScreenShareClient
import sys
import re
from getmac import get_mac_address

HOST = '192.168.18.178'
PORT = 1235
HOST_ss = socket.gethostname()
host_ip_ss = socket.gethostbyname(HOST_ss)
print(f'{host_ip_ss}')
DISCONNECT_MESSAGE='!DISCONNECT'
SIZE=1024

status = b'0'  
DARK_BLUE = '#192A56'
LIGHT_BLUE = '#3A539B'
WHITE = "white"
FONT = ("Arial", 12)
BUTTON_FONT = ("Arial", 10)
FORMAT = 'utf-8'
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data = b""
payload_size = struct.calcsize("Q")

try:
    client.connect((HOST, PORT))
    print("Successfully connected to server")
except:
    messagebox.showerror("Unable to connect", f"Unable to connect to server {HOST} {PORT}")

def add_message(message):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)


def connect():
    add_message("[SERVER] Successfully connected to the server")
    username = username_textbox.get()
    if username != '':
        client.sendall(username.encode())
    else:
        messagebox.showerror("Invalid username", "Username cannot be empty")

    threading.Thread(target=listen_for_messages_from_server, args=(client,)).start()

    username_textbox.config(state=tk.DISABLED)
    username_button.config(state=tk.DISABLED)


def send_message():
    first = 'chat'
    client.send(first.encode())
    time.sleep(1)

    message = message_textbox_1.get()
    print(f'{message}')

    if message != '':
        client.send(message.encode('utf-8'))
        msg = message_textbox.get()
        if msg != '':
            client.send(msg.encode('utf-8'))

        message_textbox_1.delete(0, len(message))
        message_textbox.delete(0, len(msg))
    else:
        messagebox.showerror("Empty message", "Message cannot be empty")


def send_document():
    first = 'document'
    client.send(first.encode())
    sending_info = message_textbox_1.get()
    message_textbox_1.delete(0, len(sending_info))
    print(f'{sending_info}')
    client.send(sending_info.encode())

    # Modified document sending method
    file_path = filedialog.askopenfilename()
    if file_path:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        header = f"{file_name}|{file_size}".ljust(100).encode('utf-8')
        client.send(header)

        with open(file_path, "rb") as file:
            while True:
                file_data = file.read(1024)
                if not file_data:
                    break
                client.send(file_data)


def function_send_frames():
    global status
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Camera', frame)

        data = pickle.dumps((status, frame))
        frame_size = struct.pack("L", len(data))

        try:
            client.send(frame_size)
            client.send(data)
        except:
            cap.release()
            cv2.destroyAllWindows()
            break

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            status = b'1'
            last_frame_data = pickle.dumps((status, frame))
            client.send(struct.pack("L", len(last_frame_data)))
            client.send(last_frame_data)
            print("Streaming stopped")
            break

    cap.release()
    cv2.destroyAllWindows()


def send_video():
    first = 'video'
    client.send(first.encode('utf-8'))
    function_send_frames()


def s_sharing():
    first = 'screen-sharing'
    client.send(first.encode())
    message = str(host_ip_ss)
    client.send(message.encode('utf-8'))
    time.sleep(5)
    IP = host_ip_ss
    PORT = 9999

    server = ScreenShareClient(IP, PORT)
    t = threading.Thread(target=server.start_stream)
    t.start()


def send_message_all():
    first = 'chat'
    client.sendall(first.encode())
    second = 'all'
    client.sendall(second.encode())
    time.sleep(1)
    message = message_textbox.get()
    if message==DISCONNECT_MESSAGE:
        client.close()
    elif message != '':
        client.sendall(message.encode())
        message_textbox.delete(0, len(message))
    else:
        messagebox.showerror("Empty message", "Message cannot be empty")


root = tk.Tk()
root.geometry("850x600")
root.title("Chat and File Transfer Client")
root.resizable(False, False)
custom_font = font.Font(family="Arial", size=16)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=2)
root.grid_rowconfigure(2, weight=2)
root.grid_rowconfigure(3, weight=1)

top_frame = tk.Frame(root, width=700, height=100, bg=DARK_BLUE)
top_frame.grid(row=0, column=0, sticky=tk.NSEW)

middle_frame = tk.Frame(root, width=700, height=200, bg=LIGHT_BLUE)
middle_frame.grid(row=1, column=0, sticky=tk.NSEW)

bottom_frame = tk.Frame(root, width=700, height=200, bg=DARK_BLUE)
bottom_frame.grid(row=2, column=0, sticky=tk.NSEW)

bottom_frame_1 = tk.Frame(root, width=700, height=100, bg=DARK_BLUE)
bottom_frame_1.grid(row=3, column=0, sticky=tk.NSEW)

username_label = tk.Label(top_frame, text="Enter username:", font=FONT, bg=DARK_BLUE, fg=WHITE)
username_label.pack(side=tk.LEFT)

username_textbox = tk.Entry(top_frame, font=FONT, bg=LIGHT_BLUE, fg=WHITE, width=30)
username_textbox.pack(side=tk.LEFT)

username_button = tk.Button(top_frame, text="Join Server", font=BUTTON_FONT, bg=LIGHT_BLUE, fg=WHITE, command=connect)
username_button.pack(side=tk.LEFT, padx=40)

username_label_1 = tk.Label(bottom_frame_1, text="Message:", font=custom_font, bg=DARK_BLUE, fg=WHITE, width=10, height=2)
username_label_1.pack(side=tk.LEFT)
message_textbox = tk.Entry(bottom_frame_1, font=FONT, bg=LIGHT_BLUE, fg=WHITE, width=20)
message_textbox.pack(side=tk.LEFT, padx=0)

message_textbox_1 = tk.Entry(bottom_frame_1, font=FONT, bg=LIGHT_BLUE, fg=WHITE, width=20)
message_textbox_1.pack(side=tk.LEFT, padx=20)

send_button = tk.Button(bottom_frame, text="Send Message", font=BUTTON_FONT, bg=LIGHT_BLUE, fg=WHITE, command=send_message)
send_button.pack(side=tk.LEFT, padx=15)

send_all_button = tk.Button(bottom_frame, text="Send to All", font=BUTTON_FONT, bg=LIGHT_BLUE, fg=WHITE,
                            command=send_message_all)
send_all_button.pack(side=tk.LEFT, padx=15)

document_button = tk.Button(bottom_frame, text="Send Document", font=BUTTON_FONT, bg=LIGHT_BLUE, fg=WHITE,
                            command=send_document)
document_button.pack(side=tk.LEFT, padx=15)

video_button = tk.Button(bottom_frame, text="Send Video", font=BUTTON_FONT, bg=LIGHT_BLUE, fg=WHITE, command=send_video)
video_button.pack(side=tk.LEFT, padx=15)

screen_sharing = tk.Button(bottom_frame, text="Start Screen Sharing", font=BUTTON_FONT, bg=LIGHT_BLUE, fg=WHITE,
                        command=s_sharing)
screen_sharing.pack(side=tk.LEFT, padx=30)

message_box = scrolledtext.ScrolledText(middle_frame, font=FONT, bg=LIGHT_BLUE, fg=WHITE, width=80, height=10)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.TOP)


def listen_for_messages_from_server(client):
    while 1:
        try:
            m = client.recv(1024).decode('utf-8')
            print(f'{m}')
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError: ", e)
            break
        if m == 'message':
            print('hi-12')
            while 1:
                message = client.recv(2048).decode('utf-8')
                if message != '':
                    username = message.split("~")[0]
                    content = message.split('~')[1]

                    add_message(f"[{username}] {content}")
                    break
                else:
                    messagebox.showerror("Error", "Message received from client is empty")
        elif m == 'document':
            print('\nThis is a document file sent by the server\n')
            header = client.recv(100).decode('utf-8')
            file_name, file_size_str = header.strip().split('|')
            file_size = int(file_size_str)

            file_path = filedialog.asksaveasfilename()

            with open(file_path, "wb") as file:
                bytes_received = 0
                while bytes_received < file_size:
                    file_data = client.recv(1024)
                    if not file_data:
                        break
                    file.write(file_data)
                    bytes_received += len(file_data)
            file.close()
            print("File received and saved successfully.")
        elif m == 'video':
            print('This is a video file sent by the server')
            function_conference()
        elif m == 'screen-sharing':
            print('This is a screen-sharing application')
            message = client.recv(2048).decode('utf-8')
            print(f'{message}')

            IP = message
            PORT = 9999
            time.sleep(10)
            sender = ScreenShareClient(IP, PORT)

            t = threading.Thread(target=sender.start_stream)
            t.start()

            try:
                while True:
                    continue
            except KeyboardInterrupt:
                print("Ctrl+C pressed. Stopping the server.")


def function_conference():
    print('The client is listening to the frame')
    data = b""
    payload_size = struct.calcsize("L")
    cv2.namedWindow("Receiving video", cv2.WINDOW_NORMAL)

    while True:
        while len(data) < payload_size:
            packet = client.recv(4 * 1024)

            if not packet:
                break
            data += packet

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]

        try:
            msg_size = struct.unpack("L", packed_msg_size)[0]
        except:
            print("Done!")
            cv2.destroyAllWindows()
            break

        while len(data) < msg_size:
            data += client.recv(4 * 1024)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        status, frame = pickle.loads(frame_data)
        if status == b'1':
            cv2.destroyAllWindows()
            break

        cv2.imshow("Receiving video", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            last_frame_data = pickle.dumps((status, frame))
            client.send(struct.pack("L", len(last_frame_data)))
            client.send(last_frame_data)
            cv2.destroyAllWindows()
            client.send(b'q')
            sys.exit(0)

def disconnect_server(client: socket.socket, recv_from: str):
    global connected
    connected = False
    client.send(pickle.dumps(DISCONNECT_MESSAGE))
    if recv_from == "client":
        print(f"[DISCONNECTED] Client disconnected from {HOST}:{PORT}")
    elif recv_from == "server":
        print(f"[DISCONNECTED] Server disconnected from Client.")
    client.close()

def recv_msg(client: socket.socket, disconnect_info: str = ""):
    msg = client.recv(SIZE)
    if not msg:
        return ''
    msg = pickle.loads(msg)
    if msg == DISCONNECT_MESSAGE:
        print(disconnect_info)
        disconnect_server(client, "server")
    return msg

def game_entry():
    print('1')
    def register():
        mac_address_pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        match = re.match(mac_address_pattern, mac_entry.get())
        if not match:
            messagebox.showerror("Invalid MAC Address", "Invalid MAC Address")
        else:
            mac = mac_entry.get()
            client.send(pickle.dumps(f"REGISTER/{mac}"))
            msg = recv_msg(client)
            if msg == "OK":
                print(f"Registered MAC Address: {mac}")
                messagebox.showinfo("Registration Successful", f"Registered MAC Address: {mac}")
            else:
                print(f"Registration Failed: {msg}")
                messagebox.showerror("Registration Failed", f"Registration Failed: {msg}")
    
    
    def login():
        mac = mac_entry.get()
        client.send(pickle.dumps(f"LOGIN/{mac}"))
        msg = recv_msg(client)
        if msg == "OK":
            print(f"Logged in with MAC Address: {mac}")
            start_tk.destroy()
        else:
            print(f"Login Failed: {msg}")
            messagebox.showerror("Login Failed", f"Login Failed: {msg}")

    def pay(): 
        msg, t = "", 0
        try:
            if int(amount_entry.get()) <= 0:
                t = 1
                messagebox.showerror("Invalid Amount", "Amount should be greater than 0")
            else:
                float(amount_entry.get())
                mac = mac_entry.get()
                amount = amount_entry.get()
                client.send(pickle.dumps(f"PAY/{mac}/{amount}"))
                msg = recv_msg(client)
        except:
            t = 1
            messagebox.showerror("Invalid Amount", "Amount should be a number")
        if msg == "OK":
            print(f"Paid {amount} for MAC Address: {mac}")
            messagebox.showinfo("Payment Successful", f"Paid {amount} for MAC Address: {mac}")
        elif t == 0:
            print(f"Payment Failed: {msg}")
            messagebox.showerror("Payment Failed", f"Payment Failed: {msg}")
    
    def end_tk():
        start_tk.destroy()
        disconnect_server(client, "client")

    start_tk = tk.Tk()
    start_tk.title("Game Registration/Login")
    
    mac_label = tk.Label(start_tk, text="MAC Address:")
    mac_label.grid(row=0, column=0)
    mac_entry = tk.Entry(start_tk)
    mac_entry.grid(row=0, column=1)

    mac_entry.insert(0, get_mac_address())
    # mac_entry.config(state='readonly') # comment this line to run on local machine
    
    amount_label = tk.Label(start_tk, text="Amount (100/min):")
    amount_label.grid(row=2, column=0)
    amount_entry = tk.Entry(start_tk)
    amount_entry.grid(row=2, column=1)

    amount_entry.insert(0, "100")
    
    register_button = tk.Button(start_tk, text="Register", command=register)
    pay_button = tk.Button(start_tk, text="Pay", command=pay)
    login_button = tk.Button(start_tk, text="Login", command=login)

    register_button.grid(row=1, column=0, columnspan=2)
    pay_button.grid(row=3, column=0, columnspan=2)
    login_button.grid(row=4, column=0, columnspan=2)

    start_tk.protocol("WM_DELETE_WINDOW", end_tk)

    start_tk.mainloop()

    root.mainloop()

def main():
    game_entry()

if __name__ == '__main__':
    main()