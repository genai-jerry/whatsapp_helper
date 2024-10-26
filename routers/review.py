from datetime import datetime
from flask import Blueprint, render_template, request
from routers.sales import get_weekly_summary, get_pipeline
from store.employee_store import get_all_departments, get_all_employees
from store.sales_store import get_hot_list
from store.tasks_store import get_tasks_due
from store.win_store import get_all_wins_for_date
from utils import get_month_dates
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
    return render_template('metrics/review.html', **context)

@review_blueprint.route('sales-metrics', methods=['GET'])
@review_blueprint.route('sales-metrics/<int:user_id>', methods=['GET'])
@review_blueprint.route('sales-metrics/all', methods=['GET'])
@login_required
def get_sales_review_dashboard(user_id=None):
    context = get_sales_review_data(user_id)  
    return render_template('metrics/sales.html', **context)

@review_blueprint.route('sales-metrics/all', methods=['GET'])
@login_required
def get_all_sales_review_dashboard():
    context = get_sales_review_data(None)  
    return render_template('metrics/sales.html', **context)

def get_sales_review_data(user_id):
    selected_date = request.args.get('selected_date', 0, type=int)
    month = request.args.get('month', datetime.now().strftime('%B %Y'))
    hot_list_page = request.args.get('hot_list_page', 1, type=int)
    pipeline_page = request.args.get('pipeline_page', 1, type=int)
    tasks_due_page = request.args.get('tasks_due_page', 1, type=int)
    start_date, end_date = get_month_dates(month)
    year = start_date.year
    weekly_summary, _ = get_weekly_summary(user_id, start_date, end_date)
    opportunities, hot_list_count = get_hot_list(user_id, hot_list_page, 10)
    pipeline, pipeline_count = get_pipeline(user_id, pipeline_page, 10)
    tasks_due, tasks_due_count = get_tasks_due(user_id, tasks_due_page, 10)
    employees = get_all_employees()
    monthly_performance = get_performance_metrics_for_sales_agent_for_month(user_id, month, year)
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
        "selected_employee_id": user_id
    }
    return context