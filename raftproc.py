import socket
import threading
import struct
import time

class raftProc:
    def __init__(self, id, port, peers):
        self.id = id
        self.port = port
        self.peers = peers
        
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('localhost', self.port))
        self.server_sock.listen(1)

        self.recv_thread = threading.Thread(target=self.recv_messages)
        self.recv_thread.start()

    # add a new peer to the list of peers
    def add_peer(self, peer):
        # check if the peer is already in the list of peers
        if peer in self.peers:
            raise Exception('Peer already in the list of peers')
        # check if the peer is the current process
        if peer == self.port:
            raise Exception('Peer is the current process')
        # add the peer to the list of peers
        self.peers.append(peer)
    
    # remove a peer from the list of peers
    def remove_peer(self, peer):
        # check if the peer is in the list of peers
        if peer not in self.peers:
            raise Exception('Peer not in the list of peers')
        # check if the peer is the current process
        if peer == self.port:
            raise Exception('Peer is the current process')
        # remove the peer from the list of peers
        self.peers.remove(peer)
    
    def send_message(self, dest_port, message):
        # check if the peer is in the list of peers
        if dest_port not in self.peers:
            raise Exception('Peer not in the list of peers')
        # check if port is available, if not, wait for 1 second and try again
        # if connection is done, send the message
        # set a maximum number of attempts to connect to the peer
        max_attempts = 5
        while max_attempts > 0:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('localhost', dest_port))
                message_bytes = struct.pack('>i', self.port) + message.encode('utf-8')
                sock.sendall(message_bytes)
                print(f"Sent message to {dest_port}: {message}")
                sock.close()
                break
            except:
                time.sleep(1)
                max_attempts -= 1

    def recv_messages(self):
        while True:
            client_sock, client_addr = self.server_sock.accept()
            message_bytes = client_sock.recv(1024)
            sender_port = struct.unpack('>i', message_bytes[:4])[0]
            message = message_bytes[4:].decode('utf-8')
            print(f"Received message from {sender_port}: {message}")
            # add return statement as requrired here

            client_sock.close()
