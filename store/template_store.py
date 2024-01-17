from db.connection_manager import *
import json

def store_template(user_data):
    name = user_data['name']
    template = user_data['template_text']
    # Insert data into 'templates' table using a prepared statement
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "INSERT INTO templates (name, template_text, active) VALUES (%s, %s, 1)"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (name, template))

        connection.commit()
        print("Data inserted successfully.")
    finally:
        if cursor:
            cursor.close()

def update_template(user_data):
    id = user_data['id']
    text = user_data['template_text']
    # Update data into 'templates' table using a prepared statement
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "UPDATE templates set template_text=%s where id=%s"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (text, id))

        connection.commit()
        print("Data updated successfully.")
    finally:
        if cursor:
            cursor.close()

def deactivate_template(id):
    update_template_status(id, False)

def activate_template(id):
    update_template_status(id, True)

def update_template_status(id, status):
    # Update data into 'templates' table using a prepared statement
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "UPDATE templates set active=%s where id=%s"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (status, id))

        connection.commit()
        print("Data updated successfully.")
    finally:
        if cursor:
            cursor.close()

def retrieve_template(id):
    # Select data from the specified table and return as JSON
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Select data for the given ID
        cursor.execute(f"SELECT * FROM templates WHERE id = %s", (id,))

        # Fetch the result as a dictionary
        template = cursor.fetchone()

        if template:
            # Convert the result to a JSON object
            return template
        else:
            return None
    finally:
        if cursor:
            cursor.close()

def retrieve_template_by_name(name):
    # Select data from the specified table and return as JSON
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Select data for the given ID
        cursor.execute(f"SELECT * FROM templates WHERE name = %s", (name,))

        # Fetch the result as a dictionary
        template = cursor.fetchone()

        if template:
            # Convert the result to a JSON object
            return template
        else:
            return None
    finally:
        if cursor:
            cursor.close()

def get_all_templates():
    # Select data from the specified table and return as JSON
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Select all data from the specified table
        cursor.execute(f"SELECT * FROM templates")

        # Fetch all rows as a list of dictionaries
        rows = cursor.fetchall()

        # Convert the result to a JSON object
        result_json = json.dumps(rows, indent=2)
        print(result_json)
        return result_json
    finally:
        if cursor:
            cursor.close()
    


