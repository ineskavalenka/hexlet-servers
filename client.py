import socket

def start_client(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")
        
        message = "Hello, Server!"
        print(f"Sending: {message}")
        client_socket.sendall(message.encode('ascii'))  # Send ASCII message
        
        data = client_socket.recv(1024)  # Receive echoed message
        print(f"Received from server: {data.decode('ascii')}")

if __name__ == "__main__":
    start_client()
