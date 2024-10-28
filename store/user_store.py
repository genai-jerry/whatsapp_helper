from db.connection_manager import *
from werkzeug.security import generate_password_hash

def create_new_user(username, password, name):
    password_hash = generate_password_hash(password)
    # Insert data into 'users' table using a prepared statement
    try:
        connection = create_connection()

        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "INSERT INTO users (username, password, active, name) VALUES (%s, %s, 0, %s)"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (username, password_hash, name))

        connection.commit()
        print("User created successfully.")
    finally:
        if cursor:
            cursor.close()

def load_user_by_username(username):
    try:
        print(f'Checking username: {username}')
        connection = create_connection()
        cursor = connection.cursor()
        # Define the SQL query with placeholders
        sql = '''SELECT u.id, u.username, u.password, u.active, r.name 
            FROM users u
            LEFT JOIN user_role ur on ur.user_id = u.id
            LEFT JOIN roles r on ur.role_id = r.id
            WHERE username = %s AND active = True'''
        # Execute the query with the provided value
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        if result:
            user = {
                'id': result[0],
                'username': result[1],
                'password': result[2],
                'active': result[3],
                'role': result[4]
            }
            print(f'Returning {user}')
            return user
        else:
            return None
    finally:
        if cursor:
            cursor.close()