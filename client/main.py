from sys import exit
import socket
from threading import Thread
from time import sleep as wait
from config import PORT, RETRIES, SERVER

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((SERVER, PORT))
except ConnectionRefusedError:
    for i in range(0, RETRIES):
        i += 1
        print(f"attempt {i} to reconnect")
        try:
            client.connect((SERVER, PORT))
            break
        except ConnectionRefusedError:
            if i == RETRIES + 1:
                exit()
            wait(10)
print("Connected!")


def reader():
    while True:
        data = client.recv(4096)
        if data.decode() != "":
            print(repr(data.decode()))
        else:
            print("Connection closed")
            client.close()
            exit(0)
            break


def sender():
    while True:
        client.sendall(bytes(input(), "UTF-8"))


Thread(target=sender, daemon=True).start()
Thread(target=reader, daemon=True).start()

# Infinity cycle for do nothing
try:
    while True:
        wait(10)
except KeyboardInterrupt:
    exit()
