import json
import mysql.connector
from mysql.connector import errorcode
import configparser

def read_db_config(filename='config/config.ini', section='mysql'):
    # Read database configuration from an external file
    parser = configparser.ConfigParser()
    parser.read(filename)

    # Get the MySQL database configuration
    db_config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_config[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {filename} file.")

    return db_config

def create_connection():
    # Create a MySQL database connection using the configuration file
    try:
        db_config = read_db_config()
        connection = mysql.connector.connect(**db_config)
        print("Connected to the database.")
        return connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Access denied. Check your MySQL username and password in the config file.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: The specified database does not exist.")
        else:
            print(f"Error: {err}")
        return None

def save_instance(mobile_number, name, status):
    # Insert data into 'instances' table using a prepared statement
    try:
        connection = create_connection()

        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "INSERT INTO instances (mobile_number, name, status) VALUES (%s, %s, %s)"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (mobile_number, name, status))

        connection.commit()
        print("Data inserted successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()

def delete_instance(mobile_number):
    # Insert data into 'instances' table using a prepared statement
    try:
        connection = create_connection()

        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "DELETE FROM instances where mobile_number = %s"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (mobile_number,))

        connection.commit()
        print("Data deleted successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()

def modify_instance(mobile_number, status):
    # Update data into 'instances' table using a prepared statement
    try:
        print('Modifying instance')
        connection = create_connection()
        
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "UPDATE instances set status=%s where mobile_number=%s"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (status, mobile_number))

        connection.commit()
        print("Data updated successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()

def load_all_instances():
    # Select data from the specified table and return as JSON
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Select all data from the specified table
        cursor.execute(f"SELECT * FROM instances")

        # Fetch all rows as a list of dictionaries
        rows = cursor.fetchall()

        # Convert the result to a JSON object
        result_json = json.dumps(rows, indent=2)

        return result_json
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()

def load_instance(mobile_number):
    # Select data from the specified table and return as JSON
    try:
        print(f'Loading instance for {mobile_number}')
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Select data for the given ID
        cursor.execute(f"SELECT * FROM instances WHERE mobile_number = %s", (mobile_number,))

        # Fetch the result as a dictionary
        instance = cursor.fetchone()
        print(instance)
        if instance:
            # Convert the result to a JSON object
            return instance
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()

def save_template(name, template):
    # Insert data into 'templates' table using a prepared statement
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "INSERT INTO templates (name, text_template) VALUES (%s, %s)"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (name, template))

        connection.commit()
        print("Data inserted successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()

def load_template(id):
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
            return json.dumps(template, indent=2)
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()

def update_template(id, name, template_text):
    # Update data into 'templates' table using a prepared statement
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "UPDATE templates set name=%s, template_text=%s where id=%s"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (name, template_text, id))

        connection.commit()
        print("Data updated successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()