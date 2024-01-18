from db.connection_manager import *

def update_message(id, status, error):
    try:
        connection = create_connection()

        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = '''Update messages set status=%s, error_message=%s where id=%s'''

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (status, error, id))

        connection.commit()
        print("Data Updated successfully.")
    finally:
        if cursor:
            cursor.close()

def store_message(message_data):
    type = message_data['type']
    sender = message_data['sender']
    receiver = message_data['receiver']
    template = message_data['template'] if type == 'template' else None
    message = message_data['message']
    print(f'Got {template}')
    # Insert data into 'instances' table using a prepared statement
    try:
        connection = create_connection()

        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = '''INSERT INTO messages (type, sender, receiver, message, template, status) 
            VALUES (%s, %s, %s, %s, %s, %s)'''

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (type, sender, receiver, message, template, 'Pending'))
        print('Executed Query')
        # Retrieve the last inserted ID
        last_inserted_id = cursor.lastrowid
        print(f'Got id {last_inserted_id}')
        connection.commit()
        print("Data inserted successfully.")
        return last_inserted_id
    finally:
        if cursor:
            cursor.close()


    


