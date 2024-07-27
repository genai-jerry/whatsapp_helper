from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
import csv
from store.payment_store import store_sales
from store.sales_store import get_sales_data, mark_sale_final, mark_sale_not_final, get_monthly_sales_data
from store.payment_store import get_unassigned_payments
from routers.opportunity import get_opportunity_detail

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
    print(formatted_report)
    return jsonify(formatted_report), 200

@sales_blueprint.route('report/load')
def sales_report_load():
    return render_template('sales/report.html'), 200