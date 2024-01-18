from flask import jsonify, Blueprint, request
from whatsapp.qr_code_generator import *
from whatsapp.whatsapp_automation import *
from browser.update_chrome import *
from store.message_store import *
from store.instance_store import *
from store.template_store import *
import threading
from .message_producer import producer, topic
from whatsapp.message_consumer import *

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
app_home = os.path.abspath(os.path.join(current_dir, os.pardir))

# Create a lock to synchronize access to a resource
resource_lock = threading.Lock()

message_blueprint = Blueprint('message', __name__)

def error_response(status_code, message):
    response = jsonify({'error': message})
    response.status_code = status_code
    return response

@message_blueprint.route('/text', methods=['POST'])
def text_message():
    try:
        data = request.json
        sender = data.get('sender')
        receiver = data.get('receiver')
        message = data.get('message')
        instance = retrieve_instance(sender)
        if instance == None:
            return error_response(400, 'No instance available for the number')
        if is_instance_ready(sender):
            try:
                print(f'Sending text message {message}')
                message_data = {'type': 'text', 'sender': sender, 'receiver': receiver, 
                                         'message': message}
                id = store_message(message_data)
                message_data['id'] = id
                print(f'Sending message on queue {message_data}')
                producer.produce(topic,
                                 json.dumps(message_data).encode('utf-8')
                                  )
                producer.flush()
                return jsonify({'status': 'Done', 'id': id})
            except RuntimeError as e:
                return error_response(400, str(e))
        else:
            return error_response(400, 'Instance is not ready for the number')
    except Exception as e:
        return error_response(500, str(e))
    
@message_blueprint.route('/template', methods=['POST'])
def template_message():
    try:
        data = request.json
        sender = data.get('sender')
        receiver = data.get('receiver')
        instance = retrieve_instance(sender)
        
        if instance == None:
            return error_response(400, 'No instance available for the number')
        if is_instance_ready(sender):
            try:
                template_name = data.get('template_name')
                template = retrieve_template_by_name(template_name)
                if template == None:
                    return error_response(400, 'Template not available')
            
                message = process_template(template['template_text'], data)

                message_data = {'type': 'template', 'sender': sender, 'receiver': receiver, 
                                         'message': message,
                                         'template': template['name']}
                id = store_message(message_data)
                message_data['id'] = id
                print(f'Sending message to producer {message_data}')
                producer.produce(topic,
                                 json.dumps(message_data).encode('utf-8')
                                  )
                producer.flush()
                #with resource_lock:
                #    send_whatsapp_message(mobile_number, contact_name, message)
                return jsonify({'status': 'Done', 'id': id})
            except RuntimeError as e:
                return error_response(400, str(e))
        else:
            return error_response(400, 'Instance is not ready for the number')
    except Exception as e:
        return error_response(500, str(e))
        
def process_template(template, args):
    for placeholder in set(find_placeholders(template)):
        if placeholder in args:
            template = template.replace(f"{{{placeholder}}}", str(args[placeholder]))
    return template

def find_placeholders(template):
    import re
    return re.findall(r'{(.*?)}', template)
    
def get_query_param_values(request):
    # Get the values of query parameters in the original sequence
    param_values = [value for key, value in request.args.items()]

    return param_values
    
@message_blueprint.route('/media', methods=['POST'])
def media_message():
    try:
        data = request.json
        sender = data.get('sender')
        receiver = data.get('receiver')
        url = data.get('url')
        instance = retrieve_instance(sender)
        if instance == None:
            return error_response(400, 'No instance available for the number')
        if is_instance_ready(sender):
            print(f'Sending media {url}')
            message_data = {'type': 'media', 'sender': sender, 'receiver': receiver, 
                                        'message': url}
            id = store_message(message_data)
            message_data['id'] = id
            message_data['app_home'] = app_home
            producer.produce(topic,
                                 json.dumps(message_data).encode('utf-8')
                                  )
            producer.flush()
            return jsonify({'status': 'Done', 'id': id})
        else:
            return error_response(400, 'Instance is not ready for the number')
    except Exception as e:
        return error_response(500, str(e))
