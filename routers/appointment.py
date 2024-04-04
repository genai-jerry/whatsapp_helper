from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from utils import require_api_key
from store.appointment_store import store_appointment, retrieve_appointments, cancel_saved_appointment

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
            'career_challenge': request.json.get('career_challenge', 'Not Set'),
            'challenge_description': request.json.get('challenge_description', 'Not Set'),
            'urgency': request.json.get('urgency', 'Not Set'),
            'salary_range': request.json.get('salary_range', 'Not Set'),
            'expected_salary': request.json.get('expected_salary', 'Not Set'),
            'current_employer': request.json.get('current_employer', 'Not Set'),
            'financial_situation': request.json.get('financial_situation', 'Not Set'),
            'availability': request.json.get('availability', 'Not Set'),
            'whatsapp_number': request.json.get('whatsapp_number', 'Not Set'),
            'appointment_time': request.json.get('appointment_time', 'Not Set')
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

@appointment_blueprint.route('/')
@login_required
def show_instances():
    return render_template('/appointment/list.html', content={})

@appointment_blueprint.route('/list', methods=['GET'])
@login_required
def list_appointments():
    # Add your logic to retrieve appointments
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    pages, total_items, appointments = retrieve_appointments(page_number=page, page_size=per_page)
    print(f'Appointments: {appointments}, page: {page}, total_pages: {pages}, total_items: {total_items}')
    return jsonify({
        'appointments': appointments, 
        'page': page,
        'total_pages': pages,
        'total_items': total_items}), 200

@appointment_blueprint.route('/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    cancel_saved_appointment(appointment_id)
    return jsonify({'status': 'success'}), 200