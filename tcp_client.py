import socket

def tcp_client():
	tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp_socket.connect(("10.120.104.153",9162))
	send_data = "TCP Client Request"
	tcp_socket.send(send_data.encode("utf-8"))
	recv_data = tcp_socket.recv(1024)
	print(recv_data.decode("utf-8"))
	tcp_socket.close()

if __name__ == "__main__":
	tcp_client()
	
