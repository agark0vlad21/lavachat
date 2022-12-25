PORT = 7777 # port to listen
HOST = "" # adress to bind
MULTIVATE_METHOD = "thread" # method of multivate, avaliabe only thread and process
CLI_COMMANDS = {
        "connected": "print(len(sockets))",
        "help": "for i in list(CLI_COMMANDS):\n    print(i)"
        }
