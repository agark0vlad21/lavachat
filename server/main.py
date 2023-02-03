import readline
import socket
try:
    from config import Host, Port, MultivateMethod, CliCommands
except ImportError as e:
    print(f"can't import config: {e}")
    exit(3)


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
readline.set_completer(CliCompleter(list(CliCommands)).complete)
readline.parse_and_bind("tab: complete")
readline.parse_and_bind("set editing-mode vi")

# Configuring multivate method
if MultivateMethod.strip().lower() == "thread":
    from threading import Thread as multivate
elif MultivateMethod.strip().lower() == "process":
    from multiprocessing import Process as multivate
else:
    print("unkown multivate method, valid values are 'thread' and 'process'")
    exit(1)

# Setting up server
sockets = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# Setting up server cli
def Cli():
    while True:
        try:
            cmd = input("put your command here: ").strip()
            if cmd in CliCommands:
                exec(CliCommands[cmd])
            else:
                print("command not found")
        except (EOFError, KeyboardInterrupt):
            exit(3)
        except Exception as e:
            print(e.__class__, e, e.args)


# Starting server
try:
    server.bind((Host, Port))
except OSError as e:
    print(f"Can't bind adress: \u001b[31;1m{e.strerror.lower()}\u001b[0m")
    exit(2)


# Defines thread for client
class ClientThread(multivate):
    def __init__(self, clientAdress, clientsock):
        sockets.append(clientsock)
        multivate.__init__(self)
        self.csocket = clientsock

    def run(self):
        msg = ""
        while True:
            try:
                data = self.csocket.recv(4096)
            except OSError:
                sockets.remove(self.csocket)
                self.csocket.close()
                break

            try:
                msg = data.decode()
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


# Running cli
multivate(target=Cli).start()

# Accepting connections in infinity cycle
while True:
    try:
        server.listen(1)
        clientsock, clientAdress = server.accept()
        ClientThread(clientAdress, clientsock).start()
    except (KeyboardInterrupt, EOFError):
        exit(4)
