from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
import csv
from store.payment_store import store_sales
from store.sales_store import get_sales_data
from store.payment_store import get_unassigned_payments

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