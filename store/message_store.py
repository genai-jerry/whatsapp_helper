from db.connection_manager import *
from datetime import datetime
from store.opportunity_store import get_opportunity_id_by_phone_number
from utils import format_phone_number
import re

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

    # Format the receiver as per international mobile number format standards
    receiver = format_phone_number(message_data['receiver'])

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

        # Retrieve the last inserted ID
        last_inserted_id = cursor.lastrowid
        print(f'Got id {last_inserted_id}')
        connection.commit()
        print("Message inserted successfully.")
        return last_inserted_id
    finally:
        if cursor:
            cursor.close()

def retrieve_message_by_id(id):
    try:
        connection = create_connection()

        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = '''SELECT id, receiver, template, status, create_time FROM messages WHERE id = %s'''

        # Execute the query with the provided value
        cursor.execute(sql, (id,))

        # Fetch the result
        result = cursor.fetchone()

        if result:
            # Create a dictionary to store the message data
            message_data = {
                'id': result[0],
                'receiver': result[1],
                'template': result[2],
                'status': result[3],
                'create_time': result[4]
            }
            return message_data
        else:
            return None
    finally:
        if cursor:
            cursor.close()

def get_all_messages(page, per_page):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Count the total number of messages
        count_sql = "SELECT COUNT(*) FROM messages"
        cursor.execute(count_sql)
        total_items = cursor.fetchone()[0]

        # Calculate the total number of pages
        total_pages = (total_items + per_page - 1) // per_page

        # Retrieve the messages for the current page
        offset = (page - 1) * per_page
        select_sql = """
            SELECT 
                m.id, 
                m.receiver, 
                m.template, 
                m.status, 
                m.create_time
            FROM 
                messages m
            ORDER BY m.create_time desc
            LIMIT %s OFFSET %s
        """
        cursor.execute(select_sql, (per_page, offset))
        results = cursor.fetchall()

        # Prepare the response data
        messages = []
        for row in results:
            message = {
                'id': row[0],
                'receiver': row[1],
                'template': row[2],
                'status': row[3],
                'create_time': row[4]
            }
            messages.append(message)

        return messages, total_pages, total_items

    finally:
        if cursor:
            cursor.close()

def get_message(message_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the message from the database
        select_sql = """
            SELECT 
                m.id, 
                m.receiver, 
                m.template, 
                m.status, 
                m.create_time
            FROM 
                messages m
            WHERE 
                m.id = %s
        """
        cursor.execute(select_sql, (message_id,))
        row = cursor.fetchone()

        # Prepare the response data
        if row is not None:
            message = {
                'id': row[0],
                'receiver': row[1],
                'template': row[2],
                'status': row[3],
                'create_time': row[4]
            }
            return message

    finally:
        if cursor:
            cursor.close()

def update_message_status(message_id, status):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Update the message status in the database
        update_sql = """
            UPDATE 
                messages
            SET 
                status = %s
            WHERE 
                id = %s
        """
        cursor.execute(update_sql, (status, message_id))

        # Commit the transaction
        connection.commit()

    finally:
        if cursor:
            cursor.close()