import os
from db.connection_manager import *

def generate_new_api_key():
    # Generate a new API key
    new_key = os.urandom(24).hex()

    # Create a new ApiKey instance
    query = """
    INSERT INTO api_key (`key`)
    VALUES (%s)
    """
    connection_manager = create_connection()
    cursor = connection_manager.cursor()
    try:
        cursor.execute(query, (new_key,))
        connection_manager.commit()
    finally:
        cursor.close()

    # Return the new API key
    return new_key

def retrieve_api_key(api_key):
    # Retrieve the API key from the database
    query = """
    SELECT `key`
    FROM api_key
    WHERE `key` = %s
    """
    connection_manager = create_connection()
    cursor = connection_manager.cursor()
    try:
        cursor.execute(query, (api_key,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    finally:
        cursor.close()