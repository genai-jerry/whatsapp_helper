import mysql.connector
from mysql.connector import errorcode
import configparser
from xmlrpc.client import ServerProxy
# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

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