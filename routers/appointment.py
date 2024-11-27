from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from store.employee_store import get_all_employees
from utils import require_api_key
import csv
from utils import error_response
from werkzeug.utils import secure_filename
from store.appointment_store import *
from store.opportunity_store import get_all_opportunity_status

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
            'appointment_time': request.json.get('appointment_time', 'Not Set'),
            'appointment_number': request.json.get('whatsapp_number', 'Not Set')
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
def show_appointments():
    employees = get_all_employees()
    return render_template('/appointment/list.html', content={},
                           employees=employees, selected_employee_id=current_user.id)

@appointment_blueprint.route('/list', methods=['GET'])
@login_required
def list_appointments():
    # Add your logic to retrieve appointments
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    max_appointments = request.args.get('max', default=0, type=int)
    app_date = request.args.get('date', default=None, type=str)
    pages, total_items, appointments = retrieve_appointments(page, per_page, 
                                                             max_appointments, app_date)
    employees = get_all_employees()
    opportunity_statuses = get_all_opportunity_status()
    return jsonify({
        'appointments': appointments, 
        'opportunity_statuses': opportunity_statuses,
        'employees': employees,
        'page': page,
        'total_pages': pages,
        'selected_employee_id': current_user.id,
        'total_items': total_items
        }), 200

@appointment_blueprint.route('/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    cancel_saved_appointment(appointment_id)
    return jsonify({'status': 'success'}), 200

@appointment_blueprint.route('/<int:appointment_id>/confirm', methods=['POST'])
@login_required
def confirm_appointment(appointment_id):
    # Add your logic to confirm the appointment
    # You can update the appointment status in the database or perform any other necessary actions
    confirm_saved_appointment(appointment_id)
    return jsonify({'status': 'success'}), 200

@appointment_blueprint.route('/import', methods=['POST'])
@login_required
def import_appointments():
    print('Importing appointments')
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    filename = secure_filename(file.filename)
    file.save(filename)

    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            profile_details = {
                'name': row['Contact Name'],
                'email': row['Email'],
                'telephone': row['Phone'],
            }
            application_form_details = {
                'appointment_time': row['Requested Time'],
                'outcome': row['Outcome']
                # add other fields from the CSV file as needed
            }
            mentor_name = row['Appointment Owner']
            store_appointment(profile_details, application_form_details, mentor_name, True)

    return jsonify({'status': 'success'}), 200

@appointment_blueprint.route('status/<int:opportunity_id>/<int:appointment_id>', methods=['POST'])
@login_required
def set_appointment_status(opportunity_id, appointment_id):
    try:
        # Extract status from request body
        status = request.json.get('status')
        update_appointment_status(opportunity_id,appointment_id, status)
        print('Appointment Status Updated')
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))
    
@appointment_blueprint.route('/<int:appointment_id>/link', methods=['POST'])
@login_required
def set_appointment_link(appointment_id):
    opportunity_id = request.form.get('opportunity_id')
    print('Setting link for appointment:', appointment_id, 'to opportunity:', opportunity_id)
    update_appointment_link(appointment_id, opportunity_id)
    return show_appointments()