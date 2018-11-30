import socket
import threading
from collections import defaultdict



class Server(object):
    def __init__(self, HOST='localhost', PORT=7734, V='P2P-CI/1.0'):
        self.HOST = HOST
        self.PORT = PORT
        self.V = V
        # element: {(host,port), set[rfc #]}
        self.peers = defaultdict(set)
        # element: {RFC #, (title, set[(host, port)])}
        self.rfcs = {}
        self.lock = threading.Lock()
    
    #start listenning
    def start(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.HOST, self.PORT))
        self.s.listen(5)
        print('Server %s on %s:%s is listening' % (self.V, self.HOST, self.PORT))
        while True:
            soc, addr = self.s.accept()
            print(addr)
            thread = threading.Thread(target=self.connect, args=soc)
            thread.start()

    #connect with a client
    def connect(self, soc):
        req = soc.recv(1024)
        lines = req.splitlines()
        version = lines[0].split()[-1]
        if version != self.V:
            soc.sendall(self.V + ' 505 P2P-CI Version Not Supported\n')
        else:
            method = lines[0].split()[0]
            num = lines[0].split()[-2]
            host = lines[1].split(None, 1)
            port = int(lines[2].split(None, 1))
            title = lines[3].split(None, 1)
            
            if method == 'ADD':
                self.addRecord(soc, (host, port), num, title)
            elif method == 'LOOKUP':
                self.getPeersOfRfc(soc, num)
            elif method == 'LIST':
                self.getAllRecords(soc)
            else:
                soc.sendall(self.V + '  400 Bad Request\n')
        soc.close()

    def addRecord(self, soc, peer, num, title):
        self.lock.acquire()
        try:
            self.peers[peer].add(num)
            self.rfcs.setdefault(num,(title, set()))[1].add(peer)
        finally:
            self.lock.release()
        header = V + ' 200 OK\n'
        header += 'RFC %s %s %s %s\n' % (num, title, peer[0], peer[1])
        soc.sendall(header)
    
    def getPeersOfRfc(self, soc, num):
        self.lock.acquire()
        try:
            if num not in self.rfcs:
                header = self.V + ' 404 Not Found\n'
            else:
                header = self.V + ' 200 OK\n'
                title = self.rfcs[num][0]
                for peer in self.rfcs[num][1]:
                    header += 'RFC %s %s %s %s\n' & (num, title, peer[0], peer[1])
        finally:
            self.lock.release()
        soc.sendall(header)

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
                        header += 'RFC %s %s %s %s\n' & (num, title, peer[0], peer[1])
        finally:
            self.lock.release()
        soc.sendall(header)

if __name__ == '__main__':
    s = Server()
    s.start()
