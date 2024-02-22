from flask import jsonify

def error_response(status_code, message):
    response = jsonify({'error': message})
    response.status_code = status_code
    return response