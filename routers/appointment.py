from flask import Blueprint, request, jsonify
from flask_login import login_required
from utils import require_api_key
from store.appointment_store import store_appointment

appointment_blueprint = Blueprint('appointment', __name__)

@appointment_blueprint.route('/', methods=['POST'])
@require_api_key
def create_new_appointment():
    try:
        # Extract details from request body
        profile_details = {
            'name': request.json.get('name'),
            'email': request.json.get('email'),
            'telephone': request.json.get('phone')
        }
        mentor_name = request.json.get('mentor_name')
        application_form_details = {
            'career_challenge': request.json.get('career_challenge'),
            'challenge_description': request.json.get('challenge_description'),
            'urgency': request.json.get('urgency'),
            'salary_range': request.json.get('salary_range'),
            'expected_salary': request.json.get('expected_salary'),
            'current_employer': request.json.get('current_employer'),
            'financial_situation': request.json.get('financial_situation'),
            'availability': request.json.get('availability'),
            'whatsapp_number': request.json.get('whatsapp_number')
        }

        # Create new appointment in database
        store_appointment(profile_details, application_form_details, mentor_name)

        # Return response
        return jsonify({
            'status': 'success'
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@appointment_blueprint.route('/', methods=['GET'])
@require_api_key
@login_required
def list_appointments():
    # Add your logic to retrieve appointments
    # ...
    return jsonify({'status': 'success'}), 200

@appointment_blueprint.route('/<int:appointment_id>', methods=['PUT'])
@require_api_key
@login_required
def update_appointment(appointment_id):
    data = request.json
    # Add your logic to update the appointment
    # ...
    return jsonify({'status': 'success'}), 200