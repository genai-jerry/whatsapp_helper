import json
from confluent_kafka import Consumer, Message
import asyncio
import threading
import configparser
from .fb_conversions import add_lead, add_sale, video_watched

config = configparser.ConfigParser()
config.read('config/config.ini')

class KafkaAdManagerConsumerThread(threading.Thread):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(KafkaAdManagerConsumerThread, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self.consumer = Consumer({
            'bootstrap.servers': config.get('admanagement.consumer', 'bootstrap_servers'),
            'group.id': config.get('admanagement.consumer', 'group_id'),
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False  # Disable auto-commit to manage offset manually
        })

        self.topic = config.get('admanagement.consumer', 'topic')
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
        print(f'Processing conversion message: {msg.value().decode("utf-8")}')
        message_data = json.loads(msg.value().decode('utf-8'))
        print(f'Received message: {message_data}')

        if message_data['event_type'] == 'call_status':
            lead = message_data['opportunity']
            print(f'Adding New Lead {lead}')
            add_lead(lead, message_data['event_value'])
        if message_data['event_type'] == 'opportunity_status':
            lead = message_data['opportunity']
            print(f'Updating Opportunity Sale {lead}')
            # Update opportunity status
            add_sale(lead)
        if message_data['event_type'] == 'video_watched':
            lead = message_data['opportunity']
            print(f'Handling video watched {lead}')
            video_watched(lead)



