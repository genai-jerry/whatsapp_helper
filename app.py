from flask import Flask, jsonify, request, render_template, url_for, redirect, make_response
from qr_code_generator import *
from whatsapp_automation import *
from update_chrome import *
from instance_store import *
import threading
from xmlrpc.client import ServerProxy

# Create a lock to synchronize access to a resource
resource_lock = threading.Lock()

app = Flask(__name__)
# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/instances/home')
def show_instances():
    return render_template('instance.html', content={})

@app.route('/register/qr', methods=['POST'])
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
    
@app.route('/register/qr/refresh', methods=['POST'])
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
            print('Creating new instance')
            result = server.create_instance(app_home, mobile_number)
            if result:
                print('Storing Instance')
                store_instance(mobile_number, {'status': 'Pending', 'name': user_name, 'mobile_number': mobile_number})
                # Respond with a successful creation message or similar
                return jsonify({'status': 'pending', 'message': 'Instance creation initiated', 'mobileNumber': mobile_number})
            else:
                return error_response(400, f'{app_home} - Unable to load page')
        else:
            print('Instance is available')
            if is_instance_ready(mobile_number):
                print('Instance is ready. Updating instance')
                update_instance(mobile_number, {'status': 'Ready'})
                print('Updated the instance')
                return jsonify({'status': 'ready', 'message': 'Instance creation initiated', 'mobileNumber': mobile_number})
            else:
                print('Refreshing Browser')
                server.refresh(mobile_number)
        # Respond with a successful creation message or similar
        return jsonify({'status': 'pending', 'message': 'QR Loading Initiated', 'mobileNumber': mobile_number})
    except Exception as e:
        return error_response(500, f'{app_home} - {str(e)}')

@app.route('/register/qr', methods=['GET'])
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
            print('Loaded the QR Code and updating instance')
            update_instance(mobile_number, {'status': 'Ready'})
            print('Updated the instance')
            return jsonify({'status': 'ready'})
        else:
            print('Updating instance')
            update_instance(mobile_number, {'status': 'Pending'})
            print('Updated the instance')
            return jsonify({'status': 'not ready'})
    except Exception as e:
        return error_response(500, str(e))
    
@app.route('/qr/image', methods=['GET'])
def redirect_to_home():
    mobile_number = request.args.get('mobile_number')
    return redirect(url_for('static', filename = f'/images/whatsapp_web_qr_{mobile_number}.png'))

@app.route('/register/qr/active', methods=['GET'])
def check_activation():
    try:
        mobile_number = request.args.get('mobile_number')

        # Check if the instance is activated
        instance = retrieve_instance(mobile_number)
        if instance != None and is_instance_ready(mobile_number):
            update_instance(mobile_number, {'status': 'Ready'})
            #read_text_message(mobile_number)
            return jsonify({'status': 'ready'})
        else:
            update_instance(mobile_number, {'status': 'Pending'})
            return jsonify({'status': 'not ready'})
    except Exception as e:
        return error_response(500, str(e))

@app.route('/instances', methods=['GET'])
def list_instances():
    try:
        print('Listing instances')
        # List all instances - in a real app, fetch this from a database
        # Function to filter and map the dictionary
        # Filtering out specific keys
        return get_all_instances()
    except Exception as e:
        return error_response(500, str(e))

@app.route('/instances/edit', methods=['GET'])
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

@app.route('/driver/update')
def driver_update():
    try:
        update_chrome_driver()
        return jsonify({'status': 'Done'})
    except Exception as e:
        return error_response(500, str(e))

@app.route('/message/text', methods=['POST'])
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
    
@app.route('/message/media', methods=['POST'])
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

app_home = os.path.abspath(os.path.dirname(__file__))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=30000)
