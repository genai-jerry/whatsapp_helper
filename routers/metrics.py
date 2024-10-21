from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from store.metrics_store import *
from store.employee_store import get_all_employees

metrics_blueprint = Blueprint('metrics', __name__)

@metrics_blueprint.route('projections', methods=['GET'])
def projections():
    # Handle GET request
    month = request.args.get('month', datetime.now().strftime('%B'))
    year = request.args.get('year', datetime.now().year)
    employees = get_all_employees()
    print(f'month: {month}, year: {year}')
    projection_config = get_projection_config(month, year)
    print(f'projection_config: {projection_config}')
    return render_template('metrics/projections.html', projection_config=projection_config, employees=employees
                               )
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
            "sale_price": request.form['sale_price']
        }
    update_projection_config(projection_config_data)
    return projections()
    
@metrics_blueprint.route('projections/<int:employee_id>/config', methods=['POST'])
def edit_employee_projection_config(employee_id):
    month = request.args.get('month', datetime.now().strftime('%B'))
    year = request.args.get('year', datetime.now().year)
    
    projection_config_data = {
            "month": month,
            "year": year,
            "sales_agent_id": employee_id,
            "show_up_rate_goal": request.form['show_up_rate_goal'],
            "show_up_rate_projection": request.form['show_up_rate_projection'],
            "sales_closed_goal": request.form['sales_closed_goal'],
            "sales_closed_projection": request.form['sales_closed_projection'],
            "total_sales_goal": request.form['total_sales_goal'],
            "total_sales_projection": request.form['total_sales_projection'],
            "total_calls_goal": request.form['total_calls_goal']
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
