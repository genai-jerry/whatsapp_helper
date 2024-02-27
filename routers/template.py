from flask import jsonify, Blueprint, request, render_template
from whatsapp.qr_code_generator import *
from whatsapp.whatsapp_automation import *
from browser.update_chrome import *
from store.template_store import *
from utils import error_response

template_blueprint = Blueprint('template', __name__)

@template_blueprint.route('/')
def home():
    return render_template('message/templates.html')

@template_blueprint.route('/new')
def new():
    return render_template('template.html')

@template_blueprint.route('/activate')
def activate():
    print(f'Updating the template {request.form}')
    id = request.args["id"]
    activate_template(id)
    return render_template('message/templates.html')

@template_blueprint.route('/deactivate')
def deactivate():
    print(f'Updating the template {request.form}')
    id = request.args["id"]
    deactivate_template(id)
    return render_template('message/templates.html')

@template_blueprint.route('/', methods=['POST'])
def save_template():
    print('Saving Template')
    name = request.form['name']
    template = request.form['text']
    print(f'Name: {name} : Template : {template}')
    store_template({'name': name, 'template_text': template})
    return render_template('message/templates.html')

@template_blueprint.route('/edit')
def load_edit_template():
    print('Loading Template')
    id = request.args['id']
    template = retrieve_template(id)
    print(template)
    return render_template('message/template_edit.html', content=template)

@template_blueprint.route('/edit', methods=['POST'])
def edit_template():
    print('Updating Template')
    id = request.form['id']
    template = request.form['text']
    update_template({'id': id, 'template_text': template})
    return render_template('message/templates.html')

@template_blueprint.route('/list')
def list_templates():
    return get_all_templates()

@template_blueprint.route('/<template_name>')
def get_template(template_name):
    template = retrieve_template(template_name)
    if template:
        return jsonify(template)
    else:
        return error_response('Template not found', 404)

