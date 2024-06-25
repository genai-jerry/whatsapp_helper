from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock database
payments = []
payment_modes = [{"id": 1, "name": "PhonePe", "description": "PhonePe payments"}]

@app.route('/payments', methods=['POST'])
def record_payment():
    new_payment = request.json
    new_payment["id"] = len(payments) + 1
    payments.append(new_payment)
    return jsonify(new_payment), 201

@app.route('/payments', methods=['GET'])
def list_payments():
    return jsonify(payments), 200

@app.route('/payments/<int:payment_id>', methods=['GET'])
def view_payment_details(payment_id):
    payment = next((p for p in payments if p["id"] == payment_id), None)
    if payment:
        return jsonify(payment), 200
    else:
        return jsonify({"message": "Payment not found"}), 404

@app.route('/opportunities/<int:opportunity_id>/payments', methods=['GET'])
def view_opportunity_payments(opportunity_id):
    # Mock implementation, replace with real logic to fetch opportunity payments
    return jsonify({"sales_value": 10000, "total_paid": 5000, "payments_pending": 2, "tax_value": 500}), 200

@app.route('/payment-modes', methods=['POST'])
def create_payment_mode():
    new_mode = request.json
    new_mode["id"] = len(payment_modes) + 1
    payment_modes.append(new_mode)
    return jsonify(new_mode), 201

@app.route('/payment-modes', methods=['GET'])
def list_payment_modes():
    return jsonify(payment_modes), 200

if __name__ == '__main__':
    app.run(debug=True)