from flask import jsonify, Blueprint, request, render_template
from qr_code_generator import *
from whatsapp_automation import *
from update_chrome import *
from instance_store import *
from xmlrpc.client import ServerProxy

instance_blueprint = Blueprint('instance', __name__)
# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

@instance_blueprint.route('/')
def home():
    return render_template('index.html')

@instance_blueprint.route('/instances/home')
def show_instances():
    return render_template('instance.html', content={})

@instance_blueprint.route('/instances', methods=['GET'])
def list_instances():
    try:
        print('Listing instances')
        # List all instances - in a real app, fetch this from a database
        # Function to filter and map the dictionary
        # Filtering out specific keys
        return get_all_instances()
    except Exception as e:
        return error_response(500, str(e))

@instance_blueprint.route('/instances/edit', methods=['GET'])
def edit_instance():
    try:
        mobile_number = request.args.get('mobile_number')
        instance = retrieve_instance(mobile_number)
        return render_template("instance.html", content=instance)
    except Exception as e:
        return error_response(500, str(e))

def error_response(status_code, message):
    response = jsonify({'error': message})
    response.status_code = status_code
    return response
