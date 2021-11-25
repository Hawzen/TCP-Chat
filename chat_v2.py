import os
import sys
import math
import time
import socket
import random
import logging
import datetime
import threading

from chat_functions import *

def initate_conversation(remote_ip: str, remote_port: int, client_timeout: int, my_socket: socket.socket) -> None:
    """Contacts remote_ip as client"""
    global host_timing
    host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_socket.settimeout(client_timeout)
    try:
        host_socket.connect((remote_ip, remote_port))
        my_socket.close()
        message_remote(host_socket, True)
    except (ConnectionRefusedError, TimeoutError, socket.timeout):
        pass

def register_or_contact(tracker_ip: str, tracker_port: int, 
                                tracker_timeout: int, local_ip: str, local_port: int) -> None:
    """If this function is called before remote calls it then local will register their ip and port in tracker
    If this function is called after remote calls it then local will contact remote via tracker"""
    global host_timing
    global other_address
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as register_socket:
        register_socket.settimeout(tracker_timeout)
        register_socket.connect((tracker_ip, tracker_port))
        message = f"\n{local_ip}\n{local_port}"
        register_socket.sendall(message.encode("UTF-8"))
        message = register_socket.recv(1024).decode("UTF-8")
        print("Got message", message.replace("\n", " ").strip())
        if message == "OK":
            other_address = None
            return
        else:
            remote_ip, remote_port = message.split("\n")[1:]
            initate_conversation(remote_ip, int(remote_port), client_timeout, my_socket)

if __name__ == "__main__":
    # Variables
    client_timeout = 15
    host_timeout = 15
    tracker_timeout = 30
    start_local_port_range, end_local_port_range = 21000, 22000
    log = True
    logging_folder = "logs/chat_v2"
    instance_name =  datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S") # Used for logging
    print_cool_logo = True

    # Initializing
    global host_timing
    global other_address
    host_timing = math.inf
    other_address = None

    assert len(sys.argv) - 1 == 2, f"""Include tracker ip, and tracker port when calling this script. 
    You provided {len(sys.argv)-1} arguments."""

    _, tracker_ip, tracker_port = sys.argv
    tracker_port = int(tracker_port)
    
    local_port = random.randint(start_local_port_range, end_local_port_range)

    if log:
        os.makedirs(logging_folder, exist_ok=True)
        logging.basicConfig(filename=f"{logging_folder}/{instance_name}.log",
                            filemode="w",
                            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                            datefmt='%D %H:%M:%S',
                            level=logging.INFO)

    if print_cool_logo:
        print("""
████████╗ ██████╗██████╗      ██████╗██╗  ██╗ █████╗ ████████╗   ██╗   ██╗██████╗ 
╚══██╔══╝██╔════╝██╔══██╗    ██╔════╝██║  ██║██╔══██╗╚══██╔══╝   ██║   ██║╚════██╗
   ██║   ██║     ██████╔╝    ██║     ███████║███████║   ██║█████╗██║   ██║ █████╔╝
   ██║   ██║     ██╔═══╝     ██║     ██╔══██║██╔══██║   ██║╚════╝╚██╗ ██╔╝██╔═══╝ 
   ██║   ╚██████╗██║         ╚██████╗██║  ██║██║  ██║   ██║       ╚████╔╝ ███████╗
   ╚═╝    ╚═════╝╚═╝          ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝        ╚═══╝  ╚══════╝
    """)

    # Accept any new connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.settimeout(host_timeout)
        my_socket.bind(("0.0.0.0", local_port))
        my_socket.listen(1)

        # Register or contact via the tracker
        threading.Thread(target=register_or_contact, args=(tracker_ip, tracker_port, tracker_timeout, socket.gethostbyname(socket.gethostname()), local_port)).start()

        try:
            client_socket, (client_ip, client_port) = my_socket.accept()
            host_timing = time.time()
            message_remote(client_socket, False)
        except OSError: # Happens when closing my_socket elsewhere
            pass
