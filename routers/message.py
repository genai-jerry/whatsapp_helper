from flask import Blueprint, request, render_template, g
from flask_login import login_required
from store.kafka_factory import KafkaConsumerFactory, KafkaProducerFactory
from smsidea.qr_code_generator import *
from smsidea.whatsapp_automation import *
from smsidea.message_sender import *
from browser.update_chrome import *
from store.message_store import *
from store.instance_store import *
from store.template_store import *
from store.key_store import generate_new_api_key
from utils import app_home, require_api_key

message_blueprint = Blueprint('message', __name__)

KafkaProducerFactory.get_producer()
KafkaConsumerFactory.get_consumer()

@message_blueprint.route('/api_key', methods=['POST'])
def generate_api_key():
    # Generate a new API key
    try:
        api_key = generate_new_api_key()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500

@message_blueprint.route('/text', methods=['POST'])
@require_api_key
def text_message():
    print('Sending text message')
    data = request.json
    print(f'Data: {data}')
    return send_text_message(data, app_home)

@message_blueprint.route('/template', methods=['POST'])
@require_api_key
def template_message():
    data = request.json
    return send_template_message(data, app_home)

@message_blueprint.route('/media', methods=['POST'])
@require_api_key
def media_message():
    data = request.json
    return send_media_message(data, app_home)

@message_blueprint.route('/', methods=['GET'])
@login_required
def get_messages():
    return render_template('message/list.html'), 200

@message_blueprint.route('/list', methods=['GET'])
@login_required
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
            'create_time': message['create_time'],
            'opportunity_name': message['opportunity_name']
        }
        response_data.append(message_data)

    return jsonify({
        'items': response_data,
        'page': page,
        'total_pages': total_pages,
        'total_items': total_items
    }), 200
        
@message_blueprint.route('/retry/<int:message_id>', methods=['POST'])
@login_required
def retry_message(message_id):
    # Retrieve the message from your database
    print(f'Retrying message {message_id}')
    message = get_message(message_id)
    print(f'Got the message {message}')
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    # Retry sending the message
    try:
        if 'type' not in message or message['type'] == 'text':
            send_text_message(message, app_home)
        else:
            return jsonify({'error': 'Invalid message type'}), 400

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