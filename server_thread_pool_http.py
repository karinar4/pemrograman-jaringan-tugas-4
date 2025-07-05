from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = b""
    connection.settimeout(10)
    
    while True:
        try:
            data = connection.recv(4096)
            if data:
                rcv += data

                if b'\r\n\r\n' in rcv:
                    header, body = rcv.split(b'\r\n\r\n', 1)
                    header_lines = header.decode('utf-8', errors='ignore').split('\r\n')

                    content_length = 0
                    for line in header_lines:
                        if line.lower().startswith("content-length:"):
                            try:
                                content_length = int(line.split(":")[1].strip())
                            except:
                                content_length = 0
                            break

                    total_len = len(body)
                    if total_len >= content_length:
                        hasil = httpserver.proses(rcv)
                        connection.sendall(hasil)
                        connection.close()
                        return
            else:
                break
        except OSError:
            break

    connection.close()
    return

def Server():
	the_clients = []
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	my_socket.bind(('0.0.0.0', 8885))
	my_socket.listen(1)

	with ThreadPoolExecutor(20) as executor:
		while True:
				connection, client_address = my_socket.accept()
				p = executor.submit(ProcessTheClient, connection, client_address)
				the_clients.append(p)
				jumlah = ['x' for i in the_clients if i.running()==True]
				print(jumlah)

def main():
	Server()

if __name__=="__main__":
	main()