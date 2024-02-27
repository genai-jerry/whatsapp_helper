from db.connection_manager import *
import json
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
instances = {}

def store_instance(mobile_number, user_data):
    name = user_data['name']
    status = user_data['status']
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
    finally:
        if cursor:
            cursor.close()

def remove_instance(mobile_number):
    server.remove_instance(mobile_number)
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
    finally:
        if cursor:
            cursor.close()

def update_instance(mobile_number, user_data):
    status = user_data['status']
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
    finally:
        if cursor:
            cursor.close()

def retrieve_instance(mobile_number):
    # Select data from the specified table and return as JSON
    try:
        print(f'Loading instance for {mobile_number}')
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Select data for the given ID
        cursor.execute(f"SELECT * FROM instances WHERE mobile_number = %s", (mobile_number,))

        # Fetch the result as a dictionary
        instance = cursor.fetchone()
        if instance:
            # Convert the result to a JSON object
            return instance
        else:
            return None
    finally:
        if cursor:
            cursor.close()

def get_all_instances():
    print('Getting Instances from Instance Manager')
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
    finally:
        if cursor:
            cursor.close()
    
def get_senders():
    # Select data from the specified table and return as JSON
    try:
        print('Loading senders')
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Select all data from the specified table
        cursor.execute("SELECT mobile_number, name FROM instances")

        # Fetch all rows as a list of dictionaries
        rows = cursor.fetchall()
        print(f'Rows {rows}')
        senders = []
        for row in rows:
            print(row)
            sender = {
                'mobile_number': row['mobile_number'],
                'name': row['name']
            }
            senders.append(sender)
        print(f'Senders: {senders}')
        return senders
    finally:
        if cursor:
            cursor.close()

