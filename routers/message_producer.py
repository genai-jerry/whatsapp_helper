from confluent_kafka import Producer
import json
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

producer = Producer({'bootstrap.servers': config.get('Producer', 'bootstrap_servers')
                     })
topic = config.get('Producer', 'topic')