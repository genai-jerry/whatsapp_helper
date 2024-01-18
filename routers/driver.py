from flask import jsonify, Blueprint, request
from whatsapp.qr_code_generator import *
from whatsapp.whatsapp_automation import *
from browser.update_chrome import *
from store.instance_store import *
from xmlrpc.client import ServerProxy

driver_blueprint = Blueprint('driver', __name__)
# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

def error_response(status_code, message):
    response = jsonify({'error': message})
    response.status_code = status_code
    return response

@driver_blueprint.route('/update')
def driver_update():
    try:
        update_chrome_driver()
        return jsonify({'status': 'Done'})
    except Exception as e:
        return error_response(500, str(e))
