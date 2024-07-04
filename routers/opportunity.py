"""Add the APIs for the opportunites. Use Flask-Restful to create the APIs."""
from flask import jsonify, Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from utils import error_response, app_home, require_api_key
import csv
from werkzeug.utils import secure_filename
from store.opportunity_store import *  # Import the store_opportunity function
from store.instance_store import get_senders
from whatsapp.message_sender import send_template_message
import datetime

# Import your database model and messaging system here
opportunity_blueprint = Blueprint('opportunity', __name__)

@opportunity_blueprint.route('/', methods=['GET'])
@login_required
def load_opportunities():
    tomorrow_date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
    return render_template('opportunity/list.html', content={}, tomorrow=tomorrow_date)

@opportunity_blueprint.route('/create', methods=['POST'])
@require_api_key
def create_opportunity():
    try:
        # Extract the data from the request
        data = request.get_json()
        date = data.get('date')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        campaign = data.get('campaign')
        ad_name = data.get('ad_name')
        ad_id = data.get('ad_id')
        ad_medium = data.get('ad_medium')
        ad_fbp = data.get('ad_fbp')
        ad_fbc = data.get('ad_fbc')
        ad_placement = data.get('ad_placement')
        ad_account = data.get('ad_account')

        # Create the opportunity in your database
        opportunity_data = {
            'name': name,
            'date': date,
            'email': email,
            'phone': phone,
            'campaign': campaign,
            'ad_name': ad_name,
            'ad_id': ad_id,
            'ad_medium': ad_medium,
            'ad_fbp': ad_fbp,
            'ad_fbc': ad_fbc,
            'ad_placement': ad_placement,
            'ad_account': ad_account
        }
        store_opportunity(opportunity_data)

        return jsonify({'message': 'Opportunity created successfully'}), 201
    except Exception as e:
        return error_response(500, str(e))

@opportunity_blueprint.route('/video_watched', methods=['POST'])
@require_api_key
def video_watched():
    try:
        # Extract the data from the request
        data = request.get_json()
        email = data.get('email')
        handle_video_watch_event(email)
        
        return jsonify({'status': 'success', 'message': 'Opportunity status updated successfully'}), 200
    except Exception as e:
        return error_response(500, str(e))

