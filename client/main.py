#! /usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep as wait
from config import Port as CfgPort, Retries as CfgRetries, Adress as CfgAdress
from atexit import register
from argparse import ArgumentParser
from sys import exit
from gzip import BadGzipFile, compress, decompress

parser = ArgumentParser(description="Simple chat in terminal")
parser.add_argument("-p",
                    "--port",
                    type=int,
                    help=f"Port for connection (default is {CfgPort})",
                    default=CfgPort)
parser.add_argument("-a",
                    "--adress",
                    type=str,
                    help=f"Adress for connecting (default is {CfgAdress})",
                    default=CfgAdress)
parser.add_argument("-r",
                    "--retries",
                    type=int,
                    help=f"Retries for connecting (default is {CfgRetries})",
                    default=CfgRetries)
args, unknown = parser.parse_known_args()
if len(unknown) != 0:
    print(f"Unknown args: {unknown}")


client = socket(AF_INET, SOCK_STREAM)

try:
    client.connect((args.adress, args.port))
except OSError:
    try:
        for i in range(0, args.retries):
            i += 1
            print(f"Attempt {i} to reconnect")
            try:
                client.connect((args.adress, args.port))
                break
            except OSError:
                if i == args.retries + 1:
                    exit()
                wait(10)
    except KeyboardInterrupt:
        print("\rCancelled by user, exiting")
        exit()

print("Connected!")

# Registering close connection function at exit
register(client.close)
del register


def reader():
    while True:
        msg = decompress(client.recv(4096)).decode()
        if msg != "":
            print(repr(msg))
        else:
            print("Connection closed")
            break


def sender():
    while True:
        client.sendall(compress(bytes(input(), "UTF-8")))


Thread(target=sender, daemon=True).start()
Thread(target=reader, daemon=False).start()
