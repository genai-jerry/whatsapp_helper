from db.connection_manager import *

def get_tasks_due(employee_id = None, page=1, per_page=10, assigned_by = None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        if employee_id:
            sql = '''SELECT t.id, t.due_date, t.description, t.opportunity_id, o.name as opportunity_name,
                     u.name as assigned_to, t.completed
                     FROM tasks t
                     LEFT JOIN opportunity o ON t.opportunity_id = o.id
                     LEFT JOIN users u ON t.user_id = u.id
                     '''
            if assigned_by:
                sql += ''' WHERE t.user_id != %s AND t.created_by = %s ORDER BY t.due_date, o.name ASC    
                     LIMIT %s OFFSET %s'''
                cursor.execute(sql, (employee_id, assigned_by, per_page, (page-1)*per_page))
            else:
                sql += ''' WHERE t.completed = 0 AND t.user_id = %s ORDER BY t.due_date, o.name ASC    
                     LIMIT %s OFFSET %s'''
                cursor.execute(sql, (employee_id, per_page, (page-1)*per_page))
        else:
            sql = '''SELECT t.id, t.due_date, t.description, t.opportunity_id, o.name as opportunity_name,
                     u.name as assigned_to, t.completed
                     FROM tasks t
                     LEFT JOIN opportunity o ON t.opportunity_id = o.id
                     LEFT JOIN users u ON t.user_id = u.id
                     '''
            if assigned_by:
                sql += ''' WHERE t.user_id != %s AND t.created_by = %s ORDER BY t.due_date, o.name ASC    
                     LIMIT %s OFFSET %s'''
                cursor.execute(sql, (assigned_by, assigned_by, per_page, (page-1)*per_page))
            else:
                sql += ''' WHERE t.completed = 0 ORDER BY t.due_date, o.name ASC    
                     LIMIT %s OFFSET %s'''
                cursor.execute(sql, (per_page, (page-1)*per_page))

        tasks = cursor.fetchall()
        tasks_list = []
        for task in tasks:
            tasks_list.append({
                'id': task[0],
                'due_date': task[1],
                'description': task[2],
                'opportunity_id': task[3],
                'opportunity_name': task[4],
                'assigned_to': task[5],
                'completed': task[6]
            })

        if employee_id:
            sql = '''SELECT COUNT(*) FROM tasks t '''
            if assigned_by:
                sql += ''' WHERE t.user_id != %s AND t.created_by = %s'''
                cursor.execute(sql, (assigned_by, assigned_by))
            else:
                sql += ''' WHERE t.completed = 0 AND t.user_id = %s'''
                cursor.execute(sql, (employee_id,))
        else:
            sql = '''SELECT COUNT(*) FROM tasks t '''
            if assigned_by:
                sql += ''' WHERE t.user_id != %s AND t.created_by = %s'''
                cursor.execute(sql, (assigned_by, assigned_by))
            else:
                sql += ''' WHERE t.completed = 0'''
                cursor.execute(sql)
        total_tasks = cursor.fetchone()[0]

        return tasks_list, total_tasks
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def create_task(user_id, name, description, due_date, opportunity_id, created_by):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = '''INSERT INTO tasks (user_id, name, description, due_date, opportunity_id, completed, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(sql, (user_id, name, description, due_date, opportunity_id, False, created_by))
            # Get the last inserted ID
            cursor.execute("SELECT LAST_INSERT_ID()")
            task_id = cursor.fetchone()[0]
            connection.commit()
            cursor.close()
            connection.close()
    return {"id": task_id}

def update_task_status(task_id, status):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = '''UPDATE tasks SET completed = %s, last_updated = NOW() WHERE id = %s'''
            cursor.execute(sql, (status, task_id))
            connection.commit()
            cursor.close()
            connection.close()
            return True
            
def update_task(task_id, user_id, name, description, due_date, opportunity_id=None):    
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''UPDATE tasks SET user_id = %s, name = %s, description = %s, due_date = %s, 
                opportunity_id = %s, last_updated = NOW() WHERE id = %s'''
        cursor.execute(sql, (user_id, name, description, due_date, opportunity_id, task_id))
        connection.commit()
        print("Task updated successfully.")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def delete_task(task_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()        

        sql = '''DELETE FROM tasks WHERE id = %s'''
        cursor.execute(sql, (task_id))
        connection.commit()
        print("Task deleted successfully.")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_task_by_id(task_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''SELECT * FROM tasks WHERE id = %s'''
        cursor.execute(sql, (task_id))
        task = cursor.fetchone()
        return task
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()  

def complete_task(task_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''UPDATE tasks SET completed = 1, last_updated = NOW() WHERE id = %s'''
        cursor.execute(sql, (task_id))
        connection.commit()
        print("Task completed successfully.")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_all_tasks_for_opportunity(opportunity_id, employee_id = None, page=1, per_page=10):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''SELECT t.id, o.name, t.description, t.due_date, t.completed , t.last_updated, u.name as creator_name
                FROM tasks t
                LEFT JOIN opportunity o ON t.opportunity_id = o.id
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.opportunity_id = %s'''
        if employee_id:
            sql += ''' AND t.user_id = %s'''
        
        sql += ''' ORDER BY t.due_date ASC
                LIMIT %s OFFSET %s'''
        if employee_id:
            cursor.execute(sql, (opportunity_id, employee_id, per_page, (page-1)*per_page))
        else:
            cursor.execute(sql, (opportunity_id, per_page, (page-1)*per_page))
        tasks = cursor.fetchall()

        sql = '''SELECT COUNT(*) FROM tasks t WHERE t.opportunity_id = %s'''
        if employee_id:
            sql += ''' AND t.user_id = %s'''
            cursor.execute(sql, (opportunity_id, employee_id))
        else:
            cursor.execute(sql, (opportunity_id,))

        total_tasks = cursor.fetchone()[0]
        tasks_list = []
        for task in tasks:
            tasks_list.append({
                'id': task[0],
                'opportunity_name': task[1],
                'description': task[2],
                'due_date': task[3],
                'status': task[4],
                'last_updated': task[5],
                'creator_name': task[6]
            })
        print(tasks_list)
        return tasks_list, total_tasks
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_all_tasks_for_user(user_id, page=1, per_page=10):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''SELECT * FROM tasks WHERE user_id = %s
                ORDER BY due_date ASC
                LIMIT %s OFFSET %s'''
        cursor.execute(sql, (user_id, per_page, (page-1)*per_page)) 
        tasks = cursor.fetchall()

        sql = '''SELECT COUNT(*) FROM tasks WHERE user_id = %s'''
        cursor.execute(sql, (user_id,))
        total_tasks = cursor.fetchone()[0]

        return tasks, total_tasks
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_all_tasks_for_user_and_opportunity(user_id, opportunity_id, page=1, per_page=10):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''SELECT * FROM tasks WHERE user_id = %s AND opportunity_id = %s
                ORDER BY due_date ASC
                LIMIT %s OFFSET %s'''
        cursor.execute(sql, (user_id, opportunity_id, per_page, (page-1)*per_page))
        tasks = cursor.fetchall()

        sql = '''SELECT COUNT(*) FROM tasks WHERE user_id = %s AND opportunity_id = %s'''
        cursor.execute(sql, (user_id, opportunity_id))
        total_tasks = cursor.fetchone()[0]

        return tasks, total_tasks
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_all_tasks_for_user_and_opportunity_and_date(user_id, opportunity_id, date, page=1, per_page=10):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''SELECT * FROM tasks WHERE user_id = %s AND opportunity_id = %s AND due_date = %s
                ORDER BY due_date ASC
                LIMIT %s OFFSET %s'''
        cursor.execute(sql, (user_id, opportunity_id, date, per_page, (page-1)*per_page))
        tasks = cursor.fetchall()

        sql = '''SELECT COUNT(*) FROM tasks WHERE user_id = %s AND opportunity_id = %s AND due_date = %s'''
        cursor.execute(sql, (user_id, opportunity_id, date))
        total_tasks = cursor.fetchone()[0]

        return tasks, total_tasks
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_all_tasks_for_appointment(appointment_id, page=1, per_page=10):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''SELECT * FROM tasks WHERE appointment_id = %s
                ORDER BY due_date ASC
                LIMIT %s OFFSET %s'''
        cursor.execute(sql, (appointment_id, per_page, (page-1)*per_page)) 
        tasks = cursor.fetchall()

        sql = '''SELECT COUNT(*) FROM tasks WHERE appointment_id = %s'''
        cursor.execute(sql, (appointment_id,))
        total_tasks = cursor.fetchone()[0]

        return tasks, total_tasks
    finally:
        if cursor:
            cursor.close()  
        if connection:
            connection.close()