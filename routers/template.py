from flask import jsonify, Blueprint, request, render_template
from qr_code_generator import *
from whatsapp_automation import *
from update_chrome import *
from instance_store import *
from xmlrpc.client import ServerProxy

template_blueprint = Blueprint('template', __name__)
# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

templates = []

@template_blueprint.route('/')
def home():
    return render_template('templates.html')

@template_blueprint.route('/new')
def new():
    return render_template('template.html')

@template_blueprint.route('/edit')
def edit():
    id = request.args.get("id")
    print(f'Editing {id}')
    return render_template('template_edit.html', content=templates[0])

@template_blueprint.route('/edit', methods=['POST'])
def update():
    print(f'Updating the template {request.form}')
    id = request.form["id"]
    print(f'Updating {id}')
    name = request.form['name']
    template = request.form['text']
    print(f'Name: {name} : Template : {template}')
    return render_template('templates.html')

@template_blueprint.route('/', methods=['POST'])
def save_template():
    print('Saving Template')
    name = request.form['name']
    template = request.form['text']
    print(f'Name: {name} : Template : {template}')
    templates.append({'name': name, 'text': template})
    return render_template('templates.html')

@template_blueprint.route('/list')
def list_templates():
    return templates

def error_response(status_code, message):
    response = jsonify({'error': message})
    response.status_code = status_code
    return response
