from flask import Blueprint, Flask, render_template, request, jsonify
from flask_login import login_required
from flask_login import login_required
from store.payment_store import *
from store.opportunity_store import get_opportunity_by_id
from werkzeug.utils import secure_filename
import csv
from werkzeug.utils import secure_filename
import csv

from utils import require_api_key
app = Flask(__name__)

payments_blueprint = Blueprint('payments', __name__)

@payments_blueprint.route('<int:opportunity_id>/<int:sale_id>', methods=['POST'])
@login_required
def manage_payments(opportunity_id, sale_id):
    # Assuming the form data is sent as application/x-www-form-urlencoded
    # Extracting form data
    payment_data = {
        'payment_date': request.form.get('payment_date'),
        'payment_amount': request.form.get('payment_amount'),
        'charges': request.form.get('charges'),
        'payment_mode': request.form.get('payment_mode'),
        'invoice_link': request.form.get('invoice_link'),
        'is_deposit': True if request.form.get('is_deposit') == 'on' else False,
        'opportunity_id': opportunity_id
    }

    # Process the payment data (e.g., store in database)
    # This function should be defined elsewhere in your application
    store_payment(sale_id, payment_data)

    # Return a success response
    return list_payments(opportunity_id, sale_id)

@payments_blueprint.route('assign', methods=['POST'])
@login_required
def assign_payment():
    # Assuming the form data is sent as application/x-www-form-urlencoded
    # Extracting form data
    payment_id = request.form.get('payment_id')
    sale_id = request.form.get('sale_id')
    payment_amount = request.form.get('payment_amount')

    # Process the assign data (e.g., store in database)
    # This function should be defined elsewhere in your application
    opportunity_id = assign_payment_to_sale(payment_id, sale_id, payment_amount)

    # Return a success response
    return list_payments(opportunity_id, sale_id,)

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
        store_payments(payments)
    return jsonify({'status': 'success'}), 200

@payments_blueprint.route('<int:opportunity_id>/<int:sale_id>', methods=['GET'])
@login_required
def list_payments(opportunity_id, sale_id):
    payments = list_payments_for_sale(sale_id)
    payment_dues = list_payment_dues(sale_id)
    opportunity = get_opportunity_by_id(opportunity_id)
    return render_template('payments/view.html', payments=payments, dues = payment_dues, sale_id=sale_id, 
                           opportunity_id=opportunity_id, opportunity_name=opportunity['name']), 200

@payments_blueprint.route('<int:opportunity_id>/<int:sale_id>/due', methods=['POST'])
@login_required
def handle_due(opportunity_id, sale_id):
    try:
        due_amount = request.form.get('amount_due')  # Assuming this is part of your form
        due_date = request.form.get('due_date')  # Assuming this is part of your form
        # Process the due amount and due date (e.g., store in database)
        store_payments_due(sale_id, due_date, due_amount)
        return list_payments(opportunity_id, sale_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@payments_blueprint.route('<int:opportunity_id>/<int:sale_id>/due/<int:due_id>/paid', methods=['GET'])
@login_required
def mark_due_paid(opportunity_id, sale_id, due_id):
    try:
        mark_payment_due_as_paid(due_id)
        return list_payments(opportunity_id, sale_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payments_blueprint.route('<int:opportunity_id>/<int:sale_id>/due/<int:due_id>/cancel', methods=['GET'])
@login_required
def mark_due_cancelled(opportunity_id, sale_id, due_id):
    try:
        mark_payment_due_as_cancelled(due_id)
        return list_payments(opportunity_id, sale_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payments_blueprint.route('/', methods=['POST'])
@require_api_key
def record_payment():
    try:
        # Parse JSON payload from the request
        data = request.get_json()
        
        # Extract data from the payload
        email = data.get('email')
        phone = data.get('phone')
        amount = data.get('amount')
        charges = data.get('charges')
        charge_tax = data.get('charge_tax')
        mode = data.get('mode')
        method = data.get('method')
        date = data.get('date')
        reference = data.get('reference')

        charges = int(charges) + int(charge_tax)
        
        if mode == "Razorpay":
            amount = round(amount / 100, 2)
            charges = round(charges / 100, 2)
            amount = amount - charges

        # Process the payment information (e.g., validate data, store in database)
        # This is a placeholder for your logic
        process_payment(email, phone, amount, charges, mode, method, date, reference)
        
        # Return a success response
        return jsonify({'message': 'Payment processed successfully'}), 200
    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({'error': str(e)}), 400
    

@payments_blueprint.route('<int:opportunity_id>/<int:sale_id>/<int:payment_id>/deposit', methods=['POST'])
@login_required
def mark_deposit(opportunity_id,sale_id, payment_id):
    try:
        # Process the deposit marking (e.g., update in database)
        mark_payment_as_deposit(payment_id)

        # Return a success response
        return list_payments(opportunity_id, sale_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 400