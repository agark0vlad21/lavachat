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
                exit
            wait(10)

def task():
    while True:
        in_data =  client.recv(4096)
        if in_data.decode() != "":
            print(in_data.decode())
        else:
            print("looks like server shutdowned")
            client.close()
            exit(0)
            break

def task2():
    while True:
        out_data = input()
        client.sendall(bytes(out_data,'UTF-8'))

t1 = Thread(target=task2)
t2 = Thread(target=task)

t1.start()
t2.start()

t1.join()
t2.join()
