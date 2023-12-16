from flask import Flask, jsonify, request, render_template, url_for, redirect, make_response
from qr_code_generator import *
from whatsapp_automation import *
from update_chrome import *
import threading
# Create a lock to synchronize access to a resource
resource_lock = threading.Lock()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/instances/home')
def show_instances():
    return render_template('instance.html')

# Placeholder for storing instances - in a real application, use a database
instances = {}

@app.route('/register/qr', methods=['POST'])
def register_qr():
    try:
        data = request.json
        mobile_number = data.get('mobileNumber')
        user_name = data.get('userName')
        instance = instances.get(mobile_number)
        if instance == None:
            print('Creating new instance')
            browser = create_instance(app_home)
            instances[mobile_number] = {'mobile_number': mobile_number, 'status': 'Pending', 'browser': browser, 'name': user_name}
        else:
            if is_instance_ready(instance['browser']):
                return jsonify({'status': 'ready', 'message': 'Instance creation initiated', 'mobileNumber': mobile_number})
        # Start a new thread for loading the QR code
        thread = threading.Thread(target=load_qr_code, args=(browser, mobile_number))
        thread.start()

        # Respond with a successful creation message or similar
        return jsonify({'status': 'pending', 'message': 'Instance creation initiated', 'mobileNumber': mobile_number})
    except Exception as e:
        error_response(500, str(e))

@app.route('/register/qr', methods=['GET'])
def get_qr_code():
    try:
        mobile_number = request.args.get('mobile_number')

        # Check if the instance exists and if the QR code is ready
        instance = instances.get(mobile_number)
        
        if instance != None:
            # In a real application, provide the URL or path to the generated QR code
            load_qr_code(instance['browser'], mobile_number)
            instance['status'] = 'Ready'
            return jsonify({'status': 'ready'})
        else:
            instance['status'] = 'Pending'
            return jsonify({'status': 'not ready'})
    except Exception as e:
        error_response(500, str(e))
    
@app.route('/qr/image', methods=['GET'])
def redirect_to_home():
    mobile_number = request.args.get('mobile_number')
    return redirect(url_for('static', filename = f'/images/whatsapp_web_qr_{mobile_number}.png'))

@app.route('/register/qr/active', methods=['GET'])
def check_activation():
    try:
        mobile_number = request.args.get('mobile_number')

        # Check if the instance is activated
        instance = instances.get(mobile_number)
        if instance != None and is_instance_ready(instance['browser']):
            instance['status'] = 'Ready'
            return jsonify({'status': 'ready'})
        else:
            instance['status'] = 'Pending'
            return jsonify({'status': 'not ready'})
    except Exception as e:
        error_response(500, str(e))

@app.route('/instances', methods=['GET'])
def list_instances():
    try:
        # List all instances - in a real app, fetch this from a database
        # Function to filter and map the dictionary
        # Filtering out specific keys
        keys_to_exclude = ['browser']

        # Using list comprehension to map and filter
        data = [{k: v for k, v in sub_dict.items() if k not in keys_to_exclude} for sub_dict in instances.values()]
        # Apply the function to the data
        return jsonify(data)
    except Exception as e:
        error_response(500, str(e))

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
        error_response(500, str(e))

@app.route('/message/text', methods=['POST'])
def text_message():
    try:
        data = request.json
        mobile_number = data.get('mobile_number')
        contact_name = data.get('contact_name')
        message = data.get('message')
        instance = instances.get(mobile_number)
        if instance == None:
            return error_response(400, 'No instance available for the number')
        if is_instance_ready(instance['browser']):
            try:
                with resource_lock:
                    browser = instance['browser']
                    send_whatsapp_message(browser, contact_name, message)
                    return jsonify({'status': 'Done'})
            except RuntimeError as e:
                return error_response(400, str(e))
        else:
            return error_response(400, 'Instance is not ready for the number')
    except Exception as e:
        error_response(500, str(e))
    
@app.route('/message/media', methods=['POST'])
def media_message():
    try:
        data = request.json
        mobile_number = data.get('mobile_number')
        contact_name = data.get('contact_name')
        url = data.get('url')
        instance = instances.get(mobile_number)
        if instance == None:
            return error_response(400, 'No instance available for the number')
        if is_instance_ready(instance['browser']):
            with resource_lock:
                browser = instance['browser']
                send_media_whatsapp_message(browser, contact_name, url)
                return jsonify({'status': 'Done'})
        else:
            return error_response(400, 'Instance is not ready for the number')
    except Exception as e:
        error_response(500, str(e))

app_home = os.path.abspath(os.path.dirname(__file__))
if __name__ == '__main__':
    app.run(debug=True)
