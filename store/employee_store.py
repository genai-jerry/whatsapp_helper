from db.connection_manager import *

def get_all_employees():
    try:
        cnx = create_connection()
        cursor = cnx.cursor()
        query = '''SELECT e.id, e.user_id, u.name as name, d.department_key,
         d.name as department_name 
        FROM employees e 
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN users u ON e.user_id = u.id
        WHERE u.active = 1
        ORDER BY u.name ASC
        '''
        cursor.execute(query)
        employees = cursor.fetchall()
        employee_list = []
        for employee in employees:
            employee_list.append({
                'id': employee[0],
                'user_id': employee[1],
                'name': employee[2],
                'department_key': employee[3],
                'department_name': employee[4]
            })
        return employee_list
    except Exception as e:
        print(f"Error fetching employees: {e}")
    

def get_all_departments():
    try:
        cnx = create_connection()
        cursor = cnx.cursor()
        query = '''SELECT id, name, department_key FROM departments 
        WHERE active = 1
        ORDER BY name ASC'''
        cursor.execute(query)
        departments = cursor.fetchall()
        department_list = []
        for department in departments:
            department_list.append({
                'id': department[0],
                'name': department[1],
                'department_key': department[2]
            })
        return department_list
    except Exception as e:
        print(f"Error fetching departments: {e}")

def get_sales_agent_id_for_user(user_id, cursor = None):
    try:
        connection = None
        if not cursor:
            connection = create_connection()
            cursor = connection.cursor()

        query = '''SELECT id FROM sales_agent WHERE user_id = %s'''
        cursor.execute(query, (user_id,))
        sales_agent = cursor.fetchone()
        if sales_agent:
            return sales_agent[0]
        else:
            return None
    finally:
        if connection:
            if cursor:
                cursor.close()
                connection.close()