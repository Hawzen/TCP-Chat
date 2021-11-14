import os
import sys
import math
import time
import socket
import random
import logging
import datetime
import threading
from itertools import chain
from binascii import hexlify

from chat_functions import *

def initate_conversation(remote_ip: str, client_timeout: int, my_socket: socket.socket,
                start_remote_port_range: int, end_remote_port_range: int, stop_event: threading.Event) -> None:
    """Contacts remote_ip as client"""
    global host_timing
    host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_socket.settimeout(client_timeout)

    for remote_port in range(start_remote_port_range, end_remote_port_range):
        try:
            if remote_port == local_port:
                continue
            host_socket.connect((remote_ip, remote_port))
            
            stop_event.set()
            if host_timing > time.time(): # If no one connected yet
                my_socket.close()
                host_socket.settimeout(None)
                message_remote(host_socket, True)
            else:
                host_socket.close()
            

        except (OSError, ConnectionRefusedError, TimeoutError, socket.timeout) as e:
            pass        

if __name__ == "__main__":
    # Variables
    client_timeout = 5
    host_timeout = 15
    start_remote_port_range, end_remote_port_range = 23000, 24000
    num_scans = 10
    log = True
    print_cool_logo = True
    logging_folder = "logs/chat_v1"
    instance_name =  datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S") # Used for logging

    # Initializing
    assert int(end_remote_port_range - start_remote_port_range) == end_remote_port_range - start_remote_port_range, \
        "End range and start range have to be multiples of 10"
    assert len(sys.argv) - 1 == 1, f"""Include remote ip when calling this script. 
    You provided {len(sys.argv)-1} arguments."""

    
    global host_timing
    host_timing = math.inf

    num_scanners = int((end_remote_port_range - start_remote_port_range) / num_scans)
    _, remote_ip= sys.argv
    local_port = random.randint(start_remote_port_range, end_remote_port_range)
    
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
   ██║   ██║     ██╔═══╝     ██║     ██╔══██║██╔══██║   ██║╚════╝╚██╗ ██╔╝ ╚═══██╗
   ██║   ╚██████╗██║         ╚██████╗██║  ██║██║  ██║   ██║       ╚████╔╝ ██████╔╝
   ╚═╝    ╚═════╝╚═╝          ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝        ╚═══╝  ╚═════╝ 
    """)

    print(f"My port: {local_port}")
    # Accept any new connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.settimeout(host_timeout)
        my_socket.bind(("0.0.0.0", local_port))
        my_socket.listen(1)

        # Initiate connection with args target
        stop_event = threading.Event()
        for i in range(num_scanners):
            threading.Thread(target=initate_conversation, args=(remote_ip, client_timeout, my_socket, 
                    int(start_remote_port_range + (end_remote_port_range - start_remote_port_range) / num_scanners * i),
                    int(start_remote_port_range + (end_remote_port_range - start_remote_port_range) / num_scanners * (i+1)),
                    stop_event
                )).start()
        
    
        try:
            client_socket, (client_ip, client_port) = my_socket.accept()
            host_timing = time.time()
            message_remote(client_socket, False)
            # We can support multiple users by doing the line above in a thread
        except OSError: # Happens when closing my_socket elsewhere
            pass
