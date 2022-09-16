import socket
import os

# Defining the port on which host server
Server_port = 9999
Server_host = "127.0.0.1"
BUFFER_SIZE = 1024

# create server socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# attach server to the host
server_sock.bind((Server_host, Server_port))

# Read the clients to make up connection
print("watiting for a connection.")
server_sock.listen()

# Accepts the request to connect from client
client_sock, addr = server_sock.accept()
print(f"connected to client {addr}")
SEPARATOR = "<SEP>"
END = "<END>"

# Receive a file 
def receive(filename, filesize):
    with open(filename, "wb") as f:
        while True:
            bytes_read = client_sock.recv(BUFFER_SIZE)
            print(bytes_read)
            bytes_write = bytes_read.removesuffix(b"<END>")
            if (len(bytes_write) < len(bytes_read)):
                f.write(bytes_write)
                f.close()
                return
            f.write(bytes_write)

# Send a file
def sender(filename):
    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                f.close()
                bytes_read = "<END>"
                client_sock.send(bytes_read.encode())
                return
            client_sock.send(bytes_read)

# Main command loop
while True:
    client_msg = client_sock.recv(BUFFER_SIZE).decode()
    print(f"server listened {client_msg}")
    # splitting up msg
    parse_msg = client_msg.split()
    if (parse_msg[0] == "exit"):
        break
    
    elif (parse_msg[0] == "cwd"):
        client_msg = os.getcwd()
        send_msg = client_msg.encode()
        client_sock.send(send_msg)
    
    elif (parse_msg[0] == "ls"):
        client_msg = os.listdir(os.getcwd())
        client_msg = ' '.join(client_msg)
        if (len(client_msg) == 0):
            client_msg = " "
        send_msg = client_msg.encode()
        client_sock.send(send_msg)
    
    elif (parse_msg[0] == "cd"):
        if (len(parse_msg) <= 1):
            client_msg = "arguments missing"
        elif os.path.isdir(parse_msg[1]):
            os.chdir(parse_msg[1])
            client_msg = f"dir to changed to {parse_msg[1]}\n{os.getcwd()}"
        else:
            client_msg = "no such directory exists"
        send_msg = client_msg.encode()
        client_sock.send(send_msg)
    
    elif (parse_msg[0] == "upd"):
        filename, filesize = parse_msg[1].split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
        client_msg = "Ready to receive file content"
        client_sock.send(client_msg.encode())
        receive(filename, filesize)
    
    elif (parse_msg[0] == "dwd"):
        filename = parse_msg[1]
        try:
            filesize = os.path.getsize(filename)
            client_sock.send(f"{filename}{SEPARATOR}{filesize}".encode())
            sender(filename)
        except:
            client_sock.send(f"NOK".encode())
            

    else:
        client_msg = "No such command exists"
        client_sock.send(client_msg.encode())
        


# Closes the connection with client
client_sock.close()
exit()
