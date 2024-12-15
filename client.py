import socket
import signal
import sys

server_sockets = []
server_cores = []

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
        port = 50000 + i
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
        print(f"Server {server_index}: {response}")
    else:
        print(f"Server {server_index} is not connected. Message skipped.")
    return response

def get_cores(server_index):
    response = send_command(server_index, "get cores")
    return int(response.strip())

def start_client(num_servers):
    connect_to_servers(num_servers)
    try:
        for i in range(num_servers):
            server_cores.append(get_cores(i))
            print("Cores initialized", i, server_cores[i])
        
        while True:          
            message = input("Client: ")
            if not message:
                continue
            if message.startswith('0'):
                target_index = 0
            elif message.startswith('1'):
                target_index = 1
            elif message.startswith('2'):
                target_index = 2
            else:
                print("Invalid message prefix. Use '0', '1', or '2'. Message skipped.")
                continue
            if target_index >= len(server_sockets):
                print(f"No server at index {target_index}. Message skipped.")
                continue
            
            response = send_command(message)
 
    except (ConnectionResetError, BrokenPipeError):
        print("A server disconnected unexpectedly.")
    except (KeyboardInterrupt, EOFError):
        signal_handler(None, None)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py <number_of_servers>")
        sys.exit(1)
    try:
        num_servers = int(sys.argv[1])
        if num_servers <= 0:
            raise ValueError
    except ValueError:
        print("Please provide a positive integer for the number of servers.")
        sys.exit(1)
    start_client(num_servers)
