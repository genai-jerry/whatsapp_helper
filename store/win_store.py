from db.connection_manager import *

def store_win(date, user_id, win_type, description):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        sql = "INSERT INTO wins (user_id, win_type, description, created_at) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (user_id, win_type, description, date))
        cursor.execute("SELECT LAST_INSERT_ID()")
        win_id = cursor.fetchone()[0]
        connection.commit()
        return {"id": win_id}
    finally:
        cursor.close()
        connection.close()

def get_wins_for_user(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        sql = '''SELECT w.id, w.description, w.win_type, w.created_at, u.name 
            FROM wins w
        LEFT JOIN users u ON u.id = w.user_id 
            WHERE w.user_id = %s
        '''
        cursor.execute(sql, (user_id))
        wins = cursor.fetchall()
        wins_list = []
        for win in wins:
            wins_list.append({
            'id': win[0],
            'description': win[1],
            'win_type_name': win[2],
            'created_at': win[3],
                'name': win[4]
            })
        return wins_list
    finally:
        cursor.close()
        connection.close()

def get_wins_for_user_for_date(user_id, date):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        sql = '''SELECT w.id, w.description, w.win_type, w.created_at, u.name 
        FROM wins w
        LEFT JOIN users u ON u.id = w.user_id 
        WHERE w.user_id = %s AND w.created_at = %s
        '''
        cursor.execute(sql, (user_id, date))
        wins = cursor.fetchall()
        wins_list = []
        for win in wins:
            wins_list.append({
                'id': win[0],
                'description': win[1],
                'win_type_name': win[2],
                'created_at': win[3],
                'name': win[4]
            })
        return wins_list
    finally:
        cursor.close()
        connection.close()

def get_all_wins_for_date(date):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        sql = '''SELECT w.id, w.description, wt.name as win_type_name, w.created_at, u.name 
            FROM wins w
        LEFT JOIN users u ON u.id = w.user_id 
        LEFT JOIN win_types wt ON wt.id = w.win_type 
        WHERE w.created_at = %s
        '''
        cursor.execute(sql, (date,))
        wins = cursor.fetchall()
        wins_list = []
        for win in wins:
            wins_list.append({
                'id': win[0],
                'description': win[1],
                'win_type_name': win[2],
                'created_at': win[3],
                'name': win[4]
            })
        return wins_list
    finally:
        cursor.close()
        connection.close()
    
def get_win_types():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        sql = "SELECT id, name FROM win_types"
        cursor.execute(sql)
        win_types = cursor.fetchall()
        win_types_list = []
        for win_type in win_types:
            win_types_list.append({
            'id': win_type[0],
            'name': win_type[1]
            })
        return win_types_list
    finally:
        cursor.close()
        connection.close()