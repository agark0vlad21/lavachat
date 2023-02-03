from readline import set_completer, parse_and_bind
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from traceback import print_exc
from sys import stderr
from atexit import register
from gc import collect
try:
    from config import Host, Port, MultivateMethod, CliCommands
except ImportError as e:
    print(f"Can't import config: {e}")
    print("Using default settings")
    Host = ""
    Port = 7777
    MultivateMethod = "Thread"
    CliCommands = {"connected": "print(len(sockets))"}


# Setting up autocompletion in shell
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
if MultivateMethod.strip().lower() == "thread":
    from threading import Thread as Multivate
elif MultivateMethod.strip().lower() == "process":
    from multiprocessing import Process as Multivate
else:
    print("Unkown multivate method, valid values are 'Thread' and 'Process'")
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
            cmd = input("Put your command here: ").strip()
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
            try:
                msg = self.csocket.recv(4096).decode()
            except OSError:
                sockets.remove(self.csocket)
                self.csocket.close()
                break
            except UnicodeDecodeError:
                self.csocket.close()
                sockets.remove(self.csocket)
                break

            if msg == "":
                sockets.remove(self.csocket)
                self.csocket.close()
                break
            else:
                for sock in sockets:
                    if sock != self.csocket:
                        try:
                            sock.send(bytes(msg, "UTF-8"))
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
        exit()
