import os
import sys
import socket
import logging
import datetime
import threading
from binascii import hexlify

from chat_functions import exit_procedure

def handle_request(client_socket: socket.socket):
    global tracked_clients
    print(f"\nConnected to {client_socket.getpeername()}")
    logging.info(f"Connected to {client_socket.getpeername()}")

    message = client_socket.recv(1024).decode("UTF-8")

    remote_ip, remote_port = client_socket.getsockname()
    name = repr(hexlify(socket.inet_aton(remote_ip)))[2:-1]
    pretty_message = message.replace("\n", " ")
    print(f"Remote ({name}, {remote_port}): {pretty_message}")
    logging.info(f"Remote ({name}, {remote_port}): {pretty_message}")

    if tracked_clients and message != tracked_clients: # if other machine not registered
        client_socket.sendall(tracked_clients.encode("UTF-8"))
        pretty_tracked_clients = tracked_clients.replace('\n', ' ').replace('\n', ' ')
        print(f"Sent {pretty_tracked_clients} to Remote ({name}, {remote_port})")
        logging.info(f"Sent {pretty_tracked_clients} to Remote ({name}, {remote_port})")
        
        tracked_clients = ""
        if input("\nExit? (y/n): ") == "y":
            client_socket.close()
            exit_procedure()
    else: # if other machine already registered
        tracked_clients = message
        client_socket.sendall("OK".encode("UTF-8"))
        print(f"Sent OK to Remote ({name}, {remote_port})")
        logging.info(f"Sent OK to Remote ({name}, {remote_port})")
        

def exit_procedure(optional_message="") -> None:
    global my_socket
    print(optional_message)
    my_socket.close()
    logging.info(optional_message)
    logging.info("Exitting...")
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

if __name__ == "__main__":
    # Variables
    tracker_timeout = 30
    client_timeout = 30
    log = False
    logging_folder = "logs/chat_v2_tracker"
    instance_name =  datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S") # Used for logging
    print_cool_logo = True
    
    # Initializing
    global tracked_clients
    global my_socket
    tracked_clients = ""

    assert len(sys.argv) - 1 == 1, f"""Include tracker port when calling this script. 
    You provided {len(sys.argv)-1} arguments."""

    _, local_port = sys.argv
    local_port = int(local_port)

    if log:
        os.makedirs(logging_folder, exist_ok=True)
        logging.basicConfig(filename=f"{logging_folder}/{instance_name}.log",
                            filemode="w",
                            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                            datefmt='%D %H:%M:%S',
                            level=logging.INFO)
    if print_cool_logo: 
        print("""
████████╗██████╗ ██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
   ██║   ██████╔╝██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
   ██║   ██╔══██╗██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
   ██║   ██║  ██║██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """)

    # Accept any new connections
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.settimeout(tracker_timeout)
    my_socket.bind(("0.0.0.0", local_port))
    my_socket.listen()

    while True:
        try:
            client_socket, (client_ip, client_port) = my_socket.accept()
            threading.Thread(target=handle_request, args=(client_socket,)).start()
        except OSError: # Happens when closing my_socket elsewhere
            pass
