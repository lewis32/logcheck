from sshtunnel import SSHTunnelForwarder as ssh
from kafka import KafkaConsumer as kc
from core.package.mylogging import MyLogging as Logging
import random

LOGGER = Logging(__name__)


class MyKafka:
    def __init__(self, kafka_config, ssh_config=None):
        self.ssh_config = ssh_config
        self.kafka_config = kafka_config

    def _start_ssh(self):
        if self.ssh_config:
            try:
                self.server = ssh(
                    (self.ssh_config['host'], self.ssh_config['port']),
                    ssh_username=self.ssh_config['user'],
                    ssh_password=self.ssh_config['pwd'],
                    remote_bind_address=(self.kafka_config['host'], self.kafka_config['port'])
                )
                self.server.start()
            except Exception as e:
                LOGGER.error(str(e))

    def _stop_ssh(self):
        try:
            self.server.stop()
        except Exception as e:
            LOGGER.error(str(e))

    def start_kafka(self):
        try:
            self._start_ssh()

            config = {
                'bootstrap_servers': '127.0.0.1:'
                                     + str(self.server.local_bind_port),
                'group_id': str(random.random())
            } if self.ssh_config else {
                'bootstrap_servers': self.kafka_config['host'] + ':' + self.kafka_config['port'],
                'group_id': str(random.random())
            }

            self.consumer = kc(**config)
        except Exception as e:
            LOGGER.error(str(e))

    def subscribe_kafka(self, topics=None):
        try:
            self.consumer.subscribe(topics=topics)
        except Exception as e:
            LOGGER.error(str(e))

    def poll_kafka(self):
        try:
            self.consumer.poll(timeout_ms=1000)
        except Exception as e:
            LOGGER.error(str(e))

    def stop_kafka(self):
        try:
            self.consumer.unsubscribe()
            self.consumer.close()
            if self.ssh_config:
                self.server.stop()
        except Exception as e:
            LOGGER.error(str(e))

    def topics_kafka(self):
        return self.consumer.topics()
