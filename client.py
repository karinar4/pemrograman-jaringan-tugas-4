import socket
import os
import sys
from datetime import datetime

class HttpClient:
    def __init__(self, host='172.16.16.101', port=8885):
        self.host = host
        self.port = port
        
    def send_request(self, request):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            sock.connect((self.host, self.port))
            
            if isinstance(request, str):
                request = request.encode()
            sock.send(request)
            
            response = b''
            while True:
                try:
                    data = sock.recv(1024)
                    if not data:
                        break
                    response += data
                except socket.timeout:
                    break
                    
            sock.close()
            return response.decode('utf-8', errors='ignore')
            
        except Exception as e:
            return f"Error: {str(e)}"
            
    def get_file(self, filename):
        request = f"GET /{filename} HTTP/1.0\r\n\r\n"
        response = self.send_request(request)
    
        if isinstance(response, str):
            response = response.encode('utf-8', errors='ignore')
    
        parts = response.split(b'\r\n\r\n', 1)
        if len(parts) == 2:
            headers, body = parts
    
            headers_str = headers.decode('utf-8', errors='ignore')
    
            if "200 OK" in headers_str:
                try:
                    with open(filename, 'wb') as f:
                        f.write(body) 
                    print(f"File '{filename}' berhasil didownload sebagai '{filename}'")
                except Exception as e:
                    print(f"Error menyimpan file: {e}")
            else:
                print(f"Error dari server:\n{headers_str}")
        else:
            print("Response tidak valid")

    def list_files(self):
        request = "GET /list HTTP/1.0\r\n\r\n"
        response = self.send_request(request)
        
        if "200 OK" in response:
            parts = response.split('\r\n\r\n', 1)
            if len(parts) == 2:
                headers, body = parts
                print("=== DAFTAR FILE DI SERVER ===")
                print(body)
            else:
                print("Response tidak valid")
        else:
            print(f"Error: {response}")
            
    def upload_file(self, local_filename, server_filename=None):
        if not os.path.exists(local_filename):
            print(f"File '{local_filename}' tidak ditemukan")
            return
            
        if server_filename is None:
            server_filename = os.path.basename(local_filename)
            
        try:
            with open(local_filename, 'rb') as f:
                file_content = f.read()
                
            request = f"POST /upload?filename={server_filename} HTTP/1.0\r\n"
            request += f"Content-Length: {len(file_content)}\r\n"
            request += "\r\n"
            
            request_bytes = request.encode() + file_content
            
            response = self.send_request(request_bytes)
            
            if "200 OK" in response:
                print(f"File '{local_filename}' berhasil diupload sebagai '{server_filename}'")
            else:
                print(f"Error upload: {response}")
                
        except Exception as e:
            print(f"Error membaca file: {e}")
            
    def delete_file(self, filename):
        request = f"DELETE /delete/{filename} HTTP/1.0\r\n\r\n"
        response = self.send_request(request)
        
        if "200 OK" in response:
            print(f"File '{filename}' berhasil dihapus dari server")
        else:
            print(f"Error: {response}")
            
    def get_home(self):
        request = "GET / HTTP/1.0\r\n\r\n"
        response = self.send_request(request)
        print("=== RESPONSE DARI SERVER ===")
        print(response)
        
    def interactive_mode(self):
        print("=== HTTP CLIENT INTERAKTIF ===")
        print("Server:", f"{self.host}:{self.port}")
        print("\nPerintah yang tersedia:")
        print("1. list - Melihat daftar file")
        print("2. get <filename> - Download file")
        print("3. upload <local_file> [server_name] - Upload file")
        print("4. delete <filename> - Hapus file")
        print("5. quit - Keluar")
        
        while True:
            try:
                command = input("\n> ").strip().split()
                
                if not command:
                    continue
                    
                if command[0] == 'quit':
                    print("Selamat tinggal!")
                    break
                    
                elif command[0] == 'list':
                    self.list_files()
                    
                elif command[0] == 'get':
                    if len(command) < 2:
                        print("Usage: get <filename>")
                    else:
                        self.get_file(command[1])
                        
                elif command[0] == 'upload':
                    if len(command) < 2:
                        print("Usage: upload <local_file> [server_name]")
                    elif len(command) == 2:
                        self.upload_file(command[1])
                    else:
                        self.upload_file(command[1], command[2])
                        
                elif command[0] == 'delete':
                    if len(command) < 2:
                        print("Usage: delete <filename>")
                    else:
                        self.delete_file(command[1])
                    
                else:
                    print("Perintah tidak dikenal. Ketik 'quit' untuk keluar.")
                    
            except KeyboardInterrupt:
                print("\nSelamat tinggal!")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    if len(sys.argv) > 2:
        host = sys.argv[1]
        port = int(sys.argv[2])
        client = HttpClient(host, port)
    elif len(sys.argv) > 1:
        host = sys.argv[1]
        client = HttpClient(host)
    else:
        client = HttpClient()
        
    print(f"HTTP Client - Menghubungkan ke {client.host}:{client.port}")
    
    try:
        response = client.send_request("GET / HTTP/1.0\r\n\r\n")
        if "HTTP/1.0" in response:
            print("Koneksi berhasil!")
            client.interactive_mode()
        else:
            print("Server tidak merespons dengan benar")
            print("Pastikan server sudah berjalan")
    except Exception as e:
        print(f"Tidak dapat terhubung ke server: {e}")
        print("Pastikan server sudah berjalan di", f"{client.host}:{client.port}")

if __name__ == "__main__":
    main()