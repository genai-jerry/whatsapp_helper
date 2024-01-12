from flask import jsonify
from xmlrpc.client import ServerProxy
from db.connection_manager import *

def store_template(user_data):
    save_template(user_data['name'], user_data['template_text'])

def update_template(user_data):
    update_template_text(user_data['id'], user_data['template_text'])

def deactivate_template(id):
    update_template_status(id, False)

def activate_template(id):
    update_template_status(id, True)

def retrieve_templates():
    return load_all_templates()

def retrieve_template(id):
    return load_template(id)

def retrieve_template_by_name(name):
    return load_template_by_name(name)

def get_all_templats():
    print('Getting Templates')
    return load_all_templates()
    


