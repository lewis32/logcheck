import configparser

config = configparser.ConfigParser()
config.read('./cfg_bak.ini')
kafka_cn = config['kafka_cn']
print(type((kafka_cn.getint('ssh_port'))))
config['kafka_cn']['ssh_port'] = '80'
with open('./cfg_bak.ini', 'w+') as f:
    config.write(f)