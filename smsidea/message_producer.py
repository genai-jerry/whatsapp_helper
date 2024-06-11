from confluent_kafka import Producer
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

class KafkaMessageProducer(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(KafkaMessageProducer, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        print('Initializing Kafka message producer')
        self.producer = Producer({'bootstrap.servers': config.get('message.producer', 'bootstrap_servers')
                    })
        self.topic = config.get('message.producer', 'topic')
        print('Kafka message producer initialized')

    def get_producer(self):
        return self.producer
    
    def get_topic(self):
        return self.topic
    
