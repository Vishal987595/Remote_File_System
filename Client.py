import socket
import os

# server connection details
host = "10.7.38.5"
port = 9999
BUFFER_SIZE = 1024
ENCR = 0
SEPARATOR = "<SEP>"
END = "<END>"
n_file_cmd = ["cwd", "ls", "cd"]
# Encryption type can be changed using one of following list items
encrypt = ["plain", "caesar", "transpose"]


# create client socket
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connecting to the host
client_sock.connect((host, port))
print(f"Connected to {host}:{port}")
hostname = socket.gethostname()

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


# Encrypt data as per ENCR value
def encrypt_data(text):
    if (ENCR == 1):
        return (caesar_encrypt(text))
    elif (ENCR == 2):
        return (transpose(text))
    else:
        return text
# Decrypt data as per ENCR value
def decrypt_data(text):
    if (ENCR == 1):
        return (caesar_decrypt(text))
    elif (ENCR == 2):
        return (transpose(text))
    else:
        return text

# Send a file
def sender(filename):
    print("Sending file")
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
        
# Receive a file
def receive(filename):
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

# Main cmd loop
while True:
    client_msg = input(f"{hostname}: cmd: ")
    client_msg.strip()
    if (client_msg in encrypt):
        ENCR = encrypt.index(client_msg)
        print(f"Encryption changed to: {encrypt[ENCR]}")
    
    elif (client_msg == "exit" or client_msg == "exit()"):
        client_msg = str(ENCR) + encrypt_data(client_msg)
        client_sock.send(client_msg.encode())
        server_msg = client_sock.recv(BUFFER_SIZE)
        break
    
    elif (client_msg[0:3] == "dwd"):
        client_msg = str(ENCR) + encrypt_data(client_msg)
        client_sock.send(client_msg.encode())
        receive_msg = client_sock.recv(BUFFER_SIZE)
        server_msg = receive_msg.decode()
        server_msg = decrypt_data(server_msg[1:])
        if (server_msg == "NOK"):
            print(f"{server_msg}")
        else:
            print("Receiving file")
            filename, filesize = server_msg.split(SEPARATOR)
            try:
                receive(filename)
                print("OK")
            except:
                print("NOK")
    
    elif (client_msg[0:3] == "upd"):
        filename = client_msg[4:]
        try:
            filesize = os.path.getsize(filename)
        except:
            print("no such file exists")
            continue
        client_msg = f"{client_msg}{SEPARATOR}{filesize}"
        client_msg = str(ENCR) + encrypt_data(client_msg)
        client_sock.send(client_msg.encode())
        receive_msg = client_sock.recv(BUFFER_SIZE)
        server_msg = receive_msg.decode()
        server_msg = decrypt_data(server_msg[1:])
        if (server_msg == "READY"):
            sender(filename)
        else:
            print(f"{server_msg}")
            continue
        receive_msg = client_sock.recv(BUFFER_SIZE).decode()
        server_msg = decrypt_data(receive_msg[1:])
        print(f"{server_msg}")
        
    elif (client_msg[0:3] in n_file_cmd):
        client_msg = str(ENCR) + encrypt_data(client_msg)
        client_sock.send(client_msg.encode())
        receive_msg = client_sock.recv(BUFFER_SIZE)
        server_msg = receive_msg.decode()
        if (server_msg[0] == str(ENCR)):
            server_msg = decrypt_data(server_msg[1:])
        else:
            print("NOK")
            continue
        print(f"{server_msg}")

    else:
        client_msg = str(ENCR) + encrypt_data(client_msg)
        client_sock.send(client_msg.encode())
        receive_msg = client_sock.recv(BUFFER_SIZE).decode()
        server_msg = decrypt_data(receive_msg[1:])
        print(f"{server_msg}")

# Closes client socket
client_sock.close()
exit()
