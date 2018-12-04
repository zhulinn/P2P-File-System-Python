import socket
import threading
import os
import sys
from collections import defaultdict


class Server(object):
    def __init__(self, HOST='', PORT=7734, V='P2P-CI/1.0'):
        self.HOST = HOST
        self.PORT = PORT
        self.V = V
        # element: {(host,port), set[rfc #]}
        self.peers = defaultdict(set)
        # element: {RFC #, (title, set[(host, port)])}
        self.rfcs = {}
        self.lock = threading.Lock()

    # start listenning
    def start(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.HOST, self.PORT))
            self.s.listen(5)
            print('Server %s is listening on port %s' %
                  (self.V, self.PORT))

            while True:
                soc, addr = self.s.accept()
                print('%s:%s connected' % (addr[0], addr[1]))
                thread = threading.Thread(
                    target=self.handler, args=(soc, addr))
                thread.start()
        except KeyboardInterrupt:
            print('\nShutting down the server..\nGood Bye!')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)

    # connect with a client
    def handler(self, soc, addr):
        # keep recieve request from client
        host = None
        port = None
        while True:
            try:
                req = soc.recv(1024).decode()
                print('Recieve request:\n%s' % req)
                lines = req.splitlines()
                version = lines[0].split()[-1]
                if version != self.V:
                    soc.sendall(str.encode(
                        self.V + ' 505 P2P-CI Version Not Supported\n'))
                else:
                    method = lines[0].split()[0]
                    if method == 'ADD':
                        host = lines[1].split(None, 1)[1]
                        port = int(lines[2].split(None, 1)[1])
                        num = int(lines[0].split()[-2])
                        title = lines[3].split(None, 1)[1]
                        self.addRecord(soc, (host, port), num, title)
                    elif method == 'LOOKUP':
                        num = int(lines[0].split()[-2])
                        self.getPeersOfRfc(soc, num)
                    elif method == 'LIST':
                        self.getAllRecords(soc)
                    else:
                        raise AttributeError('Method Not Match')
            except ConnectionError:
                print('%s:%s left' % (addr[0], addr[1]))
                # Clean data if necessary
                if host and port:
                    self.clear(host,port)
                soc.close()
                break
            except BaseException:
                try:
                    soc.sendall(str.encode(self.V + '  400 Bad Request\n'))
                except ConnectionError:
                    print('%s:%s left' % (addr[0], addr[1]))
                    # Clean data if necessary
                    if host and port:
                        self.clear(host,port)
                    soc.close()
                    break

    def clear(self, host, port):
        self.lock.acquire()
        nums = self.peers[(host, port)]
        for num in nums:
            self.rfcs[num][1].discard((host, port))
        if not self.rfcs[num][1]:
            self.rfcs.pop(num, None)
        self.peers.pop((host, port), None)
        self.lock.release()

    def addRecord(self, soc, peer, num, title):
        self.lock.acquire()
        try:
            self.peers[peer].add(num)
            self.rfcs.setdefault(num, (title, set()))[1].add(peer)
        finally:
            self.lock.release()
        # print(self.rfcs)
        # print(self.peers)
        header = self.V + ' 200 OK\n'
        header += 'RFC %s %s %s %s\n' % (num,
                                         self.rfcs[num][0], peer[0], peer[1])
        soc.sendall(str.encode(header))

    def getPeersOfRfc(self, soc, num):
        self.lock.acquire()
        try:
            if num not in self.rfcs:
                header = self.V + ' 404 Not Found\n'
            else:
                header = self.V + ' 200 OK\n'
                title = self.rfcs[num][0]
                for peer in self.rfcs[num][1]:
                    header += 'RFC %s %s %s %s\n' % (num,
                                                     title, peer[0], peer[1])
        finally:
            self.lock.release()
        soc.sendall(str.encode(header))

    def getAllRecords(self, soc):
        self.lock.acquire()
        try:
            if not self.rfcs:
                header = self.V + ' 404 Not Found\n'
            else:
                header = self.V + ' 200 OK\n'
                for num in self.rfcs:
                    title = self.rfcs[num][0]
                    for peer in self.rfcs[num][1]:
                        header += 'RFC %s %s %s %s\n' % (num,
                                                         title, peer[0], peer[1])
        finally:
            self.lock.release()
        soc.sendall(str.encode(header))


if __name__ == '__main__':
    s = Server()

    s.start()
