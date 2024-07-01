from flask import Blueprint, Flask, render_template, request, jsonify
from flask_login import login_required
from store.payment_store import store_payment, list_payments_for_sale
from werkzeug.utils import secure_filename
import csv
app = Flask(__name__)

payments_blueprint = Blueprint('payments', __name__)

@payments_blueprint.route('<int:opportunity_id>/<int:sale_id>', methods=['POST'])
def record_payment(opportunity_id, sale_id):
    # Assuming the form data is sent as application/x-www-form-urlencoded
    # Extracting form data
    payment_data = {
        'payment_date': request.form.get('payment_date'),
        'payment_amount': request.form.get('payment_amount'),
        'charges': request.form.get('charges'),
        'payment_mode': request.form.get('payment_mode'),
        'invoice_link': request.form.get('invoice_link'),
        'is_deposit': True if request.form.get('is_deposit') == 'on' else False
    }

    # Process the payment data (e.g., store in database)
    # This function should be defined elsewhere in your application
    store_payment(sale_id, payment_data)

    # Return a success response
    return list_payments(opportunity_id, sale_id)

@payments_blueprint.route('/import', methods=['POST'])
@login_required
def import_payments():
    print('Importing payments')
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    filename = secure_filename(file.filename)
    file.save(filename)

    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        payments = []
        for row in reader:
            payment_details = {
                'email': row['Email'],
                'payment_date': row['Payment Date'],
                'invoice_number': row['Invoice Number'],
                'payment_amount': row['Payment Amount'],
                'GST': row['GST'],
                'link': row['link'],
            }
            payments.append(payment_details)
            # Process payment_details as needed, e.g., store in database
        # store_payment(sale_id, payment_details)
    return jsonify({'status': 'success'}), 200

@payments_blueprint.route('<int:opportunity_id>/<int:sale_id>', methods=['GET'])
def list_payments(opportunity_id, sale_id):
    payments = list_payments_for_sale(sale_id)
    return render_template('payments/view.html', payments=payments, sale_id=sale_id, opportunity_id=opportunity_id), 200