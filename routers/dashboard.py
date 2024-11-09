from flask import jsonify, Blueprint, request, render_template
from flask_login import current_user, login_required
from store.appointment_store import get_all_appointment_status, list_all_appointments_for_confirmation
from store.opportunity_store import generate_report, generate_metrics, get_all_call_status, list_all_leads_for_follow_up, list_all_leads_for_no_show, list_all_new_leads
from store.tasks_store import get_tasks_due
from store.employee_store import get_all_employees
from datetime import datetime
dashboard_blueprint = Blueprint('dashboard', __name__)

@dashboard_blueprint.route('/')
@login_required
def report():
    tasks_due_page = request.args.get('tasks_due_page', 1, type=int)
    assigned_follow_up_page = request.args.get('assigned_follow_up_page', 1, type=int)
    assigned_leads_pages = request.args.get('assigned_leads_page', 1, type=int)
    assigned_follow_up_page = request.args.get('assigned_follow_up_page', 1, type=int)
    assigned_no_show_page = request.args.get('assigned_no_show_page', 1, type=int)
    assigned_appointments_page = request.args.get('assigned_appointments_page', 1, type=int)
    
    user_id = current_user.id
    tasks_due, tasks_due_count = get_tasks_due(user_id, tasks_due_page, 10)
    assigned_leads, assigned_leads_count = list_all_new_leads(assigned=True, user_id=user_id, page=assigned_leads_pages, page_size=10)
    assigned_follow_up, assigned_follow_up_count = list_all_leads_for_follow_up(assigned=True, user_id=user_id, page=assigned_follow_up_page, page_size=10)
    assigned_no_show, assigned_no_show_count = list_all_leads_for_no_show(assigned=True, user_id=user_id, page=assigned_no_show_page, page_size=10)
    assigned_appointments, assigned_appointments_count = list_all_appointments_for_confirmation(assigned=True, user_id=user_id, page=assigned_appointments_page, page_size=10)
    employees = get_all_employees()
    call_statuses = get_all_call_status()
    appointment_statuses = get_all_appointment_status()
    return render_template('/report/dashboard.html', tasks_due=tasks_due, tasks_due_count=tasks_due_count, 
                           employees=employees, selected_employee_id=current_user.id,
                           call_statuses=call_statuses,
                           appointment_statuses=appointment_statuses,
                           assigned_follow_up=assigned_follow_up, 
                           assigned_follow_up_count=assigned_follow_up_count,
                           assigned_appointments=assigned_appointments, 
                           assigned_appointments_count=assigned_appointments_count,
                           assigned_no_show=assigned_no_show,
                           assigned_no_show_count=assigned_no_show_count,
                           assigned_leads=assigned_leads,
                           assigned_leads_count=assigned_leads_count,
                           assigned_leads_page=assigned_leads_pages,
                           assigned_follow_up_page=assigned_follow_up_page,
                           assigned_no_show_page=assigned_no_show_page,
                           assigned_appointments_page=assigned_appointments_page,
                           current_date=datetime.now(),
                           page_size=10)

from flask import jsonify
import json

@dashboard_blueprint.route('/report')
@login_required
def report_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    report = generate_report(start_date, end_date)
    
    # Convert the report dictionary to JSON
    report_json = json.dumps(report)
    print(f'Report: {report_json}')
    # Return the JSON response
    return jsonify(report_json)

@dashboard_blueprint.route('/metrics')
@login_required
def metrics_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    metrics = generate_metrics(start_date, end_date)
    
    # Convert the metrics dictionary to JSON
    metrics_json = json.dumps(metrics)
    print(f'Metrics: {metrics_json}')
    # Return the JSON response
    return jsonify(metrics_json)