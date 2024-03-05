import os
from flask import Flask, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from routers.driver import driver_blueprint
from routers.instance import instance_blueprint
from routers.message import message_blueprint
from routers.qr import qr_blueprint
from routers.template import template_blueprint
from routers.opportunity import opportunity_blueprint
from flask_migrate import Migrate
import configparser

# Read the config.ini file
config = configparser.ConfigParser()
config.read('config/config.ini')
# Get the MySQL configuration
mysql_config = config['mysql']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}/{mysql_config['database']}"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import *

# Register the blueprints
app.register_blueprint(instance_blueprint, url_prefix='/instance')
app.register_blueprint(driver_blueprint, url_prefix='/driver')
app.register_blueprint(message_blueprint, url_prefix='/message')
app.register_blueprint(qr_blueprint, url_prefix='/qr')
app.register_blueprint(template_blueprint, url_prefix='/template')
app.register_blueprint(opportunity_blueprint, url_prefix='/opportunity')

@app.route('/')
def home():
    return redirect('/opportunity')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=30000, debug=True)