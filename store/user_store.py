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

def load_roles_by_user_id(user_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "SELECT r.name FROM roles r LEFT JOIN user_role ur on ur.role_id = r.id WHERE ur.user_id = %s"
        cursor.execute(sql, (user_id,))
        results = cursor.fetchall()
        roles = []
        for result in results:
            roles.append(result[0])
        return roles
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def load_user_by_username(username):
    try:
        print(f'Checking username: {username}')
        connection = create_connection()
        cursor = connection.cursor()
        # Define the SQL query with placeholders
        sql = '''SELECT u.id, u.username, u.password, u.active
            FROM users u
            WHERE u.username = %s AND u.active = True'''
        # Execute the query with the provided value
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        if result:
            user = {
                'id': result[0],
                'username': result[1],
                'password': result[2],
                'active': result[3],
                'roles': load_roles_by_user_id(result[0])
            }
            print(f'Returning {user}')
            return user
        else:
            return None
    finally:
        if cursor:
            cursor.close()

def update_user_password(user_id, new_password):
    password_hash = generate_password_hash(new_password)
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "UPDATE users SET password = %s WHERE id = %s"
        cursor.execute(sql, (password_hash, user_id))
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_user_status(user_id, is_active):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "UPDATE users SET active = %s WHERE id = %s"
        cursor.execute(sql, (is_active, user_id))
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def list_all_users(page=1, page_size=10):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = '''SELECT u.id, u.name, u.username, u.active
            FROM users u
            ORDER BY u.name ASC
            LIMIT %s OFFSET %s'''
        cursor.execute(sql, (page_size, (page - 1) * page_size))
        rows = cursor.fetchall()
        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'name': row[1],
                'username': row[2],
                'active': row[3],
                'roles': list_all_roles(row[0]),
                })
        sql = "SELECT COUNT(*) FROM users"
        cursor.execute(sql)
        total_users = cursor.fetchone()[0]
        return users, total_users
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def list_all_roles(user_id = None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "SELECT r.id, r.name FROM roles r"
        if user_id:
            sql += ''' WHERE r.id IN (SELECT role_id FROM user_role WHERE user_id = %s)'''
            cursor.execute(sql, (user_id,))
        else:
            cursor.execute(sql)
        rows = cursor.fetchall()
        roles = []
        for row in rows:
            roles.append({
                'id': row[0],
                'name': row[1]
            })
        return roles
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def add_role_to_user(user_id, role_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "INSERT INTO user_role (user_id, role_id) VALUES (%s, %s)"
        cursor.execute(sql, (user_id, role_id))
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def remove_role_from_user(user_id, role_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "DELETE FROM user_role WHERE user_id = %s AND role_id = %s"
        cursor.execute(sql, (user_id, role_id))
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()