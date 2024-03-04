from flask import Blueprint, request, render_template
from store.kafka_factory import KafkaConsumerFactory, KafkaProducerFactory
from whatsapp.qr_code_generator import *
from whatsapp.whatsapp_automation import *
from whatsapp.message_sender import *
from browser.update_chrome import *
from store.message_store import *
from store.instance_store import *
from store.template_store import *
from utils import app_home

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

@message_blueprint.route('/', methods=['GET'])
def get_messages():
    return render_template('message/list.html'), 200

@message_blueprint.route('/list', methods=['GET'])
def list_messages():
    # Get the page number and size from the query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Retrieve the list of messages from your database
    messages, total_pages, total_items = get_all_messages(page, per_page)

    # Prepare the response data
    response_data = []
    for message in messages:
        message_data = {
            'id': message['id'],
            'receiver': message['receiver'],
            'receiver_id': message['receiver_id'],
            'template': message['template'],
            'status': message['status'],
            'create_time': message['create_time']
        }
        response_data.append(message_data)

    return jsonify({
        'items': response_data,
        'page': page,
        'total_pages': total_pages,
        'total_items': total_items
    }), 200
        
@message_blueprint.route('/retry/<int:message_id>', methods=['POST'])
def retry_message(message_id):
    # Retrieve the message from your database
    message = get_message(message_id)

    if not message:
        return jsonify({'error': 'Message not found'}), 404

    # Retry sending the message
    try:
        if message['type'] == 'text':
            send_text_message(message)
        elif message['type'] == 'template':
            send_template_message(message)
        else:
            return jsonify({'error': 'Invalid message type'}), 400

        update_message_status(message['id'], 'sent')
        message['status'] = 'sent'
    except Exception as e:
        update_message_status(message['id'], 'failed')
        message['status'] = 'failed'
        print(str(e))

    return jsonify({
        'id': message['id'],
        'receiver': message['receiver'],
        'template': message['template'],
        'status': message['status'],
        'create_time': message['create_time']
    }), 200