from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from routers.opportunity import get_opportunities
from routers.sales import get_weekly_summary, get_opportunities, get_pipeline
from store.sales_store import get_hot_list
from store.tasks_store import get_tasks_due
from store.win_store import get_all_wins_for_date
from utils import get_month_dates

review_blueprint = Blueprint('review', __name__)

@review_blueprint.route('/', methods=['GET'])
def get_review_dashboard():
    context = get_review_data(None)
    return render_template('review/dashboard.html', **context)

@review_blueprint.route('sales/<int:user_id>', methods=['GET'])
def get_sales_review_dashboard_for_user(user_id):  
    context = get_review_data(user_id)
    return render_template('review/sales_metrics.html', **context)

@review_blueprint.route('sales', methods=['GET'])
def get_sales_review_dashboard():
    context = get_review_data(None)
    return render_template('review/sales_metrics.html', **context)

def get_review_data(user_id):
    selected_date = request.args.get('selected_date', 0, type=int)
    month = request.args.get('month', datetime.now().strftime('%B %Y'))
    hot_list_page = request.args.get('hot_list_page', 1, type=int)
    pipeline_page = request.args.get('pipeline_page', 1, type=int)
    tasks_due_page = request.args.get('tasks_due_page', 1, type=int)
    start_date, end_date = get_month_dates(month)
    current_date = datetime.now().strftime('%Y-%m-%d')
    wins = get_all_wins_for_date(current_date)
    weekly_summary, _ = get_weekly_summary(start_date, end_date)
    opportunities, hot_list_count = get_hot_list(hot_list_page, 10)
    pipeline, pipeline_count = get_pipeline(pipeline_page, 10)
    tasks_due, tasks_due_count = get_tasks_due(user_id,tasks_due_page, 10)

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
        "wins": wins
    }
    return context