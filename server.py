import socket
import signal
import threading
import sys
from task import *
import time
import queue

server_socket = None
server_cores = None

### Task handling
server_tasks = queue.Queue()

remaining_lock = threading.Lock()
remaining_current_task = 0.0
remaining_queue = 0.0
###

def task_processor(server_tasks, task_state):
    global remaining_current_task
    global remaining_queue

    while True:
        task = server_tasks.get()

        if task is None:
            continue

        remaining_lock.acquire()
        remaining_queue -= task.storypoints
        remaining_current_task = task.storypoints
        print(f"Doing task {task.description} ({task.storypoints})")
        print(f"Remaining effort {remaining_queue + remaining_current_task}")
        remaining_lock.release()

        while remaining_current_task > 0:
            time.sleep(1)
            remaining_lock.acquire()
            remaining_current_task -= 1
            remaining_lock.release()

        remaining_lock.acquire()
        remaining_current_task = 0
        server_tasks.task_done() 
        remaining_lock.release()

def signal_handler(signal_received, frame):
    print("\nServer shutting down...")
    if server_socket:
        server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def start_server(host, port):
    global server_socket
    global remaining_queue
    global remaining_current_task
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}...")
    
    try:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        
        task_thread = threading.Thread(target=task_processor, args=(server_tasks, None), daemon=True)
        task_thread.start()

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
                        estimate1 = 0
                        remaining_lock.acquire()
                        estimate1 = remaining_current_task + remaining_queue
                        print("estimate", estimate1)
                        remaining_lock.release()
                        conn.sendall(f"{estimate1}".encode('ascii'))
                    elif request.startswith("assign"):
                        args = request.split(" ")
                        points = int(args[1])
                        description = args[2]
                        estimate2 = points / server_cores
                        remaining_lock.acquire()
                        server_tasks.put(Task(estimate2, description))
                        remaining_queue += estimate2
                        remaining_lock.release()
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
