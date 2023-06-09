import socket
import threading
import struct
import time
import ast
import requests
from pysyncobj import SyncObj, SyncObjConf, replicated_sync
import os

from requests.exceptions import Timeout
from requests.exceptions import ConnectionError
# import broker_manager
# from assign2.utility_funcs import get_link

def get_link(port:int) -> str:
    base = "http://127.0.0.1:"
    base += str(port)
    # base += "/"
    return base

class raftProc:
    def __init__(self, id, port, broker):
        self.id = id
        self.port = port
        self.broker = broker
        self.raftObjects = {}

        # call url of broker to get the information about the topics and partitions
        newLink = get_link(self.broker) + "/get_data"
        _params = {}
        try:
            resp = requests.get(newLink, json = _params, data = _params, timeout = 2)
            # do whatever you want with the response
            for partitions in resp.json()['data']:
                peers = [partitions['peer1'], partitions['peer2']]
                topic_name = partitions['topic']
                partition_id = partitions['partition_id']
                key = str(topic_name) + "_" + str(partition_id)
                msg_dict = {'peers': peers, 'port': partitions['port']}
                self.add_topic(key, msg_dict)
        except Exception as e:
            # print(e.message, e.args)
            print("The request timed out: Broker "+str(self.broker)+" is not responding !")
            # os._exit()
        
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('0.0.0.0', self.port))
        self.server_sock.listen(1)

        # send a message to all peers to add this process to their list of peers
        # message is a blank dictionary
        # message = {}
        # encode the message as a string
        # message_str = str(message)
        # send the message to all peers
        # self.broadcast(message_str, 4)

        self.recv_thread = threading.Thread(target=self.recv_messages)
        self.recv_thread.start()

        # thread for checking if the broker is alive
        self.broker_thread = threading.Thread(target=self.check_broker)
        self.broker_thread.start()

    # check if the broker is alive
    def check_broker(self):
        while True:
            newLink = get_link(self.broker) + "/health"
            # print(newLink)
            _params = {}
            try:
                resp = requests.post(newLink, json = _params, data = _params, timeout = 2)
                time.sleep(15)
            except requests.exceptions.Timeout:
                print("The request timed out: Broker "+str(self.broker)+" is not responding !")
                os._exit(1)

    # add a new peer to the list of peers
    def add_peer(self, peer):
        # check if the peer is already in the list of peers
        if peer in self.peers:
            raise Exception('Peer already in the list of peers')
        # check if the peer is the current process
        if peer == self.port:
            raise Exception('Peer is the current process')
        # check if the peer is the broker
        if peer == self.broker:
            raise Exception('Peer is the broker')
        # add the peer to the list of peers
        self.peers.append(peer)
    
    # remove a peer from the list of peers
    # def remove_peer(self, peer):
    #     # check if the peer is in the list of peers
    #     if peer not in self.peers:
    #         raise Exception('Peer not in the list of peers')
    #     # check if the peer is the current process
    #     if peer == self.port:
    #         raise Exception('Peer is the current process')
    #     # check if the peer is the broker
    #     if peer == self.broker:
    #         raise Exception('Peer is the broker')
    #     # remove the peer from the list of peers
    #     self.peers.remove(peer)
    
    # handle enqueue request from a broker
    def enqueue(self, key, message):
        # message is a dictionary with the following keys:
        #  - topic: the topic to which the message is to be enqueued
        #  - message: the message to be enqueued
        #  - partition_id: the partition to which the message is to be enqueued
        # convert the message to a string
        # message_str = str(message)
        # send the message to all peers
        self.raftObjects[key].enqueue(message)
    
    # handle dequeue request from a broker
    def dequeue(self, key, message):
        # message is a dictionary with the following keys:
        #  - topic: the topic from which the message is to be dequeued
        #  - partition_id: the partition from which the message is to be dequeued
        #  - consumer_id: the consumer that is requesting the message
        # convert the message to a string
        # message_str = str(message)
        # send the message to all peers
        resp = self.raftObjects[key].dequeue(message)
        return resp.json()['message']
    
    # handle adding a consumer from a broker
    def add_consumer(self, key, message):
        self.raftObjects[key].add_consumer(message)

    # handle adding a topic from a broker
    def add_topic(self, key, message):
        selfport = "localhost:" + str(message['port'])
        peerports = []
        for x in message['peers']:
            peerports.append("localhost:" + str(x))
        self.raftObjects[key] = raftObj(selfport,peerports, self.broker)
        print("raft object created for topic: " + key)
        # self.raftObjects[key].add_topic(message)

        print("Adding topic")
        topic = message['topic']
        partition_id = message['partition_id']
        newLink = get_link(self.broker) + "/topics" #Link for adding a topic
        _params = {"topic_name":topic, "partition_no" : partition_id}
        requests.post(newLink, json = _params, data = _params)

        return "success"

    # send a message to all peers
    # boolean flag to indicate if the message is enqueue or dequeue
    # def broadcast(self, message, flag):
    #     for peer in self.peers:
    #         self.send_message(peer, message, flag)

    # send a message to a peer
    # flag to indicate if the message is enqueue, dequeue, add consumer, or add topic
    # def send_message(self, dest_port, message, flag):
    #     # check if the peer is in the list of peers
    #     if dest_port not in self.peers:
    #         raise Exception('Peer not in the list of peers')
    #     # check if port is available, if not, wait for 1 second and try again
    #     # if connection is done, send the message
    #     # set a maximum number of attempts to connect to the peer
    #     max_attempts = 5
    #     while max_attempts > 0:
    #         try:
    #             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #             sock.connect(('localhost', dest_port))
    #             # add flag to the message
    #             message = str(flag) + message
    #             message_bytes = struct.pack('>i', self.port) + message.encode('utf-8')
    #             sock.sendall(message_bytes)
    #             print(f"Sent message to {dest_port}: {message}")
    #             sock.close()
    #             break
    #         except:
    #             time.sleep(1)
    #             max_attempts -= 1

    def recv_messages(self):
        while True:
            client_sock, client_addr = self.server_sock.accept()
            with client_sock:
                message_bytes = client_sock.recv(1024)
                sender_port = struct.unpack('>i', message_bytes[:4])[0]
                print(sender_port)
                # if the message is from the broker, handle it
                if sender_port == self.broker:
                    resp = self.handle_broker_message(message_bytes)
                    if resp is not None:
                        # encode the response to bytes
                        print("Sending response to broker: " + str(resp))
                        resp = resp.encode('utf-8')
                        # send to tcp port 5050
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect(('localhost', 5050))
                        sock.sendall(resp)
                        sock.close()
                        # client_sock.sendall(resp)
            # if the message is from a peer, handle it
            client_sock.close()

    def handle_broker_message(self, message_bytes):
        # check if the message is enqueue or dequeue
        flag = int(message_bytes[4:5])
        message = message_bytes[5:].decode('utf-8')
        message = ast.literal_eval(message)
        topic_name = message['topic']
        partition_id = message['partition_id']
        key = str(topic_name) + "_" + str(partition_id)
        if flag == 0:
            # enqueue
            self.enqueue(key,message)
        elif flag == 1:
            # dequeue
            return self.dequeue(key,message)
        elif flag == 2:
            # add consumer
            self.add_consumer(key,message)
        elif flag == 3:
            # add topic
            return self.add_topic(key,message)
        return None

    # def handle_peer_message(self, message_bytes):
    #     # check if the message is from a peer
    #     sender_port = struct.unpack('>i', message_bytes[:4])[0]
    #     if sender_port not in self.peers:
    #         print('Message not from a peer')
    #     else:
    #         # decode the message
    #         message = message_bytes[4:].decode('utf-8')
    #         # check if the message is enqueue or dequeue
    #         flag = int(message[0])
    #         message = message[1:]
    #         # convert the message to a dictionary
    #         message = ast.literal_eval(message)
    #         if flag == 0:
    #             # enqueue
    #             topic_name = message['topic']
    #             partition_id = message['partition_id']
    #             message = message['message']
    #             newLink = get_link(self.broker) + "/producer/produce" #Link for publishing to the specific partition of a particular topic 
    #             _params = {"topic_name" : topic_name, "partition_no" : partition_id, "message" : message}
    #             # print(_params)
    #             requests.post(newLink, data = _params, json = _params, params = _params)

    #         elif flag == 1:
    #             # dequeue
    #             topic_name = message['topic']
    #             partition_id = message['partition_id']
    #             consumer_id = message['consumer_id']
    #             newLink = get_link(self.broker) + "/consumer/consume" #Link for consuming from the specific partition of a particular topic
    #             _params = {"topic_name" : topic_name, "partition_no" : partition_id, "consumer_id" : consumer_id}
    #             # print(_params)
    #             requests.get(newLink, data = _params, json = _params, params = _params)

    #         elif flag == 2:
    #             # add consumer
    #             topic_name = message['topic']
    #             consumer_id = message['consumer_id']
    #             partition_id = message['partition_id']
    #             newLink = get_link(self.broker) + "/consumer/register" #Link for adding a consumer to a particular topic
    #             _params = {"topic_name" : topic_name, "consumer_id": consumer_id}
    #             requests.post(newLink, data = _params, json = _params, params = _params)

    #         elif flag == 3:
    #             # add topic
    #             topic_name = message['topic']
    #             partition_id = message['partition_id']
    #             port = message['port']
    #             peers = message['peers']
    #             newLink = get_link(self.broker) + "/topics" #Link for adding a topic
    #             _params = {"topic_name":topic_name, "partition_no" : partition_id, "port" : port, "peers" : peers}
    #             requests.post(newLink, json = _params, data = _params)

    #         elif flag == 4:
    #             # add port to peer list
    #             port = sender_port
    #             self.add_peer(port)

    #         print(f"Received message from {sender_port}: {message}")
    #         # add return statement as requrired here

    #         client_sock.close()




