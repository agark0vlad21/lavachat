# [Server]
Port = 7777  # Port to listen
Host = ""  # Adress to bind
MultivateMethod = "Thread"  # Method of multivate (Thread/Process)
Protocol = "TCP"  # Protocol for server (TCP/UDP)

# [Cli]
CliCommands = {
        "connected": "print(len(sockets))",
        "help": "print ('Avaliable commands:')\nfor i in list(CliCommands):\n    print(i)",
        "kickall": "for sock in sockets:\n    sock.close()",
        "gc": "print(f'gc returned {collect()}')",
        "exec": "exec(StrArgs)",
        "eval": "print(eval(StrArgs))",
        "exit": "print('for exit press Ctrl + C')"
        }
StartupCommands = ()  # Tuple/list of cli commands that will be executed at server startup
