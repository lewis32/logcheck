from sshtunnel import SSHTunnelForwarder as ssh
# from pykafka import KafkaClient as kc
from kafka import KafkaConsumer as kc

server = ssh(
    '47.74.250.255',
    ssh_username='root',
    ssh_password='^1xHGMlcc$',
    remote_bind_address=('192.137.180.1', 8081)
)

server.start()

topics = [
    "127.0.0.1:9002"
]
configs = {
    'bootstrap_servers': '127.0.0.1:9002',
}

client = kc(
    *topics,
    **configs
)

server.stop()

