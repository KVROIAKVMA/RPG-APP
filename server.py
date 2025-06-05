import socket
import threading

class VTTServer:
    def __init__(self, host="0.0.0.0", port=12345):
        self.host = host
        self.port = port
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor iniciado en {self.host}:{self.port}")

    def start(self):
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Cliente conectado: {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                self.broadcast(data, client_socket)
            except:
                break
        client_socket.close()
        self.clients.remove(client_socket)

    def broadcast(self, data, sender):
        for client in self.clients:
            if client != sender:
                try:
                    client.sendall(data)
                except Exception as e:
                    print(f"Error enviando a cliente: {e}")

if __name__ == "__main__":
    server = VTTServer()
    server.start()
    input("Presiona Enter para salir...\n")
