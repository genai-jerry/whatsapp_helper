from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import csv
from store.payment_store import store_sales

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