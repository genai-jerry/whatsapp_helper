import os
from flask import Flask, g, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from routers.driver import driver_blueprint
from routers.instance import instance_blueprint
from routers.message import message_blueprint
from routers.models import SystemUser
from routers.appointment import appointment_blueprint
from routers.qr import qr_blueprint
from routers.template import template_blueprint
from routers.opportunity import opportunity_blueprint
from flask_migrate import Migrate
import configparser
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_login import current_user
from store.user_store import create_new_user, load_user_by_username

# Read the config.ini file
config = configparser.ConfigParser()
config.read('config/config.ini')
# Get the MySQL configuration
mysql_config = config['mysql']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}/{mysql_config['database']}"
app.config['SECRET_KEY'] = 'commserver'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import *
from werkzeug.security import generate_password_hash

# Register the blueprints
app.register_blueprint(instance_blueprint, url_prefix='/instance')
app.register_blueprint(driver_blueprint, url_prefix='/driver')
app.register_blueprint(message_blueprint, url_prefix='/message')
app.register_blueprint(qr_blueprint, url_prefix='/qr')
app.register_blueprint(template_blueprint, url_prefix='/template')
app.register_blueprint(opportunity_blueprint, url_prefix='/opportunity')
app.register_blueprint(appointment_blueprint, url_prefix='/appointment')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_request
def before_request():
    g.user_logged_in = current_user.is_authenticated

@app.route('/login')
def home():
    return render_template("login.html")

@app.route('/')
def index():
    return redirect('/opportunity')

@app.route('/user', methods=['POST'])
def create_user():
    username = request.form['username']
    password = request.form['password']
    create_new_user(username, password)
    return 'User created successfully', 201

@login_manager.user_loader
def load_user(user_id):
    print(f'loading user {user_id}')
    user = load_user_by_username(user_id)
    if user:
        return SystemUser(user['id'], user['username'], user['password'])
    else:
        return None

@app.route('/login', methods=['POST'])
def login():
    # Authenticate the user and start a session
    print(request.form)
    user = load_user(request.form['username'])
    password = request.form['password']
    if user and user.check_password(password):
        print('Logging in user')
        try:
            login_user(user)
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            print(str(e))
            return jsonify({'status': 'Invalid user name or password'}), 400
    else:
        return jsonify({'status': 'Invalid user name or password'}), 400

@app.route('/logout')
@login_required
def logout():
    # End the session
    logout_user()
    return redirect('/login')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=30000, debug=True)