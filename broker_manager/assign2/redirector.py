import threading
from assign2 import db, Topic_Model, Consumer_Model, Producer_Model, Partition_Model, Broker_Model
import uuid, requests
from .topic import Topic 
from typing import Dict, List
from .utility_funcs import *
import docker
import os
import multiprocessing

MAX_SIZE = 10

class Redirector():
    #A class that redirects all the messages to the appropriate brokers

    def __init__(self) -> None:
        #We need to handle a single lock
        self._lock = threading.Lock()
        self._metadata: Dict[str, Topic] = {}
        self._broker: Dict[int, int] = {}
        self._ids = []


    def sync_with_db(self) -> None: 
        #Sync the in-memory metadata with the database
        self._ids.append(len(Producer_Model.query.all()))
        self._ids.append(len(Consumer_Model.query.all()))
        self._ids.append(len(Broker_Model.query.all()))

        for topic in Topic_Model.query.all():
            self._metadata[topic.name] = Topic(topic.name)

        for producer in Producer_Model.query.all():
            self._metadata[producer.topic_name].add_producer(producer.id)

        for consumer in Consumer_Model.query.all():
            self._metadata[consumer.topic_name].add_consumer(consumer.id)

        for partition in Partition_Model.query.all():
            self._metadata[partition.topic_name].add_partition(partition.id)
            if partition.broker not in self._broker.keys():
                self._broker[partition.broker] = 1
            else:  
                self._broker[partition.broker] += 1


    def _exists(self, topic_name: str, partition_no = None) -> bool:
        #Check whether the topic exists or not
        if Topic_Model.query.filter_by(name = topic_name).count() == 0:
            return False 
        
        elif partition_no != None:
            if Partition_Model.query.filter_by(topic_name = topic_name, partition_number = partition_no).count() == 0:
                return False 
        
        return True


    def add_topic(self, topic_name: str) -> None:
        print("Add Topic")
        if Broker_Model.query.all() == []:
            #No broker exists 
            raise Exception("No brokers are registered currently")
            
        #Add the topic
        if Topic_Model.query.filter_by(name = topic_name).count() != 0:
            raise Exception("Topic already exists")

        with self._lock:
              self._metadata[topic_name] = Topic(topic_name)

        db.session.add(Topic_Model(name = topic_name))
        db.session.commit()

        #Create a first partition for the topic 
        self.create_partition(topic_name)


    def get_topics(self) -> List[str]:
        print("Get Topics")
        # List all topics
        topics = []
        for topic in Topic_Model.query.all():
            topics.append(topic.name)
        return topics

    def get_num_partitions(self, topic_name: str) -> int:
        print("Get Number of Partitions")
        return Partition_Model.query.filter_by(topic_name = topic_name).all().count()
        # return self._metadata[topic_name].get_partition_count()


    def get_size(self, topic_name: str, consumer_id: int, partition_no = -1) -> int:
        print("Get size22")
        #Get the number of remaining messages in the specific partition for the consumer
        if not self._exists(topic_name):
            raise Exception("Topic does not exist")

        if Consumer_Model.query.filter_by(topic_name = topic_name, id = consumer_id).count() == 0:
            raise Exception("Consumer not registered with this topic")

        consumer = Consumer_Model.query.filter_by(id = consumer_id).first()
        consumer.heartbeat = db.func.now()
        db.session.commit()
        
        if partition_no == -1: 
            #Get the remaining number of messages from each partition of the topic
            size = 0
            for partition in Partition_Model.query.filter_by(topic_name = topic_name).all():
                print(size)
                newLink = get_link(partition.broker) + "/size"
                _params = {"topic_name" : topic_name, "consumer_id" : consumer_id, "partition_no" : partition.id}
                resp = requests.get(newLink, data = _params, json = _params, params = _params)
                if resp.json()["status"] == "success":
                    size = size + resp.json()['size']
                else:
                    pass 
            return size
        # Feature implemented : Support for multiple partitions in a broker for the same topic
        print("Hey")
        partition = Partition_Model.query.filter_by(topic_name = topic_name, partition_number = partition_no).first()
        if partition == None:
            raise Exception("The Partition Number does not exist")
        newLink = get_link(partition.broker) + "/size"
        # _params = {"topic_name" : topic_name, "consumer_id" : consumer_id}
        _params = {"topic_name" : topic_name, "consumer_id" : consumer_id, "partition_no" : partition_no}
        resp = requests.get(newLink, data = _params, json = _params, params = _params)
        print(resp.json())
        if resp.json()['status'] == "success":
            return resp.json()['size']
        print(resp.json())
        return -1



    def create_partition(self, topic_name: str, producer_id = None) -> str:
        print("Create partition")
        if Broker_Model.query.all() == []:
            #No broker currently registered
            raise Exception("No broker is currently registered")
        
        #Create a partition in the specific topic
        
        if Topic_Model.query.filter_by(name = topic_name).count()==0:
        # if topic_name not in self._metadata.keys():
            raise Exception("Topic does not exist")
        
        if producer_id != None:
            if Producer_Model.query.filter_by(topic_name = topic_name, id = producer_id).count() == 0:
            # if producer_id not in self._metadata[topic_name].producers:
                raise Exception("Producer is not subscribed to the topic")
            producer = Producer_Model.query.filter_by(id = producer_id).first()
            producer.heartbeat = db.func.now()
            db.session.commit()

        # partition_id starts at 0, and is sequential
        partition_id = len(Partition_Model.query.filter_by(topic_name = topic_name).all()) +1
        self._metadata[topic_name].add_partition(partition_id)
        #Now allocate a broker to the partition 
        broker_number = 0
        broker_size = MAX_SIZE # This needs to be set
        with self._lock:
            for broker_id in self._broker.keys():
                if self._broker[broker_id] < broker_size:
                    broker_size = self._broker[broker_id]
                    broker_number = broker_id
        
        if broker_size == MAX_SIZE:
            # broker_number = self.add_broker()
            print("Broker Overload : Please create new broker")

        #Add the partition to the broker
        self._broker[broker_number] += 1
        newLink = get_link(broker_number) + "dummy/topics"
        # print(newLink)
        _params = {"topic_name":topic_name, "partition_no" : partition_id}
        resp = requests.post(newLink, json = _params, data = _params)

        for consumer in Consumer_Model.query.filter_by(topic_name = topic_name).all():
            #Inform the broker about the new consumer
            newLink = get_link(broker_number) + "dummy/consumer/register"
            _params = {"topic_name" : topic_name, "consumer_id": consumer.id}
            requests.post(newLink, data = _params)


        if resp.json()['status'] == "success":
            db.session.add(Partition_Model(topic_name = topic_name, partition_number = partition_id, broker = broker_number))
            db.session.commit()
            return "success" 

        print(resp.json())
        return "failure"


    def add_consumer(self, topic_name: str) -> int:
        print("Add consumer")
        #Add a consumer to a specific topic 
        if not self._exists(topic_name):
            raise Exception("Topic does not exist")

        with self._lock:
            consumer_id = self._ids[1] + 1
            self._ids[1] += 1
            self._metadata[topic_name].add_consumer(consumer_id)

        db.session.add(Consumer_Model(id = consumer_id, topic_name = topic_name))
        db.session.commit()

        #Now let the other brokers subscribed to this specific topic know about the new consumer
        for partition in Partition_Model.query.filter_by(topic_name = topic_name).all():
            #Inform the broker about the new consumer
            newLink = get_link(partition.broker) + "/dummy/consumer/register"
            _params = {"topic_name" : topic_name, "consumer_id": consumer_id}
            requests.post(newLink, data = _params)

        return consumer_id


    def add_producer(self, topic_name: str) -> int:
        print("Add producer")
        #Add a producer to a specific topic 
        if not self._exists(topic_name):
            raise Exception("Topic does not exist")

        with self._lock:
            producer_id = self._ids[0] + 1
            self._ids[0] += 1
            self._metadata[topic_name].add_producer(producer_id)


        db.session.add(Producer_Model(id = producer_id,topic_name = topic_name))
        db.session.commit()

        return producer_id

    
    def add_log(self, topic_name: str, producer_id: int, message: str, partition_no = -1) -> None:
        print("Add log")
        #add a log to the specific partition 
        if partition_no == -1:
            if not self._exists(topic_name):
                raise Exception("Topic does not exist")

            if Producer_Model.query.filter_by(topic_name = topic_name, id = producer_id).count() == 0:
                raise Exception("Producer is not subscribed to the topic")
            
            self._metadata[topic_name].update_round_robin()
            partition_no = self._metadata[topic_name].current_round_robin_index

        if not self._exists(topic_name, partition_no):
            raise Exception("The Partition does not exist")

        producer = Producer_Model.query.filter_by(id = producer_id).first()
        producer.heartbeat = db.func.now()
        db.session.commit()
        #Now send the add request to the appropriate broker 
        # print("Hey")
        partition = Partition_Model.query.filter_by(topic_name = topic_name, partition_number = partition_no).first()
        newLink = get_link(partition.broker) + "/dummy/producer/produce" #Link for publishing to the specific partition of a particular topic 
        # _params = {"topic_name" : topic_name} #Complete this part as well
        _params = {"topic_name" : topic_name, "partition_no" : partition_no, "message" : message}
        # print(_params)
        requests.post(newLink, data = _params, json = _params, params = _params)


    def get_log(self, topic_name: str, consumer_id: int):
        print("Get log")
        #Can return None or the message depending on if the queue is full or not
        if not self._exists(topic_name):
            raise Exception("Topic does not exist")

        if Consumer_Model.query.filter_by(topic_name = topic_name, id = consumer_id).count() == 0:
            raise Exception("Consumer not registered with this topic")
        
        consumer = Consumer_Model.query.filter_by(id = consumer_id).first()
        consumer.heartbeat = db.func.now()
        db.session.commit()
        
        log_msg = {}

        for partition in Partition_Model.query.filter_by(topic_name = topic_name).all():
            newLink = get_link(partition.broker) + "/consumer/probe"
            _params = {"topic_name" : topic_name, "partition_no" : partition.partition_number, "consumer_id" : consumer_id}
            msg = requests.get(newLink, data = _params, json = _params, params = _params)
            print(msg.json())
            if msg.json()['status'] == 'success':
                log_msg[partition] = msg.json()

        if len(log_msg) == 0:
            return None

        # FIX These Params
        partition_no = -1
        min_time = None
        for partition in log_msg.keys():
            if min_time == None:
                min_time = log_msg[partition]['created']
                partition_no = partition
            elif log_msg[partition]['created'] < min_time :
                min_time = log_msg[partition]['created']
                partition_no = partition
        # print(partition_no)
        newLink = get_link(partition_no.broker) + "/dummy/consumer/consume"
        _params = {"topic_name" : topic_name, "partition_no" : partition_no.partition_number, "consumer_id" : consumer_id}
        return requests.get(newLink, data = _params, params = _params, json = _params).json()['message']
        

    def add_broker(self, port_no: int):
        print("Add Broker")

        # does_exist = Broker_Model.query.filter_by(port_no = port_no).all()
        # if does_exist != []:
        if Broker_Model.query.filter_by(port = port_no).count() != 0:
            #Broker with that port number already exist
            raise Exception("A broker already exists on the given port number")

        db.session.add(Broker_Model(port = port_no))
        db.session.commit()

        # print("Heyyy")

        with self._lock:
            self._broker[port_no] = 0

        return "success"

    def remove_broker(self, port_no : int):
        print("Remove Broker")
        # Remove existing broker and delete the database
        does_exist = Broker_Model.query.filter_by(port_no = port_no).all()
        if does_exist == []:
            #Broker with that port number already exist
            raise Exception("No broker exists on the given port number")

        db.delete(does_exist)
        db.commit()

        with self._lock:
            del self._broker[port_no]

    def healthCheck(self): 
        # Health Check implementation
        for broker_id in self._broker.keys():
            newLink = get_link(broker_id) + "/health"
            print(newLink)
            _params = {}
            try:
                resp = requests.post(newLink, json = _params, data = _params, timeout = 2)
                broker = Broker_Model.query.filter_by(port = broker_id).first()
                broker.heartbeat = db.func.now()
                db.session.commit()
            except requests.exceptions.Timeout:
                print("The request timed out: Broker "+str(broker_id)+" is not responding !")