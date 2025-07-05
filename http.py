import sys
import os.path
import uuid
from glob import glob
from datetime import datetime
import urllib.parse

class HttpServer:
    def __init__(self):
        self.sessions={}
        self.types={}
        self.types['.pdf']='application/pdf'
        self.types['.jpg']='image/jpeg'
        self.types['.jpeg']='image/jpeg'
        self.types['.txt']='text/plain'
        self.types['.html']='text/html'
        self.types['.png']='image/png'
        self.types['.gif']='image/gif'
        self.types['.bmp']='image/bmp'
        self.types['.webp']='image/webp'
        
    def response(self,kode=404,message='Not Found',messagebody=bytes(),headers={}):
        tanggal = datetime.now().strftime('%c')
        resp=[]
        resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
        resp.append("Date: {}\r\n" . format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n" . format(kk,headers[kk]))
        resp.append("\r\n")
        response_headers=''
        for i in resp:
            response_headers="{}{}" . format(response_headers,i)
            
        if (type(messagebody) is not bytes):
            messagebody = messagebody.encode()
        response = response_headers.encode() + messagebody

        return response
        
    def proses(self, data):
        if isinstance(data, bytes):
            original_data = data
            data_str = data.decode('utf-8', errors='ignore')
        else:
            data_str = data
            original_data = data.encode()
        
        if "\r\n\r\n" in data_str:
            header_part, body_part = data_str.split("\r\n\r\n", 1)
            if isinstance(original_data, bytes):
                header_bytes = header_part.encode() + b"\r\n\r\n"
                body_bytes = original_data[len(header_bytes):]
            else:
                body_bytes = body_part.encode()
        else:
            header_part = data_str
            body_bytes = b""
            
        requests = header_part.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n!='']
        
        headers_dict = {}
        for header in all_headers:
            if ':' in header:
                key, value = header.split(':', 1)
                headers_dict[key.strip().lower()] = value.strip()
        
        j = baris.split(" ")
        try:
            method=j[0].upper().strip()
            if (method=='GET'):
                object_address = j[1].strip()
                return self.http_get(object_address, all_headers)
            elif (method=='POST'):
                object_address = j[1].strip()
                return self.http_post(object_address, all_headers, body_bytes, headers_dict)
            elif (method=='DELETE'):
                object_address = j[1].strip()
                return self.http_delete(object_address, all_headers)
            else:
                return self.response(400,'Bad Request','',{})
        except IndexError:
            return self.response(400,'Bad Request','',{})
            
    def http_get(self,object_address,headers):
        files = glob('./*')
        thedir='./'
        
        if (object_address == '/'):
            return self.response(200,'OK','Ini Adalah web Server percobaan',dict())
        if (object_address == '/video'):
            return self.response(302,'Found','',dict(location='https://youtu.be/katoxpnTf04'))
        if (object_address == '/santai'):
            return self.response(200,'OK','santai saja',dict())
            
        if (object_address == '/list'):
            return self.list_files()
            
        if object_address.startswith('/'):
            file_path = object_address[1:] 
        else:
            file_path = object_address
            
        full_path = thedir + file_path
        
        if full_path not in files:
            return self.response(404,'Not Found','File tidak ditemukan',{})
            
        try:
            fp = open(full_path,'rb')
            isi = fp.read()
            fp.close()
            
            fext = os.path.splitext(full_path)[1].lower()
            content_type = self.types.get(fext, 'application/octet-stream')
            
            headers={}
            headers['Content-type']=content_type
            
            return self.response(200,'OK',isi,headers)
        except Exception as e:
            return self.response(500,'Internal Server Error',f'Error membaca file: {str(e)}',{})
            
    def http_post(self, object_address, headers, body_bytes, headers_dict):
        if object_address.startswith('/upload'):
            return self.upload_file(object_address, headers, body_bytes, headers_dict)
            
        headers ={}
        isi = "kosong"
        return self.response(200,'OK',isi,headers)
        
    def http_delete(self, object_address, headers):
        if object_address.startswith('/delete/'):
            filename = object_address[8:] 
            return self.delete_file(filename)
        else:
            return self.response(400,'Bad Request','Format DELETE salah. Gunakan /delete/namafile',{})
            
    def list_files(self):
        try:
            files = glob('./*')
            file_list = []
            
            for file_path in files:
                if os.path.isfile(file_path):
                    filename = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    file_ext = os.path.splitext(filename)[1].lower()
                    file_type = self.types.get(file_ext, 'unknown')
                    file_list.append(f"{filename} ({file_size} bytes) - {file_type}")
                    
            if file_list:
                content = "Daftar File:\n" + "\n".join(file_list)
            else:
                content = "Tidak ada file dalam direktori"
                
            headers = {'Content-type': 'text/plain'}
            return self.response(200, 'OK', content, headers)
            
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Error listing files: {str(e)}', {})
            
    def upload_file(self, object_address, headers, body_bytes, headers_dict):
        try:
            filename = ""
            
            if '?' in object_address:
                query_part = object_address.split('?')[1]
                params = urllib.parse.parse_qs(query_part)
                if 'filename' in params:
                    filename = params['filename'][0]
            elif object_address.startswith('/upload/'):
                filename = object_address[8:] 
                    
            if not filename:
                return self.response(400, 'Bad Request', 'Nama file tidak ditemukan. Gunakan /upload?filename=namafile.jpg atau /upload/namafile.jpg', {})
                
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in self.types:
                return self.response(400, 'Bad Request', f'Tipe file {file_ext} tidak didukung', {})
                
            with open(filename, 'wb') as f:
                f.write(body_bytes)
                    
            file_size = len(body_bytes)
            content = f"File '{filename}' berhasil diupload ({file_size} bytes)"
            headers = {'Content-type': 'text/plain'}
            return self.response(200, 'OK', content, headers)
            
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Error uploading file: {str(e)}', {})
            
    def delete_file(self, filename):
        try:
            if not filename:
                return self.response(400, 'Bad Request', 'Nama file tidak boleh kosong', {})
                
            file_path = './' + filename
            
            if not os.path.exists(file_path):
                return self.response(404, 'Not Found', f'File "{filename}" tidak ditemukan', {})
                
            if not os.path.isfile(file_path):
                return self.response(400, 'Bad Request', f'"{filename}" bukan file', {})
                
            os.remove(file_path)
            content = f'File "{filename}" berhasil dihapus'
            headers = {'Content-type': 'text/plain'}
            return self.response(200, 'OK', content, headers)
            
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Error deleting file: {str(e)}', {})

# Test functions
if __name__=="__main__":
    httpserver = HttpServer()
    
    d = httpserver.proses('GET testing.txt HTTP/1.0\r\n\r\n')
    print(d)
    
    print("\n=== Test LIST files ===")
    d = httpserver.proses('GET /list HTTP/1.0\r\n\r\n')
    print(d)