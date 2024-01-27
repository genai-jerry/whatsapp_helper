from whatsapp.whatsapp_automation import send_media_whatsapp_message, send_whatsapp_message
import json
from confluent_kafka import Consumer, KafkaException, Message
import asyncio
import threading
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

class KafkaConsumerThread(threading.Thread):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(KafkaConsumerThread, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self.consumer = Consumer({
            'bootstrap.servers': config.get('Consumer', 'bootstrap_servers'),
            'group.id': config.get('Consumer', 'group_id'),
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False  # Disable auto-commit to manage offset manually
        })

        self.topic = config.get('Consumer', 'topic')
        self.consumer.subscribe([self.topic])

    def run(self):
        try:
            while True:
                msg = self.consumer.poll(1.0)

                try:
                    if msg is None:
                        continue
                    if msg.error():
                        print(f'Got error in consumer {msg.error()}')
                        continue
                    received_message = json.loads(msg.value().decode('utf-8'))
                    print('Received message:', received_message)

                    # Process the message asynchronously
                    asyncio.run(self.process_message(msg))
                    self.consumer.commit(msg)
                except Exception as e:
                    print(f'Got an error {str(e)}')

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    async def process_message(self, msg: Message):
        # Your asynchronous message processing logic here
        # For example, you can use `asyncio.sleep` to simulate asynchronous processing
        await asyncio.sleep(2)
        print(f'Processed message: {msg.value().decode("utf-8")}')
        message_data = json.loads(msg.value().decode('utf-8'))
        print(f'Received message: {message_data}')
        if message_data['type'] == 'media':
            print('Sending whatsapp media message')
            send_media_whatsapp_message(message_data)
        else:
            print('Sending whatsapp text message')
            send_whatsapp_message(message_data)

def start_consumer():
    print('Kafka Consumer Starting')
    consumer_thread = KafkaConsumerThread()
    consumer_thread.start()
    print('Kafka Consumer Started')

