import configparser

config = configparser.ConfigParser()
config.read('./setting_bak.ini')
kafka_cn = config['kafka_cn']
print(type((kafka_cn.getint('ssh_port'))))
config['kafka_cn']['ssh_port'] = '80'
with open('./setting_bak.ini', 'w+') as f:
    config.write(f)