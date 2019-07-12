import socket

def tcp_server():
	tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp_server_socket.bind(("10.120.104.153",9162))
	tcp_server_socket.listen(128)
	while True:
		client_socket, client_addr = tcp_server_socket.accept()
		recv_data = client_socket.recv(1024)
		print(recv_data.decode("utf-8"))
		client_socket.send("TCP Server Response".encode("utf-8"))
		#client_socket.close()
		#tcp_server_socket.close()

if __name__ == "__main__":
	tcp_server()