@opportunity_blueprint.route('/<opportunity_id>/status/<status_id>', methods=['POST'])
@login_required
def update_status_value(opportunity_id, status_id):
    try:
        # Prepare the data for the update_opportunity function
        opportunity_data = {
            'status': status_id,
            'id': opportunity_id
        }

        # Call the update_opportunity function
        print('Updating opportunity status')
        update_opportunity_status(opportunity_data)
        
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
                print(f'Processing row {row["Name"]}')
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
        # Get the filter type and value from the query parameters
        filter_type = request.args.get('filterType', None)
        filter_value = request.args.get('filterValue', None)
        
        # Retrieve the list of opportunities from your database based on the filter type and value
        opportunities, total_pages, total_items = get_opportunities(page, per_page, search_term, search_type, filter_type, filter_value)
        
        # Prepare the response dataa
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
            'agent': opportunity['agent'],
            'opportunity_status_color': opportunity['opportunity_status_color'],
            'call_status_color': opportunity['call_status_color'],
            'sales_agent_color': opportunity['sales_agent_color'],
            'opportunity_status_text_color': opportunity['opportunity_status_text_color'],
            'call_status_text_color': opportunity['call_status_text_color'],
            'sales_agent_text_color': opportunity['sales_agent_text_color'],
            'ad_name': opportunity['ad_name'],
            'ad_medium': opportunity['ad_medium'],
            'video_watched': opportunity['video_watched'],
            'ad_placement': opportunity['ad_placement'],
            }
            response_data.append(opportunity_data)
        
        call_statuses = get_all_call_status()
        opportunity_statuses = get_all_opportunity_status()
        sales_agents = get_all_sales_agents()
        
        return jsonify({
            'items': response_data,
            'page': page,
            'total_pages': total_pages,
            'total_items': total_items,
            'call_statuses': call_statuses,
            'opportunity_statuses': opportunity_statuses,
            'sales_agents': sales_agents
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
            'appointments': opportunity['appointments'],
            'senders': senders,  # Add the list of senders to the response data,
            'gender': opportunity['gender'],
            'challenge_type': opportunity['challenge_type'],
            'company_type': opportunity['company_type'],
        }
        call_statuses = get_all_call_status()
         # Get a list of opportunity statuses
        opportunity_statuses = get_all_opportunity_status()
        # Get a list of sales agents (optin callers)
        sales_agents = get_all_sales_agents()
        # Get a list of challenge types
        challenge_types = get_all_challenge_types()  # Replace with your database query

        # Get a list of company types
        company_types = get_all_company_types()  # Replace with your database query

        sales = get_all_sales(opportunity_id)
        
        return render_template('opportunity/view.html', opportunity=response_data,
                       call_statuses=call_statuses, opportunity_statuses=opportunity_statuses,
                       sales_agents=sales_agents, challenge_types=challenge_types,
                       company_types=company_types, sales=sales)
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
        # opportunity_status = request.form.get('opportunity_status')
        sales_agent = request.form.get('optin_caller')
        comment = request.form.get('comment')
        sales_date = request.form.get('sales_date')
        gender = request.form.get('gender')
        challenge_type = request.form.get('challenge_type')
        company_type = request.form.get('company_type')

        # Prepare the data for the update_opportunity function
        opportunity_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'call_status': call_status,
            #'opportunity_status': opportunity_status,
            'sales_agent': sales_agent,
            'comment': comment,
            'sales_date': sales_date,
            'gender': gender,
            'challenge_type': challenge_type,
            'company_type': company_type
        }
        print('Updating Opportunity Data:', opportunity_data)
        # Call the update_opportunity function
        update_opportunity_data(opportunity_id, opportunity_data)

        return redirect(url_for('opportunity.load_opportunities'))
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

@opportunity_blueprint.route('/status/<int:opportunity_id>/<string:status_type>', methods=['POST'])
@login_required
def update_status_type(opportunity_id, status_type):
    try:
        # Extract the status from the request
        data = request.get_json()
        status = data.get('status')
        opportunity_data = {
            'status': status,
            'opportunity_id': opportunity_id,
            'status_type': status_type
        }
        
        # Call the update_opportunity function
        update_opportunity_status(opportunity_data)
        
        return jsonify({'status': 'success', 'message': 'Opportunity status updated successfully'}), 200
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))
    
@opportunity_blueprint.route('/opportunity_status', methods=['GET'])
@login_required
def get_opportunity_statuses():
    try:
        # Retrieve all opportunity statuses from your database
        opportunity_statuses = get_all_opportunity_status()  # Replace with your database query
        return jsonify(opportunity_statuses), 200
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))

@opportunity_blueprint.route('/call_status', methods=['GET'])
@login_required
def get_call_statuses():
    try:
        # Retrieve all call statuses from your database
        call_statuses = get_all_call_status()  # Replace with your database query
        return jsonify(call_statuses), 200
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))
    
@opportunity_blueprint.route('/sales_agents', methods=['GET'])
@login_required
def get_sales_agents():
    try:
        # Retrieve all sales agents from your database
        sales_agents = get_all_sales_agents()  # Replace with your database query
        return jsonify(sales_agents), 200
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))
    
@opportunity_blueprint.route('/<int:opportunity_id>/sale', methods=['POST'])
@login_required
def record_sale(opportunity_id):
    try:
        # Extract the sale data from the request
        data = request.form
        sale_value = data.get('sale_value')
        note = data.get('note')
        sales_agent = data.get('sales_agent')
        product = data.get('product')
        sale_date = data.get('sale_date')

        # Record the sale in your database for the given opportunity_id
        record_new_sale(opportunity_id, sale_date, sale_value, note, sales_agent, product)
        
        return get_opportunity_detail(opportunity_id)
        return get_opportunity_detail(opportunity_id)
    except Exception as e:
        print(str(e))
        return error_response(500, str(e))