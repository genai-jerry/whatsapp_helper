from datetime import datetime
from flask import Blueprint, jsonify, render_template, request
from routers.sales import get_weekly_summary, get_pipeline
from store.employee_store import get_all_departments, get_all_employees
from store.opportunity_store import assign_opportunity_to_agent, get_all_opportunities_updated, list_all_leads_for_follow_up, list_all_leads_for_no_show, list_all_new_leads
from store.sales_store import get_hot_list
from store.tasks_store import get_tasks_due
from store.win_store import get_all_wins_for_date
from store.metrics_store import get_monthly_performance_for_agent
from store.metrics_store import get_projection_for_sales_agent_for_month
from utils import get_month_dates, get_month_number, get_month_year
from flask_login import current_user, login_required

review_blueprint = Blueprint('review', __name__)

@review_blueprint.route('/', methods=['GET'])
@review_blueprint.route('/<int:user_id>', methods=['GET'])
@login_required
def review(user_id=None):
    if not user_id:
        user_id = current_user.id
    current_date = datetime.now().strftime('%Y-%m-%d')
    wins = get_all_wins_for_date(current_date)
    departments = get_all_departments()
    context = {
        "wins": wins,
        "departments": departments
    }
    return render_template('review/review.html', **context)

@review_blueprint.route('sales-metrics', methods=['GET'])
@review_blueprint.route('sales-metrics/<int:user_id>', methods=['GET'])
@review_blueprint.route('sales-metrics/all', methods=['GET'])
@login_required
def get_sales_review_dashboard(user_id=None):
    context = get_sales_review_data(user_id)  
    return render_template('review/sales/sales.html', **context)

@review_blueprint.route('sales-metrics/all', methods=['GET'])
@login_required
def get_all_sales_review_dashboard():
    context = get_sales_review_data(None)  
    return render_template('review/sales/sales.html', **context)

def get_sales_review_data(user_id):
    selected_date = request.args.get('selected_date', 0, type=int)
    month = request.args.get('month', datetime.now().strftime('%B %Y'))
    month_name, year = get_month_year(month)
    month_number = get_month_number(month_name)
    hot_list_page = request.args.get('hot_list_page', 1, type=int)
    pipeline_page = request.args.get('pipeline_page', 1, type=int)
    tasks_due_page = request.args.get('tasks_due_page', 1, type=int)
    start_date, end_date = get_month_dates(month)
    
    weekly_summary, _ = get_weekly_summary(user_id, start_date, end_date)
    opportunities, hot_list_count = get_hot_list(user_id, hot_list_page, 10)
    pipeline, pipeline_count = get_pipeline(user_id, pipeline_page, 10)
    tasks_due, tasks_due_count = get_tasks_due(user_id, tasks_due_page, 10)
    employees = get_all_employees()
    print(f'Month: {month_number}, Year: {year}, User ID: {user_id}')
    projection = get_projection_for_sales_agent_for_month(user_id,month_name, year)
    monthly_performance = get_monthly_performance_for_agent(month_number, year, user_id)
    print(f'Monthly Performance: {monthly_performance}')
    performance_data = {
        'projection': projection,
        'weeks': monthly_performance['weeks'],
        'goal_month': monthly_performance['goal_month'],
        'projection_month': monthly_performance['projection_month'],
        'calls_month': monthly_performance['calls_month'],
        'apps_month': monthly_performance['apps_month']
    }
    context = {
        "weekly_summary": weekly_summary, 
        "opportunities": opportunities,
        "hot_list_count": hot_list_count,
        "pipeline": pipeline,
        "pipeline_count": pipeline_count,
        "tasks_due": tasks_due,
        "tasks_due_count": tasks_due_count,
        "hot_list_page": hot_list_page,
        "pipeline_page": pipeline_page,
        "tasks_due_page": tasks_due_page,
        "selected_date": selected_date,
        "month": month,
        "employees": employees,
        "selected_employee_id": user_id,
        "performance_data": performance_data
    }
    return context

