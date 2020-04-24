from sshtunnel import SSHTunnelForwarder as ssh
from kafka import KafkaConsumer as kc
import logging

log = logging.getLogger(__name__)


class MyKafka:
    def __init__(self, kafka_config, ssh_config=None):
        self.ssh_config = ssh_config
        self.kafka_config = kafka_config

    def _start_ssh(self):
        if self.ssh_config:
            try:
                print(self.kafka_config)
                print(self.ssh_config)
                self.server = ssh(
                    (self.ssh_config['host'], int(self.ssh_config['port'])),
                    ssh_username=self.ssh_config['user'],
                    ssh_password=self.ssh_config['pwd'],
                    remote_bind_address=(self.kafka_config['server'][0].split(':')[0], int(self.kafka_config['server'][0].split(':')[1]))
                )
                self.server.start()
                log.info('开始执行SSH通道')
            except Exception as e:
                log.error(str(e))

    def _stop_ssh(self):
        try:
            self.server.stop()
        except Exception as e:
            log.error(str(e))

    def init_kafka(self):
        try:
            self._start_ssh()

            config = {
                'bootstrap_servers': '127.0.0.1:'
                                     + str(self.server.local_bind_port),
                'group_id': self.kafka_config['group_id']
            } if self.ssh_config else {
                'bootstrap_servers': self.kafka_config['server'],
                'group_id': self.kafka_config['group_id']
            }
            log.info(config)

            self.consumer = kc(**config)
        except Exception as e:
            log.error(str(e))

    def subscribe_kafka(self, topics=None):
        try:
            log.info('Starting subscribing kafka...')
            self.consumer.subscribe(topics=topics)
        except Exception as e:
            log.error(str(e))

    def poll_kafka(self):
        try:
            log.info('Starting polling kafka...')
            data = self.consumer.poll(timeout_ms=1000)
            if data:
                data_ = list(data.values())[0][0].value.decode('utf-8')
                log.info(data_)
                return data_
        except Exception as e:
            log.error(str(e))

    def stop_kafka(self):
        try:
            self.consumer.unsubscribe()
            self.consumer.close()
            if self.ssh_config:
                self.server.stop()
        except Exception as e:
            log.error(str(e))

    def topics_kafka(self):
        return self.consumer.topics()
