"""Add the APIs for the opportunites. Use Flask-Restful to create the APIs."""
from flask import jsonify, Blueprint, render_template, request
from flask_login import login_required
from utils import error_response, app_home
import csv
from werkzeug.utils import secure_filename
from store.opportunity_store import *  # Import the store_opportunity function
from store.instance_store import get_senders
from whatsapp.message_sender import send_template_message

# Import your database model and messaging system here

opportunity_blueprint = Blueprint('opportunity', __name__)

@opportunity_blueprint.route('/', methods=['GET'])
@login_required
def load_opportunities():
    return render_template('opportunity/list.html', content={})

@opportunity_blueprint.route('/import', methods=['GET'])
@login_required
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
        campaign = data.get('campaign')

        # Create the opportunity in your database
        opportunity_data = {
            'name': name,
            'date': date,
            'email': email,
            'phone': phone,
            'campaign': campaign
        }
        store_opportunity(opportunity_data)

        return jsonify({'message': 'Opportunity created successfully'}), 201
    except Exception as e:
        return error_response(500, str(e))

@opportunity_blueprint.route('/<opportunity_id>/status/<status_id>', methods=['POST'])
@login_required
def update_status(opportunity_id, status_id):
    try:
        # Prepare the data for the update_opportunity function
        opportunity_data = {
            'status': status_id,
            'id': opportunity_id
        }

        # Call the update_opportunity function
        update_opportunity(opportunity_data)

        return jsonify({'status': 'success', 'message': 'Opportunity status updated successfully'}), 200
    except Exception as e:
        return error_response(500, str(e))

@opportunity_blueprint.route('/message', methods=['POST'])
@login_required
def send_message():
    try:
        # Extract the message from the request
        data = request.get_json()
        message = send_template_message(data, app_home)
        return jsonify(message), 200
    except Exception as e:
        return error_response(500, str(e))

@opportunity_blueprint.route('/import', methods=['POST'])
@login_required
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
        print('Loading data')
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                opportunity_data = {
                    'date': row['Date'],
                    'name': row['Name'],
                    'email': row['Email'],
                    'phone': row['Phone Number'],
                    'opportunity_status': row['Call Status'],
                    'optin_status': row['Status'],
                    'agent': row['Optin Call'],
                    'sale_date': row['Sale Date'],
                    'comment': row['Comments'],
                    'campaign': row['Campaign']
                }
                print('Storing Opportunity')
                store_opportunity(opportunity_data)

        return jsonify({'message': 'Opportunities imported successfully'}), 201
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))

       
@opportunity_blueprint.route('/list', methods=['GET'])
@login_required
def list_opportunities():
    try:
        # Get the page number, size, search term, and search type from the query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search_term = request.args.get('searchTerm', None)
        search_type = request.args.get('searchType', None)

        # Retrieve the list of opportunities from your database
        opportunities, total_pages, total_items = get_opportunities(page, per_page, search_term, search_type)  # Replace with your database query

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

        return jsonify({
            'items': response_data,
            'page': page,
            'total_pages': total_pages,
            'total_items': total_items
        }), 200
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))
    
@opportunity_blueprint.route('/<int:opportunity_id>', methods=['GET'])
@login_required
def get_opportunity_detail(opportunity_id):
    try:
        # Retrieve the opportunity detail from your database based on the opportunity_id
        opportunity = get_opportunity_by_id(opportunity_id)  # Replace with your database query

        # Get a list of senders
        senders = get_senders()

        # Prepare the response data
        response_data = {
            'id': opportunity['id'],
            'name': opportunity['name'],
            'email': opportunity['email'],
            'phone': opportunity['phone'],
            'comment': opportunity['comment'],
            'register_time': opportunity['register_time'],
            'opportunity_status': opportunity['opportunity_status'],
            'call_status': opportunity['call_status'],
            'sales_agent': opportunity['sales_agent'],
            'messages': opportunity['messages'],
            'templates': opportunity['templates'],
            'senders': senders  # Add the list of senders to the response data
        }
        call_statuses = get_all_call_status()
         # Get a list of opportunity statuses
        opportunity_statuses = get_all_opportunity_status()
        # Get a list of sales agents (optin callers)
        sales_agents = get_all_sales_agents()

        print(f'Showing {opportunity_statuses} and {opportunity["call_status"]}')
        return render_template('opportunity/view.html', opportunity=response_data,
                            call_statuses=call_statuses, opportunity_statuses=opportunity_statuses,
                            sales_agents=sales_agents)
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))

@opportunity_blueprint.route('/update', methods=['POST'])
@login_required
def update_opportunity_detail():
    try:
        # Extract the data from the form
        opportunity_id = request.form.get('id')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        call_status = request.form.get('call_status')
        opportunity_status = request.form.get('opportunity_status')
        sales_agent = request.form.get('optin_caller')
        comment = request.form.get('comment')

        # Prepare the data for the update_opportunity function
        opportunity_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'call_status': call_status,
            'opportunity_status': opportunity_status,
            'sales_agent': sales_agent,
            'comment': comment
        }
        print('Updating Opportunity Data:', opportunity_data)
        # Call the update_opportunity function
        update_opportunity_data(opportunity_id, opportunity_data)

        return load_opportunities()
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))

@opportunity_blueprint.route('/search', methods=['POST'])
@login_required
def handle_search_request():
    search_term = request.form['search_term']
    search_type = request.form['search_type']
    results = search_opportunities(search_term, search_type)
    return render_template('opportunity/list.html', opportunities=results)