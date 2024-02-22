import json
from flask import jsonify

from store.kafka_factory import KafkaProducerFactory
from .whatsapp_automation import *
from store.instance_store import *
from store.template_store import retrieve_template_by_name
from store.message_store import *
from utils import error_response

def prepare_message(data):
    sender = data.get('sender')
    instance = retrieve_instance(sender)
    if instance == None:
        return None, error_response(400, 'No instance available for the number')
    if not is_instance_ready(sender):
        return None, error_response(400, 'Instance is not ready for the number')
    return sender, None

def send_text_message(data, app_home):
    sender, error = prepare_message(data)
    if error:
        return error
    try:
        receiver = data.get('receiver')
        
        message_data = {
            'sender': sender,
            'receiver': receiver,
            'message': data.get('message'),
            'type': 'text'
        }
        id = store_message(message_data)
        message_data['id'] = id
        message_data['app_home'] = app_home
        return send_message_to_producer(message_data)
    except RuntimeError as e:
        return error_response(400, str(e))

def send_template_message(data, app_home):
    sender, error = prepare_message(data)
    if error:
        return error
    try:
        receiver = data.get('receiver')
        template_name = data.get('template_name')
        template = retrieve_template_by_name(template_name)
        # Add the code to send a template message here.
        message = process_template(template['template_text'], data)
        message_data = {
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'type': 'template',
            'template': template_name
        }
        id = store_message(message_data)
        message_data['id'] = id
        message_data['app_home'] = app_home
        return send_message_to_producer(message_data)
    except RuntimeError as e:
        return error_response(400, str(e))
    
def process_template(template, args):
    print(f'Processing template {template} with {args}')
    for placeholder in set(find_placeholders(template)):
        if placeholder in args:
            template = template.replace(f"{{{placeholder}}}", str(args[placeholder]))
    return template

def find_placeholders(template):
    import re
    return re.findall(r'{(.*?)}', template)

def send_media_message(data, app_home):
    sender, error = prepare_message(data)
    if error:
        return error
    try:
        receiver = data.get('receiver')
        url = data.get('url')
        message_data = {
            'sender': sender,
            'receiver': receiver,
            'message': url,
            'type': 'media'
        }
        id = store_message(message_data)
        message_data['id'] = id
        message_data['app_home'] = app_home
        return send_message_to_producer(message_data)
    except RuntimeError as e:
        return error_response(400, str(e))

def send_message_to_producer(message_data):
    try:
        producer = KafkaProducerFactory.get_producer()
        producer.get_producer().produce(producer.get_topic(),
                         json.dumps(message_data).encode('utf-8')
                         )
        producer.get_producer().    flush()
        return jsonify({'status': 'Done', 'id': message_data['id']})
    except RuntimeError as e:
        return error_response(400, str(e))