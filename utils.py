import os
from flask import jsonify

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
app_home = os.path.abspath(os.path.join(current_dir, os.pardir))

def error_response(status_code, message):
    response = jsonify({'error': message})
    response.status_code = status_code
    return response