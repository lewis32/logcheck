from sshtunnel import SSHTunnelForwarder as ssh


class MySsh:
    def __init__(self, host=None, port=None, user=None, pwd=None,
                 kafka_server=None, kafka_port=None):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.kafka_server = kafka_server
        self.kafka_port = kafka_port

        self.server = ssh(
            (self.host, self.port),
            ssh_username=self.user,
            ssh_password=self.pwd,
            remote_bind_address=(self.kafka_server, self.kafka_port)
        )

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