@review_blueprint.route('call-setting')
@review_blueprint.route('call-setting/<int:agent_id>')
def get_call_setting_data(agent_id=None):
    employees = get_all_employees()
    assigned_leads_pages = request.args.get('assigned_leads_page', 1, type=int)
    assigned_follow_up_page = request.args.get('assigned_follow_up_page', 1, type=int)
    assigned_no_show_page = request.args.get('assigned_no_show_page', 1, type=int)
    pipeline_leads_pages = request.args.get('pipeline_leads_page', 1, type=int)
    pipeline_follow_up_pages = request.args.get('pipeline_follow_up_page', 1, type=int)
    pipeline_no_show_page = request.args.get('pipeline_no_show_page', 1, type=int)
    
    assigned_leads, assigned_leads_count = list_all_new_leads(assigned=True, agent_id=agent_id, page=assigned_leads_pages, page_size=10)
    assigned_follow_up, assigned_follow_up_count = list_all_leads_for_follow_up(assigned=True, agent_id=agent_id, page=assigned_follow_up_page, page_size=10)
    assigned_no_show, assigned_no_show_count = list_all_leads_for_no_show(assigned=True, agent_id=agent_id, page=assigned_no_show_page, page_size=10)
    pipeline_leads, pipeline_leads_count = list_all_new_leads(assigned=False, agent_id=None, page=pipeline_leads_pages, page_size=10)
    pipeline_follow_up, pipeline_follow_up_count = list_all_leads_for_follow_up(assigned=False, agent_id=None, page=pipeline_follow_up_pages, page_size=10)
    pipeline_no_show, pipeline_no_show_count = list_all_leads_for_no_show(assigned=False, agent_id=None, page=pipeline_no_show_page, page_size=10)

    update_counts = get_all_opportunities_updated(since_days=7, agent_id=agent_id)
    print(f'Update Counts: {update_counts}')
    return render_template('review/call_setting.html', 
                           update_counts=update_counts,
                           employees=employees,
                           assigned_leads=assigned_leads,
                           assigned_follow_up=assigned_follow_up,
                           assigned_no_show=assigned_no_show,
                           pipeline_leads=pipeline_leads,
                           pipeline_follow_up=pipeline_follow_up,
                           pipeline_no_show=pipeline_no_show,
                           assigned_leads_page=assigned_leads_pages,
                           assigned_follow_up_page=assigned_follow_up_page,
                           assigned_no_show_page=assigned_no_show_page,
                           pipeline_leads_page=pipeline_leads_pages,
                           pipeline_follow_up_page=pipeline_follow_up_pages,
                           pipeline_no_show_page=pipeline_no_show_page,
                           assigned_leads_count=assigned_leads_count,
                           assigned_follow_up_count=assigned_follow_up_count,
                           assigned_no_show_count=assigned_no_show_count,
                           pipeline_leads_count=pipeline_leads_count,
                           pipeline_follow_up_count=pipeline_follow_up_count,
                           pipeline_no_show_count=pipeline_no_show_count,
                           selected_employee_id=agent_id,
                           page_size=10)

@review_blueprint.route('call-setting/assign-lead', methods=['POST'])
def assign_lead():
    opportunity_id = request.form.get('opportunity_id')
    agent_id = request.form.get('agent_id')
    try:
        assign_opportunity_to_agent(opportunity_id, agent_id)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@review_blueprint.route('/api/opportunity/assign', methods=['POST'])
@login_required
def assign_opportunity():
    try:
        data = request.get_json()
        opportunity_id = data.get('opportunity_id')
        employee_id = data.get('employee_id')

        if not opportunity_id or not employee_id:
            return jsonify({'error': 'Missing required fields'}), 400

        # Update the opportunity in the database
        opportunity = OpportunityStore.assign_to_employee(opportunity_id, employee_id)
        
        if opportunity:
            return jsonify({
                'message': 'Opportunity assigned successfully',
                'opportunity': opportunity.to_dict()
            })
        else:
            return jsonify({'error': 'Failed to assign opportunity'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
