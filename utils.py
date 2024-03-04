import os
import re
from flask import jsonify

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