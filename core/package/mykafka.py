from sshtunnel import SSHTunnelForwarder as ssh
from kafka import KafkaConsumer as kc
import json
import random


class MyKafka:
    def __init__(self, kafka_config, ssh_config=None):
        self.ssh_config = ssh_config
        self.kafka_config = kafka_config

    def _start_ssh(self):
        if not self.ssh_config:
            self.server = ssh(
                (self.ssh_config['host'], self.ssh_config['port']),
                ssh_username=self.ssh_config['user'],
                ssh_password=self.ssh_config['pwd'],
                remote_bind_address=(self.kafka_config['host'], self.kafka_config['port'])
            )
            self.server.start()

    def _stop_ssh(self):
        self.server.stop()

    def start_kafka(self):
        self._start_ssh()
        self.kafka_configs = {
            'bootstrap_servers': '127.0.0.1:'
                                 + str(self.server.local_bind_port),
            'group_id': str(random.random())
        } if not self.ssh_config else {
            'bootstrap_servers': self.kafka_config['host'] + ':' + self.kafka_config['port'],
            'group_id': str(random.random())
        }

        self.consumer = kc(**self.kafka_configs)

    def consume_kafka(self, topics=None):
        self.consumer.subscribe(topics=topics)
        count = 0
        while True:
            if count > 9:
                break
            print(self.consumer.poll(timeout_ms=1000))
            count += 1

    def stop_kafka(self):
        self.consumer.unsubscribe()
        self.consumer.close()
        if not self.ssh_config:
            self.server.stop()

    def topics_kafka(self):
        return self.consumer.topics()
