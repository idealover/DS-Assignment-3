# DS_Assignment3


## Setting up Dependencies

Run the following commands in the terminal.

- To setup and activate the virtual environment:
```
Scripts\activate
```

- Install dependencies:
```
pip install -r requirements.txt
```

## Running the Project

- Run the app
```
python loadbalancer.py
```

- Run the write manager
```
flask run -p 5001
```

- Run read managers
```
flask run -p %port
```
* Replace %port with port number for the manager replica
## Setting up dockers for multiple brokers

- Setup docker

```
python create_broker.py %n
```
 Replace %n with the id number for the broker

- For linux based systems, this will spawn the raft process, but Windows does not support fork. Hence, we need to run the raft processes separately as:
```
python raftproc.py %raft_port %broker_port
```
 Replace %raft_port and %broker_port by the port of the raft process and the port of the corresponding broker


## Running tests

- For testing all functionalities
```
python -i tester.py
```

All functionalities are now available to be used by the user very conviniently
- createTopic(topic_name) :
Create a new Topic
- listTopics() :
List all topics present
- registerProducer(topic_name) :
Register a producer to this topic
- registerConsumer(topic_name) :
Register a consumer to this topic
- enqueue(topic_name, producer_id, message, partition_no : default) :
Add a log message
- dequeue(topic_name, consumer_id) :
View a log message
- size(topic_name, consumer_id, partition_no : default) :
Get the number of messages not yet viewed by the consumer
- getPartitions(topic_name) :
Get the number of partitions for this topic
- partition(topic_name, producer_id) :
Create a new partition for this topic
- add_broker(port) :
Add a broker using this port
