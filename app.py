import os
from flask import Flask, render_template
from routers.driver import driver_blueprint
from routers.instance import instance_blueprint
from routers.message import message_blueprint
from routers.qr import qr_blueprint
from routers.template import template_blueprint
from routers.opportunity import opportunity_blueprint

app = Flask(__name__)

# Register the blueprints
app.register_blueprint(instance_blueprint, url_prefix='/instance')
app.register_blueprint(driver_blueprint, url_prefix='/driver')
app.register_blueprint(message_blueprint, url_prefix='/message')
app.register_blueprint(qr_blueprint, url_prefix='/qr')
app.register_blueprint(template_blueprint, url_prefix='/template')
app.register_blueprint(opportunity_blueprint, url_prefix='/opportunity')

@app.route('/')
def home():
    return render_template('index.html')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=30000, debug=True)