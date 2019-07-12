import socket

def udp_send():
	udp_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	udp_socket.bind(("10.120.104.142",9161))
	send_data="UDP TEST"
	udp_socket.sendto(send_data.encode("utf-8"),("10.120.104.142",9162))
	udp_socket.close()

if __name__ == '__main__':
	udp_send()
