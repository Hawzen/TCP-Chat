import os
import sys
import math
import time
import socket
import logging
import datetime
import threading
from binascii import hexlify

from chat_functions import *

def initate_conversation(remote_ip: str, remote_port: int, client_timeout: int, my_socket: socket.socket) -> None:
    """Contacts remote_ip as client"""
    global host_timing
    host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_socket.settimeout(client_timeout)
    try:
        host_socket.connect((remote_ip, remote_port))
    except (ConnectionRefusedError, TimeoutError, socket.timeout) as e:
        logging.error(f"Warning: The host you're connecting to actively refused connection (have you run the second instance?)")
        return

    if host_timing > time.time(): # If no one connected yet
        my_socket.close()
        host_socket.settimeout(None)
        message_remote(host_socket, True)

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

    assert len(sys.argv) - 1 == 3, f"""Include local port, remote ip, and remote port when calling this script. 
    You provided {len(sys.argv)-1} arguments."""

    _, local_port, remote_ip, remote_port = sys.argv
    local_port, remote_port = int(local_port), int(remote_port)
    
    if log:
        os.makedirs(logging_folder, exist_ok=True)
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
        threading.Thread(target=initate_conversation, args=(remote_ip, remote_port, client_timeout, my_socket)).run()
        
    
        try:
            client_socket, (client_ip, client_port) = my_socket.accept()
            host_timing = time.time()
            message_remote(client_socket, False)
            # We can support multiple users by doing the line above in a thread
        except OSError: # Happens when closing my_socket elsewhere
            pass