class raftObj(SyncObj):
    def __init__(self, selfNodeAddr, otherNodeAddrs, brokerPort):
        super(raftObj, self).__init__(selfNodeAddr, otherNodeAddrs)
        self.brokerPort = brokerPort
    
    @replicated_sync
    def enqueue(self,message):
        topic = message['topic']
        partition_id = message['partition_id']
        message = message['message']
        newLink = get_link(self.brokerPort) + "/producer/produce" #Link for publishing to the specific partition of a particular topic 
        _params = {"topic_name" : topic, "partition_no" : partition_id, "message" : message}
        # print(_params)
        requests.post(newLink, data = _params, json = _params, params = _params)
    
    @replicated_sync
    def dequeue(self, message):
        topic = message['topic']
        partition_id = message['partition_id']
        consumer_id = message['consumer_id']
        newLink = get_link(self.brokerPort) + "/consumer/consume" #Link for consuming from the specific partition of a particular topic
        _params = {"topic_name" : topic, "partition_no" : partition_id, "consumer_id" : consumer_id}
        return requests.get(newLink, data = _params, json = _params, params = _params)
    
    @replicated_sync
    def add_consumer(self, message):
        topic = message['topic']
        consumer_id = message['consumer_id']
        newLink = get_link(self.brokerPort) + "/consumer/register" #Link for adding a consumer to a particular topic
        _params = {"topic_name" : topic, "consumer_id": consumer_id}
        requests.post(newLink, data = _params, json = _params, params = _params)
    
    @replicated_sync
    def add_topic(self, message):
        print("Adding topic")
        topic = message['topic']
        partition_id = message['partition_id']
        newLink = get_link(self.brokerPort) + "/topics" #Link for adding a topic
        _params = {"topic_name":topic, "partition_no" : partition_id}
        requests.post(newLink, json = _params, data = _params)