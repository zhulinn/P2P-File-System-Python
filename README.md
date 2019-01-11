# Peer-to-Peer with Centralized Index (P2P-CI) System

Internet protocol standards are defined in documents called “Requests for Comments” (RFCs). RFCs are available for download from the IETF web site (http://www.ietf.org/). Rather than using this centralized server for downloading RFCs, you will build a P2P-CI system in which peers who wish to download an RFC that they do not have in their hard drive, may download it from another active peer who does. All communication among peers or between a peer and the server will take place over TCP. 
Specifically, the P2P-CI system will operate as follows.

- There is a centralized server, running on a well-known host and listening on a well-known port, which keeps information about the active peers and maintains an index of the RFCs available at each active peer.
When a peer decides to join the P2P-CI system, it opens a connection to the server to register itself and provide information about the RFCs that it makes available to other peers. This connection remains open as long as the peer remains active; the peer closes the connection when it leaves the system (becomes inactive).
Since the server may have connections open to multiple peers simultaneously, it spawns a new process to handle the communication to each new peer.
- When a peer wishes to download a specific RFC, it provides the RFC number to the server over the open connection, and in response the server provides the peer with a list of other peers who have the RFC; if no such active peer exists, an appropriate message is transmitted to the requesting peer. Additionally, each peer may at any point query the server to obtain the whole index of RFCs available at all other active peers.
- Each peer runs a upload server process that listens on a port specific to the peer ; in other words, this port is not known in advance to any of the peers. When a peer A needs to download an RFC from a peer B, it opens a connection to the upload port of peer B, provides the RFC number to B, and B responds by sending the (text) file containing the RFC to A over the same connection; once the file transmission is completed, the connection is closed.

# Enviroment
- Python 3.7.0(3.5+)

# Instruction
This system includes all the features and functionalities described in the requirements. There are two .py files in the root directory, `server.py` and `client.py`. They are used to start the applications for server and peers accordingly. The `testing-files` directory contains some text files for testing. Each client has his/her own storage space. **If you are testing multiple clients on a single machine, the `client.py` file should be copyed to several different directory to simulate real situation.**

# How to Run
1. Setup Server
Run `server.py` directly. `Ctrl + C` to shutting down the server.
```
python server.py
```

2. Simulate Clients
Each `client.py` starts an application for one client. To run mulpiple clients, copy `client.py` to different directory. Server's host is optional. It will be `localhost` by default.  It will generate an empty directory `rfc` to store this client's file. Put several RFC files under this directory, which means that this client has those RFC files stored in his/her computer.
```
python client.py [server host]
```
If you are runing the server on AWS, input it's public IP as server host. For example, if you have a Linux instance running on 13.25.100.100, run like this:
```
python client.py 13.25.100.100
```
# Command Line Interface
- At server's end, it shows recieved requests and the server's status. No need for input.
- At client's end, it has an operation menu for the client to interact with. Simplely enter the No. of the choice.
