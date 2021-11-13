import os
import sys
import math
import time
import socket
import random
import logging
import datetime
import threading
from binascii import hexlify

def handle_request(client_socket: socket.socket):
    global tracked_clients
    while True:
        message = client_socket.recv(1024).decode("UTF-8")
        print("Recieved message from client", message)
        if message[0] == "0":
            tracked_clients.append("\n".join(message.split()[1:]))
        elif message[0] == "1":
            if len(tracked_clients) > 1:
                index = 1 if tracked_clients[0][0] == client_socket.getsockname()[0] else 0
                message = f"1\n{tracked_clients[index]}"
            else:
                message = "0"
            print("Sent message to client", message)
            client_socket.sendall(message.encode("UTF-8"))
        time.sleep(1)
        # CHeck if its closed remove its name in tracked clients

if __name__ == "__main__":
    # Variables
    tracker_timeout = 100
    client_timeout = 20
    
    # Initializing
    global tracked_clients
    tracked_clients = []

    assert len(sys.argv) - 1 == 1, f"""Include tracker port when calling this script. 
    You provided {len(sys.argv)-1} arguments."""

    _, local_port = sys.argv
    local_port = int(local_port)

    # Accept any new connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.settimeout(15)
        my_socket.bind(("0.0.0.0", local_port))
        my_socket.listen()

        while True:
            try:
                client_socket, (client_ip, client_port) = my_socket.accept()
                client_socket.settimeout(client_timeout)
                threading.Thread(target=handle_request, args=(client_socket,)).start()
            except OSError: # Happens when closing my_socket elsewhere
                pass
