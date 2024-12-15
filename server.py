import socket

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server listening on {host}:{port}...")
        
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)  # Receive data from the client
                if not data:
                    break  # Client has closed the connection
                print(f"Received: {data.decode('ascii')}")
                conn.sendall(data)  # Echo back the received data

if __name__ == "__main__":
    start_server()
