from datetime import datetime
from flask import Flask, g, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import pytz
from routers.driver import driver_blueprint
from routers.instance import instance_blueprint
from routers.message import message_blueprint
from routers.models import SystemUser
from routers.appointment import appointment_blueprint
from routers.qr import qr_blueprint
from routers.template import template_blueprint
from routers.dashboard import dashboard_blueprint
from routers.opportunity import opportunity_blueprint
from routers.payment import payments_blueprint
from routers.sales import sales_blueprint
from routers.review import review_blueprint
from routers.task import task_blueprint
from routers.win import win_blueprint
from routers.comment import comment_blueprint
from flask_migrate import Migrate
import configparser
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_login import current_user
from store.user_store import create_new_user, load_user_by_username
from utils import require_api_key
from dateutil.relativedelta import *

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
app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')
app.register_blueprint(payments_blueprint, url_prefix='/payments')
app.register_blueprint(sales_blueprint, url_prefix='/sales')
app.register_blueprint(review_blueprint, url_prefix='/review')
app.register_blueprint(task_blueprint, url_prefix='/task')
app.register_blueprint(win_blueprint, url_prefix='/win')
app.register_blueprint(comment_blueprint, url_prefix='/comment')

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
    return redirect('/dashboard')

@app.route('/user', methods=['POST'])
@require_api_key
def create_user():
    username = request.form['username']
    password = request.form['password']
    create_new_user(username, password)
    return 'User created successfully', 201

@login_manager.user_loader
def load_user(user_id):
    user = load_user_by_username(user_id)
    if user:
        return SystemUser(user['id'], user['username'], user['password'])
    else:
        return None

@app.route('/import', methods=['GET'])
@login_required
def show_import():
    return render_template('import.html', content={})

@app.route('/login', methods=['POST'])
def login():
    # Authenticate the user and start a session
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
    
@app.template_filter()
def number_format(value):
    converted_value = format(int(value), ',d')
    return converted_value

@app.template_filter()
def excl_tax(value):
    return int(value) / 1.18

@app.template_filter()
def tax(value):
    return value - excl_tax(value)

@app.template_filter()
def format_date(value):
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value  # Return the original string if it can't be parsed
    
    formatted_date = value.strftime('%d %b')
    return formatted_date

@app.template_filter()
def format_date_time(value):
    formatted_date = value.strftime('%d %b %Y %H:%M')
    return formatted_date

@app.template_filter()
def convert_to_date(value):
    print(f'value: {value}')
    return value.strftime('%d %b %Y')

@app.template_filter()
def convert_to_ist(utc_dt):
    """
    Convert a datetime object from UTC to IST (Indian Standard Time).
    
    :param utc_dt: datetime object in UTC
    :return: datetime object in IST
    """
    if utc_dt is None:
        return None
    
    utc = pytz.UTC
    ist = pytz.timezone('Asia/Kolkata')
    
    # Ensure the input datetime is UTC
    if utc_dt.tzinfo is None or utc_dt.tzinfo.utcoffset(utc_dt) is None:
        utc_dt = utc.localize(utc_dt)
    
    # Convert to IST
    ist_dt = utc_dt.astimezone(ist)
    
    return ist_dt

from datetime import timedelta
@app.template_filter()
def date_add(value):
    if not value:
        value = 0
    today = datetime.now().date()
    new_date = today + timedelta(days=value)
    return new_date.strftime('%a, %d %b')

@app.template_filter()
def month_add(value):
    if not value:
        value = 0
    today = datetime.now().date()
    new_date = today - relativedelta(months=value)
    return new_date.strftime('%B %Y')

@app.template_filter()
def round_up(value):
    return round(value)

@app.template_filter()
def round_down(value):
    return int(value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=30000, debug=True)