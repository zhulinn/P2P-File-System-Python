# Author
- Lin Zhu lzhu15@ncsu.edu
- Huiming Yang hyang26@ncsu.edu

# Enviroment
- Python 3.7.0(3.5+)

# Instruction
This system includes all the features and functionalities described in the requirements. There are two .py files in the root directory, `server.py` and `client.py`. They are used to start the applications for server and peers accordingly. The `testing-files` directory contains some text files for testing. Each client has his/her own storage space. **If you are testing multiple clients on a single machine, the `client.py` file should be copyed to several different directory to simulate real situation.**

# How to Run
1. Setup Server
Run `server.py` directly.
```
python server.py
```

2. Simulate Clients
Each `client.py` starts an application for one client. To run mulpiple clients, copy `client.py` to different directory. Server's host is optional. It will be `localhost` by default.  It will generate an empty directory `rfc` to store this client's file. Put several RFC files under this directory, which means that this client has those RFC files stored in his/her computer.
```
python client.py [server host]
```

# Command Line Interface
- At server's end, it shows recieved requests and the server's status. No need for input.
- At client's end, it has an operation menu for the client to interact with. Simplely enter the No. of the choice.