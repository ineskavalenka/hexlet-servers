import socket
import signal
import sys
from task import *

server_socket = None
server_cores = None
server_tasks = []

def signal_handler(signal_received, frame):
    print("\nServer shutting down...")
    if server_socket:
        server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def start_server(host, port):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}...")
    
    try:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                try:
                    data = conn.recv(1024) 
                    if not data:
                        print("Client disconnected.")
                        break
                    request = data.decode('ascii')
                    print(f"Client: {request}")
                    if request == "get cores":
                        conn.sendall(f"{server_cores}".encode('ascii'))
                    elif request == "get load":
                        conn.sendall(f"{1/3}".encode('ascii'))
                    elif request.startswith("assign"):
                        args = request.split(" ")
                        points = int(args[1])
                        description = args[2]
                        estimate = points / server_cores
                        server_tasks.append(Task(estimate, description))
                        conn.sendall("assigned".encode('ascii'))
                    else:
                        response = input("Server: ")
                        conn.sendall(response.encode('ascii'))
                except (ConnectionResetError, BrokenPipeError):
                    print("Client disconnected unexpectedly.")
                    break
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python server.py <port> <cores>")
        sys.exit(1)
    try:
        port = int(sys.argv[1])
        if port <= 0:
            raise ValueError
        server_cores = int(sys.argv[2])
        if not (0 < server_cores <= 100):
            raise ValueError
        print(server_cores)
    except ValueError:
        print("Port should be free, cores should be an integer from 1 to 100")
        sys.exit(1)
    start_server('127.0.0.1', port)
    
