from flask import Blueprint, Flask, render_template, request, jsonify
from store.payment_store import store_payment, list_payments_for_sale
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

@payments_blueprint.route('<int:opportunity_id>/<int:sale_id>', methods=['GET'])
def list_payments(opportunity_id, sale_id):
    payments = list_payments_for_sale(sale_id)
    return render_template('payments/view.html', payments=payments, sale_id=sale_id, opportunity_id=opportunity_id), 200