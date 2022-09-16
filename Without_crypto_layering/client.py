import socket
import os

# server connection details
host = "127.0.0.1"
port = 9999
BUFFER_SIZE = 1024

# create client socket
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connecting to the host
client_sock.connect((host, port))
print(f"Connected to {host}:{port}")
hostname = socket.gethostname()
n_file_cmd = ["cwd", "ls", "ls ", "cd ", "cd"]
SEPARATOR = "<SEP>"

# Send a file
def sender(filename):
    print("Sending file")
    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                f.close()
                bytes_read = "<END>"
                client_sock.send(bytes_read.encode())
                print("OK")
                return
            client_sock.send(bytes_read)
        
# Receive a file
def receive(filename):
    with open(filename, "wb") as f:
        while True:
            bytes_read = client_sock.recv(BUFFER_SIZE)
            bytes_write = bytes_read.removesuffix(b"<END>")
            if (len(bytes_write) < len(bytes_read)):
                f.write(bytes_write)
                f.close()
                return
            f.write(bytes_write)

# Main cmd loop
while True:
    client_msg = input(f"{hostname}: cmd: ")
    # client_msg.strip()
    client_msg.strip()
    if (client_msg == "exit" or client_msg == "exit()"):
        client_sock.send(client_msg.encode())
        server_msg = client_sock.recv(BUFFER_SIZE)
        break
    
    elif (client_msg[0:3] == "dwd"):
        client_sock.send(client_msg.encode())
        receive_msg = client_sock.recv(BUFFER_SIZE)
        server_msg = receive_msg.decode()
        if (server_msg == "NOK"):
            print(server_msg)
        else:
            print("Receiving file")
            filename, filesize = server_msg.split(SEPARATOR)
            receive(filename)
            print("OK")
    
    elif (client_msg[0:3] == "upd"):
        filename = client_msg[4:]
        try:
            filesize = os.path.getsize(filename)
        except:
            print("No such file exists")
            continue
        client_sock.send(f"{client_msg}{SEPARATOR}{filesize}".encode())
        receive_msg = client_sock.recv(BUFFER_SIZE)
        server_msg = receive_msg.decode()
        if (server_msg == "Ready to receive file content"):
            sender(filename)

    elif (client_msg[0:3] in n_file_cmd):
        client_sock.send(client_msg.encode())
        receive_msg = client_sock.recv(BUFFER_SIZE)
        server_msg = receive_msg.decode()
        print(f"{server_msg}")
    else:
        client_sock.send(client_msg.encode())
        receive_msg = client_sock.recv(BUFFER_SIZE)
        server_msg = receive_msg.decode()
        print(f"{server_msg}")

# Closes client socket
client_sock.close()
exit()
