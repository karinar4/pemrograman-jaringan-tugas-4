import socket
import logging
import ssl
import os

server_address = ('172.16.16.101', 8885)

def make_socket(destination_address='localhost', port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def make_secure_socket(destination_address='localhost', port=10000):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.load_verify_locations(os.getcwd() + '/domain.crt')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock, server_hostname=destination_address)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def send_command(command_str, is_secure=False):
    alamat_server = server_address[0]
    port_server = server_address[1]
    if is_secure:
        sock = make_secure_socket(alamat_server, port_server)
    else:
        sock = make_socket(alamat_server, port_server)

    try:
        sock.sendall(command_str.encode())
        data_received = ""
        while True:
            data = sock.recv(2048)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        return data_received
    except Exception as ee:
        logging.warning(f"error during data receiving {str(ee)}")
        return "ERROR"

def list_files():
    response = send_command("GET /list HTTP/1.0\r\n\r\n")
    if "200 OK" in response:
        print("=== DAFTAR FILE DI SERVER ===")
        print(response.split("\r\n\r\n", 1)[1])
    else:
        print("Gagal mendapatkan daftar file")

def get_file(filename):
    response = send_command(f"GET /{filename} HTTP/1.0\r\n\r\n")
    if "200 OK" in response:
        parts = response.split("\r\n\r\n", 1)
        if len(parts) == 2:
            headers, body = parts
            with open(filename, 'wb') as f:
                f.write(body.encode('latin1'))  # agar bisa menyimpan byte
            print(f"File '{filename}' berhasil didownload")
        else:
            print("Response tidak valid")
    else:
        print(f"Gagal download: {response}")

def upload_file(local_filename, server_filename=None):
    if not os.path.exists(local_filename):
        print(f"File '{local_filename}' tidak ditemukan")
        return
    if server_filename is None:
        server_filename = os.path.basename(local_filename)
    with open(local_filename, 'rb') as f:
        file_content = f.read()
    request = f"POST /upload?filename={server_filename} HTTP/1.0\r\n"
    request += f"Content-Length: {len(file_content)}\r\n\r\n"
    response = send_command((request.encode() + file_content).decode('latin1'))
    if "200 OK" in response:
        print(f"File '{local_filename}' berhasil diupload")
    else:
        print("Gagal upload:", response)

def delete_file(filename):
    response = send_command(f"DELETE /delete/{filename} HTTP/1.0\r\n\r\n")
    if "200 OK" in response:
        print(f"File '{filename}' berhasil dihapus")
    else:
        print("Gagal menghapus file:", response)

def interactive_mode():
    print("=== HTTP CLIENT INTERAKTIF ===")
    print("Server:", f"{server_address[0]}:{server_address[1]}")
    print("\nPerintah yang tersedia:")
    print("1. list - Melihat daftar file")
    print("2. get <filename> - Download file")
    print("3. upload <local_file> [server_name] - Upload file")
    print("4. delete <filename> - Hapus file")
    print("5. quit - Keluar")

    while True:
        try:
            cmd = input("> ").strip().split()
            if not cmd:
                continue
            if cmd[0] == 'quit':
                break
            elif cmd[0] == 'list':
                list_files()
            elif cmd[0] == 'get':
                if len(cmd) < 2:
                    print("Gunakan: get <filename>")
                else:
                    get_file(cmd[1])
            elif cmd[0] == 'upload':
                if len(cmd) < 2:
                    print("Gunakan: upload <local_file> [remote_name]")
                else:
                    upload_file(cmd[1], cmd[2] if len(cmd) > 2 else None)
            elif cmd[0] == 'delete':
                if len(cmd) < 2:
                    print("Gunakan: delete <filename>")
                else:
                    delete_file(cmd[1])
            else:
                print("Perintah tidak dikenali")
        except KeyboardInterrupt:
            print("\nKeluar.")
            break

def main():
    print(f"HTTP Client - Menghubungkan ke {server_address[0]}:{server_address[1]}")
    try:
        response = send_command("GET / HTTP/1.0\r\n\r\n")
        if "HTTP/1.0" in response:
            print("Koneksi berhasil!")
            interactive_mode()
        else:
            print("Server tidak merespons dengan benar")
    except Exception as e:
        print("Gagal terhubung ke server:", e)

if __name__ == "__main__":
    main()