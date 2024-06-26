from flask import jsonify, Blueprint, request
from flask_login import login_required
from whatsapp.qr_code_generator import *
from whatsapp.whatsapp_automation import *
from browser.update_chrome import *
from store.instance_store import *
from xmlrpc.client import ServerProxy
from utils import error_response, require_api_key

driver_blueprint = Blueprint('driver', __name__)
# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

@driver_blueprint.route('/update')
@require_api_key
def driver_update():
    try:
        update_chrome_driver()
        return jsonify({'status': 'Done'})
    except Exception as e:
        return error_response(500, str(e))
