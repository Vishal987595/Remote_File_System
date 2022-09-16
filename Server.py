import socket
import os

# Defining the port on which host server
Server_port = 9999
Server_host = "10.7.38.5"
BUFFER_SIZE = 1024
ENCR = "0"
SEPARATOR = "<SEP>"
END = "<END>"

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

# Caesar encryption with offset of 2
def caesar_encrypt(text, offset=2):
    l = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    encrypted_text = ""
    for ch in text:
        idx = l.find(ch)
        if (idx == -1):
            en_ch = ch
        else:
            en_ch = l[idx + offset] if (idx + offset)<len(l) else l[idx + offset - len(l)]
        encrypted_text += str(en_ch)
    return encrypted_text
# Caesar decryption with offset of 2
def caesar_decrypt(text, offset=2):
    l = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    decrypted_text = ""
    for ch in text:
        idx = l.find(ch)
        if(idx == -1):
            den_ch = ch
        else:
            den_ch = l[idx - offset] if (idx - offset)>=0 else l[idx - offset + len(l)]
        decrypted_text += str(den_ch)
    return decrypted_text

# Transpose encryption
def transpose(text):
    l = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    transposed_text = ""
    word = ""
    for ch in text:
        if (ch in l):
            word += str(ch)
        else:
            transposed_text += word[::-1]
            transposed_text += str(ch)
            word = ""
    if (len(word)):
        transposed_text += word[::-1]
    return transposed_text


def encrypt_data(text):
    if (ENCR == "1"):
        return (caesar_encrypt(text))
    elif (ENCR == "2"):
        return (transpose(text))
    else:
        return text
def decrypt_data(text):
    if (ENCR == "1"):
        return (caesar_decrypt(text))
    elif (ENCR == "2"):
        return (transpose(text))
    else:
        return text

# Receive a file 
def receive(filename, filesize):
    with open(filename, "wb") as f:
        while True:
            bytes_read = client_sock.recv(BUFFER_SIZE)
            try:
                bytes_read = decrypt_data(bytes_read.decode())
                bytes_read = bytes_read.encode()
            except:
                if (ENCR != 0):
                    bytes_read = decrypt_data(bytes_read)
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
                bytes_read = encrypt_data(bytes_read)
                client_sock.send(bytes_read.encode())
                return
            try:
                bytes_read = encrypt_data(bytes_read.decode()).encode()
            except:
                pass
            client_sock.send(bytes_read)

# Main command loop
while True:
    client_msg = client_sock.recv(BUFFER_SIZE).decode()
    print(f"server listened {client_msg}")
    # splitting up msg
    # print("Encryption", client_msg[0])
    ENCR = client_msg[0]
    parse_msg = decrypt_data(client_msg[1:])
    parse_msg = parse_msg.split()
    if (len(parse_msg) == 0):
        client_msg = "command not entered."
        client_msg = str(ENCR) + encrypt_data(client_msg)
        client_sock.send(client_msg.encode())
    
    elif (parse_msg[0] == "exit"):
        break
    
    elif (parse_msg[0] == "cwd"):
        client_msg = os.getcwd()
        client_msg = str(ENCR) + encrypt_data(client_msg)
        send_msg = client_msg.encode()
        client_sock.send(send_msg)
    
    elif (parse_msg[0] == "ls"):
        client_msg = os.listdir(os.getcwd())
        client_msg = ' '.join(client_msg)
        if (len(client_msg) == 0):
            client_msg = " "
        client_msg = str(ENCR) + encrypt_data(client_msg)
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
        client_msg = str(ENCR) + encrypt_data(client_msg)
        send_msg = client_msg.encode()
        client_sock.send(send_msg)
    
    elif (parse_msg[0] == "upd"):
        filename, filesize = parse_msg[1].split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
        client_msg = "READY"
        client_msg = str(ENCR) + encrypt_data(client_msg)
        client_sock.send(client_msg.encode())
        receive(filename, filesize)
        if (os.path.getsize(filename) == filesize):
            client_msg = "OK"
        else:
            client_msg = "NOK"
        client_msg = str(ENCR) + encrypt_data(client_msg)
        client_sock.send(client_msg.encode())
    
    elif (parse_msg[0] == "dwd"):
        filename = parse_msg[1]
        try:
            filesize = os.path.getsize(filename)
            client_msg = f"{filename}{SEPARATOR}{filesize}"
            client_msg = str(ENCR) + encrypt_data(client_msg)
            client_sock.send(client_msg.encode())
            sender(filename)
        except:
            client_msg = str(ENCR) + encrypt_data("NOK")
            client_sock.send(client_msg.encode())
    
    else:
        client_msg = "no such command exists"
        client_msg = str(ENCR) + encrypt_data(client_msg)
        client_sock.send(client_msg.encode())
        

# Closes the connection with client
client_sock.close()
exit()