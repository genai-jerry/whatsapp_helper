from flask import Blueprint, make_response, render_template, request, jsonify
from werkzeug.utils import secure_filename
import csv
from store.payment_store import store_sales, get_unassigned_payments
from store.sales_store import *
from routers.opportunity import get_opportunity_detail, get_opportunities
from utils import get_month_dates
from datetime import datetime, timedelta
# from store.metrics_store import get_sales_agent_performance

sales_blueprint = Blueprint('sales', __name__)

@sales_blueprint.route('/import', methods=['POST'])
def import_sales():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    filename = secure_filename(file.filename)
    file.save(filename)

    with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        sales = []
        for row in csv_reader:
            # Extract required items
            sale_details = {
                'email': row['Email'],
                'date': row['Date'],
                'gross': row['Gross'],
                'token': row['Token'],
                'comments': row['Comments']
            }
            sales.append(sale_details)
            # Process the extracted data here
            # For example, store in a database or perform some calculations
        store_sales(sales)
    return jsonify({'status': 'success', 'message': 'Sales data imported successfully'}), 200

@sales_blueprint.route('/')
def list_sales():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    opportunity_name = request.args.get('opportunity_name', '')
    sales_data, total_pages = get_sales_data(page, per_page, opportunity_name)
    unassigned_payments = get_unassigned_payments()
    return render_template('sales/list.html', sales=sales_data, page=page, 
                           total_pages=total_pages, unassigned_payments=unassigned_payments), 200

@sales_blueprint.route('<int:opportunity_id>/status/<int:sale_id>/<int:status>', methods=['POST'])
def mark_sale_status(opportunity_id, sale_id, status):
    # Perform logic to mark the sale as not final
    # For example, update the sale status in the database
    if status == 1:
        mark_sale_final(sale_id)
        return get_opportunity_detail(opportunity_id)
    elif status == 0:
        mark_sale_not_final(sale_id)
        return get_opportunity_detail(opportunity_id)
    
@sales_blueprint.route('report')
def sales_report():
    # Generate the sales report
    # For example, retrieve sales data from the database and format it
    formatted_report = get_monthly_sales_data()
    return jsonify(formatted_report), 200

@sales_blueprint.route('monthly/opportunities')
def monthly_sales_opportunities_report():
    print('Getting monthly report')
    month = request.args.get('month', datetime.now().strftime('%B %Y'))
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    first_day, last_day = get_month_dates(month)

    print(f'first_day: {first_day}, last_day: {last_day}, month: {month}')
    # Generate the sales report
    # For example, retrieve sales data from the database and format it
    formatted_sales_report, total_count = get_all_opportunities_with_final_sales(page, page_size, first_day, last_day)
    return jsonify({
        'formatted_sales_report': formatted_sales_report,
        'total_count': total_count
    }), 200

@sales_blueprint.route('monthly/payments')
def monthly_sales_opportunities_payments():
    month = request.args.get('month', datetime.now().strftime('%B %Y'))
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    print('Getting monthly report')
    first_day, last_day = get_month_dates(month)
    
    print(f'first_day: {first_day}, last_day: {last_day}, month: {month}')
    # Generate the sales report
    # For example, retrieve sales data from the database and format it
    formatted_payment_report, total_count = get_opportunities_for_payments_collected(page, page_size, first_day, last_day)
    return jsonify({
        'formatted_payment_report': formatted_payment_report,
        'total_count': total_count
    }), 200

@sales_blueprint.route('monthly/payments/call_setter')
def monthly_call_setter_opportunities_payments():
    month = request.args.get('month', datetime.now().strftime('%B %Y'))
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    print('Getting monthly report')
    first_day, last_day = get_month_dates(month)
    
    print(f'first_day: {first_day}, last_day: {last_day}, month: {month}')
    # Generate the sales report
    # For example, retrieve sales data from the database and format it
    formatted_payment_report, total_count = get_payments_oppotunities_by_call_setter(page, page_size, first_day, last_day)
    return jsonify({
        'formatted_payment_report': formatted_payment_report,
        'total_count': total_count
    }), 200

@sales_blueprint.route('monthly/payments/sales_agent')
def monthly_sales_agent_opportunities_payments():
    month = request.args.get('month', datetime.now().strftime('%B %Y'))
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    print('Getting monthly report')
    first_day, last_day = get_month_dates(month)
    
    print(f'first_day: {first_day}, last_day: {last_day}, month: {month}')
    # Generate the sales report
    # For example, retrieve sales data from the database and format it
    formatted_payment_report, total_count = get_payments_oppotunities_by_sales_agent(page, page_size, first_day, last_day)
    return jsonify({
        'formatted_payment_report': formatted_payment_report,
        'total_count': total_count
    }), 200

@sales_blueprint.route('monthly')
def monthly_report():
    selected_date = request.args.get('selected_date', 0, type=int)
    month = request.args.get('month', datetime.now().strftime('%B %Y'))
    print('Getting monthly report')
    first_day, last_day = get_month_dates(month)
    
    print(f'first_day: {first_day}, last_day: {last_day}, selected_date: {selected_date}, month: {month}')
    # Generate the sales report
    # For example, retrieve sales data from the database and format it
    formatted_sales_report = get_final_sales_for_month(first_day, last_day)
    formatted_payments_report_by_call_setters = get_payments_report_call_setters(first_day, last_day)
    formatted_payments_report_by_sales_agents = get_payments_report_sales_agents(first_day, last_day)
    payments_collected = get_payments_collected(first_day, last_day)
    return render_template('sales/report.html', 
                           formatted_sales_report=formatted_sales_report,
                           formatted_payments_report_by_call_setters=formatted_payments_report_by_call_setters,
                           formatted_payments_report_by_sales_agents=formatted_payments_report_by_sales_agents,
                           payments_collected=payments_collected, selected_date=int(selected_date)), 200

@sales_blueprint.route('report/load')
def sales_report_load():
    return render_template('sales/report.html'), 200

import pdfkit
@sales_blueprint.route('invoice/<int:payment_id>')
def generate_invoice(payment_id):
    # Invoice data
    invoice_data = get_invoice_data(payment_id)

    # Render the invoice HTML template
    rendered = render_template('sales/invoice/invoice.html', data=invoice_data)

    # Generate PDF from the rendered HTML
    pdf = pdfkit.from_string(rendered, False)

    # Send the PDF as a response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'

    return response

@sales_blueprint.route("/sales", methods=['GET'])
def get_sales_metrics():
    agent_id = request.args.get('agent_id', 1, type=int)  # Default to agent_id 1 if not provided
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    performance_data = [] # get_sales_agent_performance(agent_id, start_date, end_date)
    
    return render_template("metrics/sales.html", 
                           performance_data=performance_data,
                           agent_id=agent_id,
                           start_date=start_date,
                           end_date=end_date)
