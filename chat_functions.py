import sys
import socket
import logging
from binascii import hexlify

def message_remote(remote_socket: socket.socket, message_first: bool) -> None:
    """Given a socket this function initiates a converstation with it"""
    remote_ip, remote_port = remote_socket.getpeername()
    print(f"Connected to {remote_socket.getpeername()}")
    logging.info(f"Connected to {remote_socket.getpeername()}")
    
    while True:
        if message_first:
            make_and_send_local_message(remote_socket)
            process_remote_message(remote_socket, ip=remote_ip, port=remote_port)
        else:
            process_remote_message(remote_socket, ip=remote_ip, port=remote_port)
            make_and_send_local_message(remote_socket)

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
    message_log = f"You ({socket.gethostname()}): "
    message = input(message_log).strip()
    if not message:
        return make_and_send_local_message(remote_socket)
    logging.info(message_log + message)
    
    remote_socket.sendall(message.encode("UTF-8"))

    if message == "exit":
        exit_procedure("You exited")

def exit_procedure(optional_message="") -> None:
    if optional_message:
        print(optional_message)
        logging.info(optional_message)
    else:
        print("Exitting...")
        logging.info("Exitting...")
    sys.exit()

