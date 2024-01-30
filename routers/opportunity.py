# Create the router to manage the opportunities routes and add support 
# for the CRUD operations 
# Create APIs for listing all opportunities, creating a new opportunity,
# updating an existing opportunity and deleting an opportunity
# -----------------------------------------------------------------------

# Follow the approach used in message.py for creating the APIs

# Use Flask for creating the router
# Use the blueprint approach for creating the router
# Use the opportunity_blueprint for creating the router
# Use the following route for listing all opportunities
#     /opportunity
# Use the following route for creating a new opportunity
#     /opportunity
# Use the following route for updating an existing opportunity
#     /opportunity/<id>
# Use the following route for deleting an opportunity
#     /opportunity/<id>

# Use the following code for creating the router
# -----------------------------------------------------------------------
# from flask import Blueprint, request, jsonify
# from utils import error_response
#
# opportunity_blueprint = Blueprint('opportunity', __name__)
#
# def error_response(status_code, message):
#     response = jsonify({'error': message})
#     response.status_code = status_code
#     return response
#


