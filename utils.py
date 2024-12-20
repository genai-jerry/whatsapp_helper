import calendar
from datetime import datetime, timedelta
import os
import re
from flask import jsonify, request, g
from store.key_store import retrieve_api_key

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
app_home = os.path.abspath(os.path.join(current_dir, os.pardir))

def error_response(status_code, message):
    response = jsonify({'error': message})
    response.status_code = status_code
    return response

def is_valid_phone_number(phone_number):
    # Implement your logic to validate the phone number here
    # Return True if the phone number is valid, False otherwise
    # You can use regular expressions or any other validation method
    # For example, you can use the following regular expression pattern to validate a phone number:
    pattern = r'^\+\d{1,3}\s?\(\d{1,3}\)\s?\d{1,4}-\d{1,4}$'
    if re.match(pattern, phone_number):
         return True
    else:
         return False
    pass

def format_phone_number(phone_number):
    # Remove any non-digit characters from the phone number
    phone_number = re.sub(r'\D', '', phone_number)
    
    # Check if the phone number starts with a country code
    if phone_number.startswith('+'):
        # Remove the leading '+' sign
        phone_number = phone_number[1:]
    
    # Check if the phone number has a valid length
    if len(phone_number) == 10:
        # Format the phone number as per the international mobile number format
        formatted_number = f'+91{phone_number[:3]}{phone_number[3:6]}{phone_number[6:]}'
        return formatted_number
    else:
        # Return the original phone number if it does not have a valid length
        return f'+{phone_number}'
    
from functools import wraps
def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        from models import ApiKey
        if 'X-API-KEY' not in request.headers:
            return jsonify({'error': 'Missing API key'}), 403
        api_key = request.headers['X-API-KEY']
        g.api_key = retrieve_api_key(api_key)
        if g.api_key is None:
            return jsonify({'error': 'Invalid API key'}), 403
        return view_function(*args, **kwargs)
    return decorated_function

def get_month_dates(month):
    if month:
        month = datetime.strptime(month, '%B %Y')
        first_day = month.replace(day=1)
        last_day = month.replace(day=calendar.monthrange(month.year, month.month)[1]) + timedelta(days=1)
    else:
        first_day = datetime.now().replace(day=1)
        last_day = datetime.now().replace(day=calendar.monthrange(datetime.now().year, datetime.now().month)[1]) + timedelta(days=1)
    
    return first_day, last_day

def get_month_year(month_year):
    if month_year:
        date = datetime.strptime(month_year, '%B %Y')
        month = date.strftime('%B')
        year = date.year
    else:
        month = datetime.now().strftime('%B')
        year = datetime.now().year
    return month, year

def get_month_number(month_name):
    print(f'Month Name for : {month_name}')
    month_number = datetime.strptime(month_name, '%B').month
    print(f'Month Number for : {month_number}')
    return month_number

def get_month_name(month_number):
    return calendar.month_name[month_number]