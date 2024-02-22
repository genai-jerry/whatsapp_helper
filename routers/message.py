from flask import Blueprint, request
from store.kafka_factory import KafkaConsumerFactory, KafkaProducerFactory
from whatsapp.qr_code_generator import *
from whatsapp.whatsapp_automation import *
from whatsapp.message_sender import *
from browser.update_chrome import *
from store.message_store import *
from store.instance_store import *
from store.template_store import *

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
app_home = os.path.abspath(os.path.join(current_dir, os.pardir))

message_blueprint = Blueprint('message', __name__)

KafkaProducerFactory.get_producer()
KafkaConsumerFactory.get_consumer()

@message_blueprint.route('/text', methods=['POST'])
def text_message():
    print('Sending text message')
    data = request.json
    print(f'Data: {data}')
    return send_text_message(data, app_home)

@message_blueprint.route('/template', methods=['POST'])
def template_message():
    data = request.json
    return send_template_message(data, app_home)

    
@message_blueprint.route('/media', methods=['POST'])
def media_message():
    data = request.json
    return send_media_message(data, app_home)
        
