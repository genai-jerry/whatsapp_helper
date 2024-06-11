from confluent_kafka import Producer
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

class KafkaAdManagerProducer(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(KafkaAdManagerProducer, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        print('Initializing Kafka ads producer')
        self.producer = Producer({'bootstrap.servers': config.get('admanagement.producer', 'bootstrap_servers')
                    })
        self.topic = config.get('admanagement.producer', 'topic')
        print('Kafka ads producer initialized')

    def get_producer(self):
        return self.producer
    
    def get_topic(self):
        return self.topic
    
