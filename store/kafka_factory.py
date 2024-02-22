from confluent_kafka import Producer
from store.message_consumer import KafkaConsumerThread
from store.message_producer import KafkaProducer

class KafkaProducerFactory:
    _producer = None

    @staticmethod
    def get_producer():
        if KafkaProducerFactory._producer is None:
            print('Creating Kafka producer')
            KafkaProducerFactory._producer = KafkaProducer()
            print('Kafka producer created')
        return KafkaProducerFactory._producer
  

class KafkaConsumerFactory:
    _consumer = None

    @staticmethod
    def get_consumer():
        if KafkaConsumerFactory._consumer is None:
            print('Creating Kafka consumer')
            consumer_thread = KafkaConsumerThread()
            consumer_thread.start()
            KafkaConsumerFactory._consumer = consumer_thread
            print('Kafka consumer created')
        return KafkaConsumerFactory._consumer
    