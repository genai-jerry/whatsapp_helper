from flask import jsonify, Blueprint, request, render_template
from flask_login import login_required
from store.opportunity_store import generate_report, generate_metrics

dashboard_blueprint = Blueprint('dashboard', __name__)

@dashboard_blueprint.route('/')
@login_required
def report():
    return render_template('/report/dashboard.html')

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