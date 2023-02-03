Port = 7777  # port to listen
Host = ""  # adress to bind
MultivateMethod = "Thread"  # method of multivate, avaliabe only thread and process
CliCommands = {
        "connected": "print(len(sockets))",
        "help": "print ('Avaliable commands:')\nfor i in list(CliCommands):\n    print(i)",
        "kickall": "for sock in sockets:\n    sock.close()",
        "gc": "print(f'gc returned {collect()}')"
        }
