from confluent_kafka import Producer
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

class KafkaProducer(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(KafkaProducer, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        print('Initializing Kafka producer')
        self.producer = Producer({'bootstrap.servers': config.get('Producer', 'bootstrap_servers')
                    })
        self.topic = config.get('Producer', 'topic')
        print('Kafka producer initialized')

    def get_producer(self):
        return self.producer
    
    def get_topic(self):
        return self.topic
    
