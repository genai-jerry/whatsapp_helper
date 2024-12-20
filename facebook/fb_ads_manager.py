import json
from middleware.kafka_factory import KafkaConsumerFactory, KafkaProducerFactory
KafkaConsumerFactory.get_consumer('admanager')

def handle_opportunity_update(opportunity, event_type, event_value=None):
    # Send message to fbad_producer
    try:
        print('Getting producer')
        producer = KafkaProducerFactory.get_producer('admanager')
        print('Sending message to Kafka ad manager')
        producer.get_producer().produce(producer.get_topic(),
                        json.dumps({'opportunity': opportunity, 
                                    'event_type': event_type,
                                    'event_value': event_value}).encode('utf-8')
                        )
        print('Sent message to Kafka ad manager')
    except Exception as e:
        print(f'Error sending message to Kafka ad manager: {e}')
