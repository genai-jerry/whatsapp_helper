from flask import jsonify, Blueprint, request, render_template
from whatsapp.qr_code_generator import *
from whatsapp.whatsapp_automation import *
from browser.update_chrome import *
from store.template_store import *

template_blueprint = Blueprint('template', __name__)

@template_blueprint.route('/')
def home():
    return render_template('templates.html')

@template_blueprint.route('/new')
def new():
    return render_template('template.html')

@template_blueprint.route('/activate')
def activate():
    print(f'Updating the template {request.form}')
    id = request.args["id"]
    activate_template(id)
    return render_template('templates.html')

@template_blueprint.route('/deactivate')
def deactivate():
    print(f'Updating the template {request.form}')
    id = request.args["id"]
    deactivate_template(id)
    return render_template('templates.html')

@template_blueprint.route('/', methods=['POST'])
def save_template():
    print('Saving Template')
    name = request.form['name']
    template = request.form['text']
    print(f'Name: {name} : Template : {template}')
    store_template({'name': name, 'template_text': template})
    return render_template('templates.html')

@template_blueprint.route('/edit')
def load_edit_template():
    print('Loading Template')
    id = request.args['id']
    template = retrieve_template(id)
    print(template)
    return render_template('template_edit.html', content=template)

@template_blueprint.route('/edit', methods=['POST'])
def edit_template():
    print('Updating Template')
    id = request.form['id']
    template = request.form['text']
    update_template({'id': id, 'template_text': template})
    return render_template('templates.html')

@template_blueprint.route('/list')
def list_templates():
    return get_all_templates()

def error_response(status_code, message):
    response = jsonify({'error': message})
    response.status_code = status_code
    return response