import os
import sys
import math
import time
import socket
import logging
import datetime
import threading
from binascii import hexlify

def accept_connections(my_socket: socket.socket):
    """This function continuously listens for connections. Run as daemon thread"""
    while True:
        client_socket, _ = my_socket.accept()
        threading.Thread(target=message_remote, args=(client_socket, False)).start()

def message_remote(remote_socket: socket.socket, message_first: bool) -> None:
    """Given a socket this function initiates a converstation with it"""
    remote_ip, remote_port = remote_socket.getpeername()
    print(f"Connected to {remote_socket.getpeername()}")
    logging.info(f"Connected to {remote_socket.getpeername()}")
    message_count = 0
    
    if message_first: 
        while True:
            print(f"\nMessage number {message_count}")
            make_and_send_local_message(remote_socket)
            process_remote_message(remote_socket, ip=remote_ip, port=remote_port)
            message_count += 1
    else:
        while True:
            print(f"\nMessage number {message_count}")
            process_remote_message(remote_socket, ip=remote_ip, port=remote_port)
            make_and_send_local_message(remote_socket)
            message_count += 1

def process_remote_message(remote_socket: socket.socket, ip: str, port: int) -> None:
    """Checks incoming message and logs it"""
    name = repr(hexlify(socket.inet_aton(ip)))[2:-1]
    message_log = f"Remote ({name}, {port}): "
    print(message_log + "(waiting...)", end="\r")

    message = remote_socket.recv(1024).decode("UTF-8")
    
    print(message_log + message + "            ")
    logging.info(message_log + message)

    if message == "exit":
        exit_procedure(f"Remote {name} exited")

def make_and_send_local_message(remote_socket: socket.socket) -> str:
    """Make local message"""  
    message_log = f"You ({socket.gethostname()}): "
    message = input(message_log).strip()
    if not message:
        return make_and_send_local_message(remote_socket)
    logging.info(message_log + message)
    
    remote_socket.sendall(message.encode("UTF-8"))

    if message == "exit":
        exit_procedure("You exited")

def exit_procedure(optional_message="") -> None:
    # global my_socket
    print(optional_message)
    print("Exitting...")
    logging.info(optional_message)

    # my_socket.close()
    sys.exit()

def initate_conversation(remote_ip: str, remote_port: int, client_timeout: int) -> None:
    """Contacts remote_ip as client"""
    global my_socket
    global host_timing
    host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_socket.settimeout(client_timeout)
    try:
        host_socket.connect((remote_ip, remote_port))
    except (ConnectionRefusedError, TimeoutError, socket.timeout) as e:
        logging.error(f"Warning: The host you're connecting to actively refused connection (have you run the second instance?)")
        return

    if host_timing > time.time():
        my_socket.close()
        host_socket.settimeout(None)
        threading.Thread(target=message_remote, args=(host_socket, True)).start()

if __name__ == "__main__":
    # Variables
    client_timeout = 5
    host_timeout = 15
    log = True
    print_cool_logo = True
    logging_folder = "logs/chat_v1"
    instance_name =  datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S") # Used for logging

    # Initializing
    global host_timing
    host_timing = math.inf
    global my_socket

    assert len(sys.argv) - 1 == 3, f"""Include local port, remote ip, and remote port when calling this script. 
    You provided {len(sys.argv)-1} arguments."""

    _, local_port, remote_ip, remote_port = sys.argv
    local_port, remote_port = int(local_port), int(remote_port)
    
    if log:
        try:
            os.mkdir("logs")
        except FileExistsError:
            pass
        logging.basicConfig(filename=f"{logging_folder}/{instance_name}.log",
                            filemode="w",
                            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                            datefmt='%D %H:%M:%S',
                            level=logging.INFO)
    if print_cool_logo:
        print("""
████████╗ ██████╗██████╗      ██████╗██╗  ██╗ █████╗ ████████╗   ██╗   ██╗ ██╗
╚══██╔══╝██╔════╝██╔══██╗    ██╔════╝██║  ██║██╔══██╗╚══██╔══╝   ██║   ██║███║
   ██║   ██║     ██████╔╝    ██║     ███████║███████║   ██║█████╗██║   ██║╚██║
   ██║   ██║     ██╔═══╝     ██║     ██╔══██║██╔══██║   ██║╚════╝╚██╗ ██╔╝ ██║
   ██║   ╚██████╗██║         ╚██████╗██║  ██║██║  ██║   ██║       ╚████╔╝  ██║
   ╚═╝    ╚═════╝╚═╝          ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝        ╚═══╝   ╚═╝
    """)
    # Accept any new connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.settimeout(host_timeout)
        my_socket.bind(("0.0.0.0", local_port))
        my_socket.listen(1)

        # Initiate connection with args target
        initate_conversation(remote_ip, remote_port, client_timeout)
        
    
        try:
            client_socket, (client_ip, client_port) = my_socket.accept()
            host_timing = time.time()
            threading.Thread(target=message_remote, args=(client_socket, False)).start()
        except OSError: # Happens when closing my_socket elsewhere
            pass
