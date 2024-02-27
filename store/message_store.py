from db.connection_manager import *
from datetime import datetime
from store.opportunity_store import get_opportunity_id_by_phone_number

def update_message(id, status, error):
    try:
        connection = create_connection()

        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = '''Update messages set status=%s, error_message=%s, update_time=%s where id=%s'''

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (status, error, datetime.now(), id))

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

        # Get the opportunity ID by phone number
        opportunity_id = get_opportunity_id_by_phone_number(receiver)

        # Set the opportunity ID as receiver_id in the messages table
        sql = '''INSERT INTO messages (type, sender, receiver, message, template, status, receiver_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)'''

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (type, sender, receiver, message, template, 'Pending', opportunity_id))

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


    


