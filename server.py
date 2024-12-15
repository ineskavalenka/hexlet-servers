import socket
import signal
import sys

server_socket = None

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
                    print(f"Client: {data.decode('ascii')}")
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
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    try:
        port = int(sys.argv[1])
        if port <= 0:
            raise ValueError
    except ValueError:
        print("Usage: python server.py <port>")
        sys.exit(1)
    start_server('127.0.0.1', port)
    
