"""Add the APIs for the opportunites. Use Flask-Restful to create the APIs."""
from flask import jsonify, Blueprint, render_template, request
from .utils import error_response
import pandas as pd
from werkzeug.utils import secure_filename
from store.opportunity_store import *  # Import the store_opportunity function

# Import your database model and messaging system here

opportunity_blueprint = Blueprint('opportunity', __name__)

@opportunity_blueprint.route('/', methods=['GET'])
def load_opportunities():
    return render_template('opportunity/list.html', content={})

@opportunity_blueprint.route('/import', methods=['GET'])
def show_opportunities():
    return render_template('opportunity/import.html', content={})

@opportunity_blueprint.route('/create', methods=['POST'])
def create_opportunity():
    try:
        # Extract the data from the request
        data = request.get_json()
        date = data.get('date')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        call_status = data.get('call_status')
        campaign = data.get('campaign')

        # Validate the data
        if not all([date, name, email, phone, call_status, campaign]):
            return error_response(400, 'All fields are required')

        # Create the opportunity in your database
        opportunity_data = {
            'name': name,
            'status': call_status
        }
        store_opportunity(email, opportunity_data)

        return jsonify({'message': 'Opportunity created successfully'}), 201
    except Exception as e:
        return error_response(500, str(e))

@opportunity_blueprint.route('/update_status', methods=['PUT'])
def update_status():
    try:
        # Extract the new status from the request
        data = request.get_json()
        opportunity_id = data.get('opportunity_id')
        new_status = data.get('call_status')

        # Validate the data
        if not all([opportunity_id, new_status]):
            return error_response(400, 'Both opportunity_id and call_status are required')

        # Prepare the data for the update_opportunity function
        opportunity_data = {
            'status': new_status
        }

        # Call the update_opportunity function
        update_opportunity(opportunity_id, opportunity_data)

        return jsonify({'message': 'Opportunity status updated successfully'}), 200
    except Exception as e:
        return error_response(500, str(e))

@opportunity_blueprint.route('/send_message', methods=['POST'])
def send_message():
    try:
        # Extract the message from the request
        data = request.get_json()
        opportunity_id = data.get('opportunity_id')
        message = data.get('message')

        # Validate the data
        if not all([opportunity_id, message]):
            return error_response(400, 'Both opportunity_id and message are required')

        # TODO: Add code to send the message to the user

        return jsonify({'message': 'Message sent successfully'}), 200
    except Exception as e:
        return error_response(500, str(e))

@opportunity_blueprint.route('/import', methods=['POST'])
def import_opportunities():
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return error_response(400, 'No file part')

        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return error_response(400, 'No selected file')

        filename = secure_filename(file.filename)
        file.save(filename)
        print('Reading csv file')
        # Read the Excel file
        df = pd.read_csv(filename)
        print('Loading data')
        # Iterate over the rows of the DataFrame and create opportunities
        for index, row in df.iterrows():
            print(row)
            opportunity_data = {
                'date': row['Date'],
                'name': row['Opportunity Name'],
                'email': row['Email Address'],
                'phone': row['Phone Number'],
                'call_status': row['Call Status'],
                'opportunity_status': row['Opportunity Status'],
                'agent': row['Agent'],
                'campaign': row['Campaign Name']
            }
            print('Storing Opportunity')
            store_opportunity(opportunity_data)

        return jsonify({'message': 'Opportunities imported successfully'}), 201
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))

       
@opportunity_blueprint.route('/list', methods=['GET'])
def list_opportunities():
    try:
        # Retrieve the list of opportunities from your database
        opportunities = get_opportunities()  # Replace with your database query

        # Prepare the response data
        response_data = []
        for opportunity in opportunities:
            opportunity_data = {
                'id': opportunity['id'],
                'name': opportunity['name'],
                'date': opportunity['date'],
                'email': opportunity['email'],
                'phone': opportunity['phone'],
                'call_status': opportunity['call_status'],
                'opportunity_status': opportunity['opportunity_status'],
                'agent': opportunity['agent']
            }
            response_data.append(opportunity_data)

        return jsonify(response_data), 200
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))