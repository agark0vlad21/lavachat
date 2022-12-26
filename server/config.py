PORT = 7777 # port to listen
HOST = "" # adress to bind
MULTIVATE_METHOD = "thread" # method of multivate, avaliabe only thread and process
CLI_COMMANDS = {
        "connected": "print(len(sockets))",
        "help": "print ('Avaliable commands:')\nfor i in list(CLI_COMMANDS):\n    print(i)",
        "kickall": "for sock in sockets:\n    sock.close()"
        }
KICK_WORDS = []
