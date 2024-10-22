from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from store.metrics_store import *
from store.employee_store import get_all_employees
from utils import get_month_year
from store.opportunity_store import get_total_opportunity_count_for_month

metrics_blueprint = Blueprint('metrics', __name__)

@metrics_blueprint.route('projections', methods=['GET'])
def projections():
    # Handle GET request
    selected_date = request.args.get('selected_date', 0, type=int)
    month = request.args.get('month', datetime.now().strftime('%B %Y'))
    print('Getting monthly report')
    month, year = get_month_year(month)
    employees = get_all_employees()
    print(f'month: {month}, year: {year}')
    projection_config = get_projection_config(month, year)
    sales_metrics = get_sales_kpi_for_month(month, year)
    performance_metrics = get_performance_metrics_for_sales_agent_for_month(month, year)
    opportunity_count = get_total_opportunity_count_for_month(month, year)
    print(f'performance_metrics: {performance_metrics}')
    print(f'projection_config: {projection_config}')
    return render_template('metrics/projections.html', 
                           projection_config=projection_config, employees=employees, 
                           sales_metrics=sales_metrics, performance_metrics=performance_metrics,
                           opportunity_count=opportunity_count,
                           selected_date=int(selected_date),
                           month=month,
                           year=year)

@metrics_blueprint.route('projections/<int:projection_id>', methods=['GET', 'PUT'])
def edit_projection(projection_id):
    projection = get_projection_by_id(projection_id)
    
    if request.method == 'PUT':
        # Create a new SalesProjections object
        return redirect(url_for('metrics.projections'))
    else:
        # Handle GET request
        return render_template('metrics/projections.html')

@metrics_blueprint.route('projections/config', methods=['POST'])
def edit_projection_config():
    month = request.args.get('month', datetime.now().strftime('%B'))
    year = request.args.get('year', datetime.now().year)
    
    projection_config_data = {
            "month": month,
            "year": year,
            "cost_per_lead": request.form['cost_per_lead'],
            "sale_price": request.form['sale_price'],
            "show_up_rate_goal": request.form['show_up_rate_goal'],
            "show_up_rate_projection": request.form['show_up_rate_projection'],
            "appointment_booked_goal": request.form['appointment_booked_goal'],
            "appointment_booked_projection": request.form['appointment_booked_projection']
        }
    update_projection_config(projection_config_data)
    return projections()
    
@metrics_blueprint.route('projections/employee/config', methods=['POST'])
def edit_employee_projection_config():
    month = request.args.get('month', datetime.now().strftime('%B'))
    year = request.args.get('year', datetime.now().year)
    
    projection_config_data = {
            "month": month,
            "year": year,
            "sales_agent_id": request.form['employee'],
            "sales_closed_goal": request.form['sales_closed_goal'],
            "sales_closed_projection": request.form['sales_closed_projection'],
            "total_calls_slots": request.form['total_calls_slots'],
            "sale_price": request.form['sale_price']
        }
    update_sales_agent_projections(projection_config_data)
    return projections()

# Add this new route
@metrics_blueprint.route('projections/<int:sales_agent_id>/config', methods=['GET'])
def get_sales_projection(sales_agent_id):
    month = request.args.get('month')
    year = request.args.get('year')

    projection = get_projection_for_sales_agent_for_month(sales_agent_id, month, year)

    return jsonify({'projection': projection})
