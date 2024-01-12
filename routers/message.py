from flask import jsonify, Blueprint, request
from qr_code_generator import *
from whatsapp_automation import *
from update_chrome import *
from store.instance_store import *
import threading
from xmlrpc.client import ServerProxy

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
app_home = os.path.abspath(os.path.join(current_dir, os.pardir))

# Create a lock to synchronize access to a resource
resource_lock = threading.Lock()

message_blueprint = Blueprint('message', __name__)

# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

def error_response(status_code, message):
    response = jsonify({'error': message})
    response.status_code = status_code
    return response

@message_blueprint.route('/text', methods=['POST'])
def text_message():
    try:
        data = request.json
        mobile_number = data.get('mobile_number')
        contact_name = data.get('contact_name')
        message = data.get('message')
        instance = retrieve_instance(mobile_number)
        if instance == None:
            return error_response(400, 'No instance available for the number')
        if is_instance_ready(mobile_number):
            try:
                with resource_lock:
                    send_whatsapp_message(mobile_number, contact_name, message)
                    return jsonify({'status': 'Done'})
            except RuntimeError as e:
                return error_response(400, str(e))
        else:
            return error_response(400, 'Instance is not ready for the number')
    except Exception as e:
        return error_response(500, str(e))
    
def get_query_param_values(request):
    # Get the values of query parameters in the original sequence
    param_values = [value for key, value in request.args.items()]

    return param_values
    
@message_blueprint.route('/media', methods=['POST'])
def media_message():
    try:
        data = request.json
        mobile_number = data.get('mobile_number')
        contact_name = data.get('contact_name')
        url = data.get('url')
        instance = retrieve_instance(mobile_number)
        if instance == None:
            return error_response(400, 'No instance available for the number')
        if is_instance_ready(mobile_number):
            with resource_lock:
                send_media_whatsapp_message(mobile_number, app_home, contact_name, url)
                return jsonify({'status': 'Done'})
        else:
            return error_response(400, 'Instance is not ready for the number')
    except Exception as e:
        return error_response(500, str(e))
