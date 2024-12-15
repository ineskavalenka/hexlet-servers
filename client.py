import socket
import signal
import sys
from task import *

server_sockets = []
server_cores = []
server_load = []
base_port = 0

def signal_handler(signal_received, frame):
    print("\nClient shutting down...")
    for sock in server_sockets:
        if sock:
            sock.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def connect_to_servers(num_servers):
    global server_sockets
    for i in range(num_servers):
        host = '127.0.0.1'
        port = base_port + i
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            server_sockets.append(sock)
            print(f"Connected to server {i} at {host}:{port}")
        except Exception as e:
            print(f"Failed to connect to server {i} at {host}:{port}: {e}")
            server_sockets.append(None)

def send_command(server_index, message):
    response = ""
    target_socket = server_sockets[server_index]
    if target_socket:
        target_socket.sendall(message.encode('ascii'))
        data = target_socket.recv(1024)
        response = data.decode('ascii')
        # print(f"Server {server_index}: {response}")
    #else:
        # print(f"Server {server_index} is not connected. Message skipped.")
    return response

def get_cores(server_index):
    response = send_command(server_index, "get cores")
    return int(response.strip())

def get_load(server_index):
    response = send_command(server_index, "get load")
    response = float(response)
    return response

def get_task():
    while True:
        d = input("Task?> ")
        errorstring = "Enter the task in the format '<storypoints(int[1..100])> <description(string)>'"
        try:
            i = d.index(' ')
            storypoints = int(d[:i])
            description = d[i+1:].strip()
            # print(storypoints, description)
            if not (0 < storypoints <= 100) or not description:
                raise ValueError(errorstring)
            return Task(storypoints, description)
        except (ValueError, IndexError):
            print(errorstring)

def assign_task(server_index, task):
    response = send_command(server_index, f"assign {task.storypoints} {task.description}")
    return response == "assigned"

def start_client(num_servers):
    connect_to_servers(num_servers)
    
    try:
        for i in range(num_servers):
            server_cores.append(get_cores(i))
            print("Cores initialized", i, server_cores[i])
        
        for i in range(num_servers):
            server_load.append(0.0)

        while True:              
            task = get_task()
            
            for i in range(num_servers):
                server_load[i] = get_load(i)
                print("Load updated", i, server_load[i])
            
            min_load_i = 0
            min_load_v = server_load[0]
            for i in range(1, num_servers):
                load = server_load[i] + task.storypoints / server_cores[i]
                if load < min_load_v:
                    min_load_v = load
                    min_load_i = i  
            assign_task(min_load_i, task)
            print("Task assigned, server=", min_load_i, sep='')

    except (ConnectionResetError, BrokenPipeError):
        print("A server disconnected unexpectedly.")
    except (KeyboardInterrupt, EOFError):
        signal_handler(None, None)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <base_port> <number_of_servers>")
        sys.exit(1)
    try:
        base_port = int(sys.argv[1])
        if base_port <= 0:
            raise ValueError
        num_servers = int(sys.argv[2])
        if num_servers <= 0:
            raise ValueError
    except ValueError:
        print("Please provide a positive integer for the number of servers.")
        sys.exit(1)
    start_client(num_servers)
