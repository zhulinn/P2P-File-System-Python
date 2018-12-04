import socket
import threading
import platform
import mimetypes
import os
import sys
import time
from pathlib import Path


class MyException(Exception):
    pass


class Client(object):
    def __init__(self, serverhost='localhost', V='P2P-CI/1.0', DIR='rfc'):
        self.SERVER_HOST = serverhost
        self.SERVER_PORT = 7734
        self.V = V
        self.DIR = 'rfc'  # file directory
        Path(self.DIR).mkdir(exist_ok=True)

        self.UPLOAD_PORT = None
        self.shareable = True

    def start(self):
        # connect to server
        print('Connecting to the server %s:%s' %
              (self.SERVER_HOST, self.SERVER_PORT))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.connect((self.SERVER_HOST, self.SERVER_PORT))
        except Exception:
            print('Server Not Available.')
            return

        print('Connected')
        # upload
        uploader_process = threading.Thread(target=self.init_upload)
        uploader_process.start()
        while self.UPLOAD_PORT is None:
            # wait until upload port is initialized
            pass
        print('Listening on the upload port %s' % self.UPLOAD_PORT)

        # interactive shell
        self.cli()

    def cli(self):
        command_dict = {'1': self.add,
                        '2': self.lookup,
                        '3': self.listall,
                        '4': self.pre_download,
                        '5': self.shutdown}
        while True:
            try:
                req = input('\n1: Add, 2: Look Up, 3: List All, 4: Download, 5: Shut Down\nEnter your request: ')
                command_dict.setdefault(req, self.invalid_input)()
            except MyException as e:
                print(e)
            except Exception:
                print('System Error.')
            except BaseException:
                self.shutdown()

    def init_upload(self):
        # listen upload port
        self.uploader = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.uploader.bind(('', 0))
        self.UPLOAD_PORT = self.uploader.getsockname()[1]
        self.uploader.listen(5)

        while self.shareable:
            requester, addr = self.uploader.accept()
            handler = threading.Thread(
                target=self.handle_upload, args=(requester, addr))
            handler.start()
        self.uploader.close()

    def handle_upload(self, soc, addr):
        header = soc.recv(1024).decode().splitlines()
        try:
            version = header[0].split()[-1]
            num = header[0].split()[-2]
            method = header[0].split()[0]
            path = '%s/rfc%s.txt' % (self.DIR, num)
            if version != self.V:
                soc.sendall(str.encode(
                    self.V + ' 505 P2P-CI Version Not Supported\n'))
            elif not Path(path).is_file():
                soc.sendall(str.encode(self.V + ' 404 Not Found\n'))
            elif method == 'GET':
                header = self.V + ' 200 OK\n'
                header += 'Data: %s\n' % (time.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))
                header += 'OS: %s\n' % (platform.platform())
                header += 'Last-Modified: %s\n' % (time.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(os.path.getmtime(path))))
                header += 'Content-Length: %s\n' % (os.path.getsize(path))
                header += 'Content-Type: %s\n' % (
                    mimetypes.MimeTypes().guess_type(path)[0])
                soc.sendall(header.encode())
                # Uploading
                try:
                    print('\nUploading...')

                    send_length = 0
                    with open(path, 'r') as file:
                        to_send = file.read(1024)
                        while to_send:
                            send_length += len(to_send.encode())
                            soc.sendall(to_send.encode())
                            to_send = file.read(1024)
                except Exception:
                    raise MyException('Uploading Failed')
                # total_length = int(os.path.getsize(path))
                # print('send: %s | total: %s' % (send_length, total_length))
                # if send_length < total_length:
                #     raise MyException('Uploading Failed')
                print('Uploading Completed.')
                # Restore CLI
                print(
                    '\n1: Add, 2: Look Up, 3: List All, 4: Download\nEnter your request: ')
            else:
                raise MyException('Bad Request.')
        except Exception:
            soc.sendall(str.encode(self.V + '  400 Bad Request\n'))
        finally:
            soc.close()

    def add(self, num=None, title=None):
        if not num:
            num = input('Enter the RFC number: ')
            if not num.isdigit():
                raise MyException('Invalid Input.')
            title = input('Enter the RFC title: ')
        file = Path('%s/rfc%s.txt' % (self.DIR, num))
        print(file)
        if not file.is_file():
            raise MyException('File Not Exit!')
        msg = 'ADD RFC %s %s\n' % (num, self.V)
        msg += 'Host: %s\n' % socket.gethostname()
        msg += 'Post: %s\n' % self.UPLOAD_PORT
        msg += 'Title: %s\n' % title
        self.server.sendall(msg.encode())
        res = self.server.recv(1024).decode()
        print('Recieve response: \n%s' % res)

    def lookup(self):
        num = input('Enter the RFC number: ')
        title = input('Enter the RFC title(optional): ')
        msg = 'LOOKUP RFC %s %s\n' % (num, self.V)
        msg += 'Host: %s\n' % socket.gethostname()
        msg += 'Post: %s\n' % self.UPLOAD_PORT
        msg += 'Title: %s\n' % title
        self.server.sendall(msg.encode())
        res = self.server.recv(1024).decode()
        print('Recieve response: \n%s' % res)

    def listall(self):
        l1 = 'LIST ALL %s\n' % self.V
        l2 = 'Host: %s\n' % socket.gethostname()
        l3 = 'Post: %s\n' % self.UPLOAD_PORT
        msg = l1 + l2 + l3
        self.server.sendall(msg.encode())
        res = self.server.recv(1024).decode()
        print('Recieve response: \n%s' % res)

    def pre_download(self):
        num = input('Enter the RFC number: ')
        msg = 'LOOKUP RFC %s %s\n' % (num, self.V)
        msg += 'Host: %s\n' % socket.gethostname()
        msg += 'Post: %s\n' % self.UPLOAD_PORT
        msg += 'Title: Unkown\n'
        self.server.sendall(msg.encode())
        lines = self.server.recv(1024).decode().splitlines()
        if lines[0].split()[1] == '200':
            # Choose a peer
            print('Available peers: ')
            for i, line in enumerate(lines[1:]):
                line = line.split()
                print('%s: %s:%s' % (i + 1, line[-2], line[-1]))

            try:
                idx = int(input('Choose one peer to download: '))
                title = lines[idx].rsplit(None, 2)[0].split(None, 2)[-1]
                peer_host = lines[idx].split()[-2]
                peer_port = int(lines[idx].split()[-1])
            except Exception:
                raise MyException('Invalid Input.')
            # exclude self
            if((peer_host, peer_port) == (socket.gethostname(), self.UPLOAD_PORT)):
                raise MyException('Do not choose yourself.')
            # send get request
            self.download(num, title, peer_host, peer_port)
        elif lines[0].split()[1] == '400':
            raise MyException('Invalid Input.')
        elif lines[0].split()[1] == '404':
            raise MyException('File Not Available.')
        elif lines[0].split()[1] == '500':
            raise MyException('Version Not Supported.')

    def download(self, num, title, peer_host, peer_port):
        try:
            # make connnection
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect_ex return errors
            if soc.connect_ex((peer_host, peer_port)):
                # print('Try Local Network...')
                # if soc.connect_ex(('localhost', peer_port)):
                raise MyException('Peer Not Available')
            # make request
            msg = 'GET RFC %s %s\n' % (num, self.V)
            msg += 'Host: %s\n' % socket.gethostname()
            msg += 'OS: %s\n' % platform.platform()
            soc.sendall(msg.encode())

            # Downloading

            header = soc.recv(1024).decode()
            print('Recieve response header: \n%s' % header)
            header = header.splitlines()
            if header[0].split()[-2] == '200':
                path = '%s/rfc%s.txt' % (self.DIR, num)
                print('Downloading...')
                try:
                    with open(path, 'w') as file:
                        content = soc.recv(1024)
                        while content:
                            file.write(content.decode())
                            content = soc.recv(1024)
                except Exception:
                    raise MyException('Downloading Failed')

                total_length = int(header[4].split()[1])
                # print('write: %s | total: %s' % (os.path.getsize(path), total_length))

                if os.path.getsize(path) < total_length:
                    raise MyException('Downloading Failed')

                print('Downloading Completed.')
                # Share file, send ADD request
                print('Sending ADD request to share...')
                if self.shareable:
                    self.add(num, title)
            elif header[0].split()[1] == '400':
                raise MyException('Invalid Input.')
            elif header[0].split()[1] == '404':
                raise MyException('File Not Available.')
            elif header[0].split()[1] == '500':
                raise MyException('Version Not Supported.')
        finally:
            soc.close()
            # Restore CLI
          #  print('\n1: Add, 2: Look Up, 3: List All, 4: Download\nEnter your request: ')

    def invalid_input(self):
        raise MyException('Invalid Input.')

    def shutdown(self):
        print('\nShutting Down...')
        self.server.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        client = Client(sys.argv[1])
    else:
        client = Client()
    client.start()
