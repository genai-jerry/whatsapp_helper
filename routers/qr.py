from flask import Flask, jsonify, Blueprint, request, render_template, url_for, redirect, make_response
from whatsapp.qr_code_generator import *
from whatsapp.whatsapp_automation import *
from browser.update_chrome import *
from store.instance_store import *
from xmlrpc.client import ServerProxy
from utils import error_response

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
app_home = os.path.abspath(os.path.join(current_dir, os.pardir))

qr_blueprint = Blueprint('qr', __name__)
# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

@qr_blueprint.route('/register', methods=['POST'])
def register_qr():
    try:
        data = request.json
        mobile_number = data.get('mobileNumber')
        user_name = data.get('userName')
        instance = retrieve_instance(mobile_number)
        if instance == None:
            print('Creating new instance')
            result = server.create_instance(app_home, mobile_number)
            if result:
                print('Storing Instance')
                store_instance(mobile_number, {'status': 'Pending', 'name': user_name, 'mobile_number': mobile_number})
            else:
                return error_response(400, f'{app_home} - Unable to load page')
        else:
            if is_instance_ready(mobile_number):
                return jsonify({'status': 'ready', 'message': 'Instance creation initiated', 'mobileNumber': mobile_number})
       
        # Respond with a successful creation message or similar
        return jsonify({'status': 'pending', 'message': 'Instance creation initiated', 'mobileNumber': mobile_number})
    except Exception as e:
        return error_response(500, f'{app_home} - {str(e)}')
    
@qr_blueprint.route('/refresh', methods=['POST'])
def refresh_qr():
    try:
        print('Refreshing QR')
        data = request.json
        mobile_number = data.get('mobileNumber')
        user_name = data.get('userName')
        print('Retreiving instances')
        instance = retrieve_instance(mobile_number)
        print(f'Got instance {instance}')
        if instance == None:
            return create_instance(mobile_number, user_name, True)
        else:
            print('Instance is available')
            try:
                if is_instance_ready(mobile_number):
                    print('Instance is ready. Updating instance')
                    update_instance(mobile_number, {'status': 'Ready'})
                    print('Updated the instance')
                    return jsonify({'status': 'ready', 'message': 'Instance creation initiated', 'mobileNumber': mobile_number})
                else:
                    print('Refreshing Browser')
                    server.refresh(mobile_number)
            except:
                return create_instance(mobile_number, user_name, False)
        # Respond with a successful creation message or similar
        return jsonify({'status': 'pending', 'message': 'QR Loading Initiated', 'mobileNumber': mobile_number})
    except Exception as e:
        return error_response(500, f'{app_home} - {str(e)}')

def create_instance(mobile_number, user_name, new_instance):
    print('Creating new instance')
    result = server.create_instance(app_home, mobile_number)
    print(result)
    if result:
        if new_instance:
            print('Storing Instance')
            store_instance(mobile_number, {'status': 'Pending', 'name': user_name, 'mobile_number': mobile_number})
        # Respond with a successful creation message or similar
        return jsonify({'status': 'pending', 'message': 'Instance creation initiated', 'mobileNumber': mobile_number})
    else:
        return error_response(400, f'{app_home} - Unable to load page')

@qr_blueprint.route('/register', methods=['GET'])
def get_qr_code():
    try:
        mobile_number = request.args.get('mobile_number')

        # Check if the instance exists and if the QR code is ready
        instance = retrieve_instance(mobile_number)
        print(f'Instance in get_qr_code is {instance}')
        if instance != None:
            print('Loading the QR Code')
            # In a real application, provide the URL or path to the generated QR code
            load_qr_code(mobile_number, app_home)
            print('Loaded the QR Code')
            return jsonify({'status': 'ready'})
        else:
            print('Updating instance')
            update_instance(mobile_number, {'status': 'Pending'})
            print('Updated the instance')
            return jsonify({'status': 'not ready'})
    except Exception as e:
        return error_response(500, str(e))
    
@qr_blueprint.route('/image', methods=['GET'])
def redirect_to_home():
    mobile_number = request.args.get('mobile_number')
    return redirect(url_for('static', filename = f'/images/whatsapp_web_qr_{mobile_number}.png'))

@qr_blueprint.route('/active', methods=['GET'])
def check_activation():
    try:
        mobile_number = request.args.get('mobile_number')

        # Check if the instance is activated
        instance = retrieve_instance(mobile_number)
        if instance != None and is_whatsapp_ready(mobile_number):
            update_instance(mobile_number, {'status': 'Ready'})
            #read_text_message(mobile_number)
            return jsonify({'status': 'ready'})
        else:
            update_instance(mobile_number, {'status': 'Pending'})
            return jsonify({'status': 'not ready'})
    except Exception as e:
        return error_response(500, str(e))
