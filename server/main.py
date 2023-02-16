#! /usr/bin/python3
"""Lavachat - simple terminal chat based on python sockets"""
from os import name
try:
    from readline import set_completer, parse_and_bind
except ImportError:
    try:
        from pyreadline3 import Readline
        readline = Readline()
        set_completer = readline.set_completer
        parse_and_bind = readline.parse_and_bind
        del readline
    except ImportError:
        print("Warning: No readline found")
        print("Note: You can install it with 'pip install pyreadline3'")
        UseReadline = False
else:
        UseReadline = True
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from traceback import print_exc
from sys import stderr, platform, version
from atexit import register
from gzip import BadGzipFile, compress, decompress

print(f"Starting lavachat with Python {version} on {platform} ({name})")
del version, platform, name

try:
    from config import Host, Port, MultivateMethod, CliCommands, StartupCommands
except Exception as e:
    print(f"Can't import config: {e.lower()}")
    print("Using default settings")
    Host = ""
    Port = 7777
    MultivateMethod = "Thread"
    CliCommands = {"connected": "print(len(sockets))"}

# Setting up autocompletion in shell
if UseReadline:
    class CliCompleter():
        def __init__(self, options):
            self.options = sorted(options)
            return

        def complete(self, text, state):
            response = None
            if state == 0:
                if text:
                    self.matches = [s
                                for s in self.options
                                if s and s.startswith(text)]
                else:
                    self.matches = self.options[:]
            try:
                response = self.matches[state]
            except IndexError:
                response = None
            return response

    # Binding autocompletion
    set_completer(CliCompleter(list(CliCommands)).complete)
    parse_and_bind("tab: complete")
    parse_and_bind("set editing-mode vi")

    # Removing useless variables
    del parse_and_bind, set_completer

# Configuring multivate method
if MultivateMethod.strip().lower().strip() == "thread":
    from threading import Thread as Multivate
elif MultivateMethod.strip().lower().strip() == "process":
    from multiprocessing import Process as Multivate
else:
    print("Unknown multivate method, valid values are 'Thread' and 'Process'")
    print("Using Thread by default")
    from threading import Thread as Multivate

# Removing useless variables
del MultivateMethod

# Setting up server
sockets = []
server = socket(AF_INET, SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# Removing useless variables
del socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR


# Setting up server cli
def Cli():
    while True:
        try:
            cmd = input("> ").strip()
            args = cmd.split()[1:]
            try:
                cmd = cmd.split()[0]
            except IndexError:
                continue
            StrArgs = ""
            for arg in args:
                StrArgs += f"{arg} "
            if len(StrArgs) > 0:
                HasArgs = True
            else:
                HasArgs = False
            if cmd in CliCommands:
                exec(CliCommands[cmd])
            else:
                print("Command not found")
        except (EOFError, KeyboardInterrupt):
            exit(3)
        except Exception:
            print_exc(file=stderr)


# Starting server
try:
    server.bind((Host, Port))
except OSError as e:
    print(f"Can't bind adress: \u001b[31;1m{e.strerror.lower()}\u001b[0m")
    exit(2)


# Defines thread for client
class ClientThread(Multivate):
    def __init__(self, clientAdress, clientsock):
        sockets.append(clientsock)
        Multivate.__init__(self)
        self.csocket = clientsock

    def run(self):
        while True:
            # Catching decoding error and disconnecting
            try:
                msg = decompress(self.csocket.recv(4096)).decode("UTF-8")
            except (OSError, UnicodeDecodeError, BadGzipFile):
                sockets.remove(self.csocket)
                self.csocket.close()
                break

            if msg == "":
                sockets.remove(self.csocket)
                self.csocket.close()
                break
            else:
                for sock in sockets:
                    if sock != self.csocket:
                        try:
                            sock.send(compress(bytes(msg, "UTF-8")))
                        except OSError:
                            sock.close()
                            sockets.remove(sock)
                            break


@register
def GracefullyExit():
    for sock in sockets:
        try:
            sock.send(bytes("Server is shutting down, bye-bye", "UTF-8"))
        except OSError:
            pass
        try:
            sockets.remove(sock)
        except ValueError:
            pass
        sock.close()


# Removing useless variables
del register

# Running cli
Multivate(target=Cli, daemon=True).start()

# Accepting connections in infinity cycle
while True:
    try:
        server.listen(1)
        clientsock, clientAdress = server.accept()
        ClientThread(clientAdress, clientsock).start()
    except KeyboardInterrupt:
        GracefullyExit()
        print()
        exit()
    except OSError:
        pass
