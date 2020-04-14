from sshtunnel import SSHTunnelForwarder as ssh
from kafka import KafkaConsumer as kc
import json
import random


server = ssh(
    ('52.38.247.195', 22),
    ssh_username='root',
    ssh_password='AWS@nus!S1t#!#',
    remote_bind_address=('192.169.1.181', 9092)
)

server.start()

topics = [
    'json.na.ter.terminal'
]

configs = {
    'bootstrap_servers': '127.0.0.1:'+str(server.local_bind_port),
    'group_id': str(random.random())
}

consumer = kc(**configs)

print(json.dumps(list(consumer.topics())))

consumer.subscribe(topics=list(consumer.topics()))

count = 0
while True:
    if count > 9:
        break
    print(consumer.poll(timeout_ms=1000))
    count += 1

consumer.unsubscribe()
consumer.close()

server.stop()


topics = [
    'json.exposure'
]

configs = {
    'bootstrap_servers': '10.18.220.142:9092',
}

consumer = kc(
    **configs
)

print(json.dumps(list(consumer.topics())))

consumer.subscribe(
    topics=topics
)

print('partition:', consumer.partitions_for_topic(topic=topics[0]))

count = 0
while True:
    if count > 9:
        break
    print(consumer.poll(timeout_ms=1000))
    count += 1

consumer.unsubscribe()
consumer.close()



