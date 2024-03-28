from db.connection_manager import *

def store_config(config_data):
    try:
        # Create a new database connection
        cnx = create_connection()

        # Create a new cursor
        cursor = cnx.cursor()

        # Define the SQL query for inserting a new config
        query = """
        INSERT INTO configs (key, value)
        VALUES (%s, %s)
        """

        # Define the values for the SQL query
        values = (config_data['key'], config_data['value'])

        # Execute the SQL query
        cursor.execute(query, values)

        # Commit the transaction
        cnx.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        cnx.close()

def retrieve_config(key):
    try:
        # Create a new database connection
        cnx = create_connection()

        # Create a new cursor
        cursor = cnx.cursor()

        # Define the SQL query for getting a config
        query = "SELECT value FROM configs WHERE name = %s"

        # Execute the SQL query
        cursor.execute(query, (key,))

        # Fetch the first row
        row = cursor.fetchone()

        # Return the config value
        return row[0] if row else None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        cnx.close()