from facebook.fbad_producer import KafkaAdManagerProducer
from facebook.fbad_consumer import KafkaAdManagerConsumerThread

class KafkaProducerFactory:
    _producers = {}

    @staticmethod
    def get_producer(key):
        if key not in KafkaProducerFactory._producers or KafkaProducerFactory._producers[key] is None:
            print('Creating Kafka producer')
            if key == 'admanager':
                KafkaProducerFactory._producers[key] = KafkaAdManagerProducer()
            print('Kafka producer created')
            return KafkaProducerFactory._producers[key]
        else:
            return KafkaProducerFactory._producers[key]
  

class KafkaConsumerFactory:
    _consumers = {}

    @staticmethod
    def get_consumer(key):
        if key not in KafkaConsumerFactory._consumers or KafkaConsumerFactory._consumers[key] is None:
            print('Creating Kafka consumer')
            if key == 'admanager':
                consumer_thread = KafkaAdManagerConsumerThread()
                KafkaConsumerFactory._consumers[key] = consumer_thread
            consumer_thread.start()
            print('Kafka consumer created')
            return KafkaConsumerFactory._consumers[key]
        else:
            return KafkaConsumerFactory._consumers[key]
    