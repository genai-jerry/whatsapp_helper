from db.connection_manager import *
from datetime import datetime

def get_projection_by_id(projection_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = '''SELECT * FROM sales_projections WHERE id=%s'''

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (projection_id,))

        # Fetch the result
        projection = cursor.fetchone()

        return projection
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_sales_agent_projections(projection_config_data):
    # store the data in the database in the sales_projections
    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Check if the projection already exists for the employee   
        projection_exists = get_projection_for_sales_agent_for_month(projection_config_data['sales_agent_id'], projection_config_data['month'], projection_config_data['year'])
        if projection_exists:
            sql = '''UPDATE sales_projections SET month=%s, year=%s, sale_price=%s, total_call_slots=%s, 
                closure_percentage_goal=%s, closure_percentage_projected=%s
                WHERE id=%s''' 
        else:
            sql = '''INSERT INTO sales_projections (month, year, sale_price, total_call_slots, 
                closure_percentage_goal, closure_percentage_projected, sales_agent_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)'''  

        cursor.execute(sql, (projection_config_data['month'], projection_config_data['year'], projection_config_data['sale_price'], 
                             projection_config_data['total_calls_slots'], 
                             projection_config_data['sales_closed_goal'], 
                             projection_config_data['sales_closed_projection'],  
                             projection_config_data['sales_agent_id']))
        
        connection.commit()
        print("Data Inserted successfully.")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_performance_metrics_for_sales_agent_for_month(month, year, sales_agent_id = None):
    try:
        print(f'Getting performance metrics for sales agent {sales_agent_id} for month {month} and year {year}')
        connection = create_connection()
        cursor = connection.cursor()

        # Get projection data
        
        if sales_agent_id:
            projection_sql = '''
                SELECT total_call_slots, closure_percentage_goal, closure_percentage_projected, 
                    sales_value_projected, sales_value_goal
                FROM sales_projections 
                WHERE month = %s AND year = %s
            '''
            projection_sql += ' AND sales_agent_id = %s'
            cursor.execute(projection_sql, (month, year, sales_agent_id))
        else:
            projection_sql = '''
                SELECT SUM(total_call_slots), AVG(closure_percentage_goal), AVG(closure_percentage_projected), 
                    AVG(sales_value_projected), AVG(sales_value_goal)
                FROM sales_projections 
            WHERE month = %s AND year = %s
        '''
            cursor.execute(projection_sql, (month, year))
        projection_data = cursor.fetchone()

        # Get appointment data
        appointment_sql = '''
            SELECT 
                COUNT(a.id) as total_appointments_booked,
                COUNT(CASE WHEN a.status NOT IN (3,5,6) THEN 1 END) as total_appointments_attended
            FROM appointments a
            WHERE MONTHNAME(a.appointment_time) = %s AND EXTRACT(YEAR FROM a.appointment_time) = %s
        '''
        if sales_agent_id:
            appointment_sql += ' AND a.mentor_id = %s'
            cursor.execute(appointment_sql, (month, year, sales_agent_id))
        else:
            cursor.execute(appointment_sql, (month, year))
        appointment_data = cursor.fetchone()

        # Get sales data
        sales_sql = '''
            SELECT 
                COUNT(CASE WHEN is_final = 1 THEN 1 END) as total_sales_final,
                COUNT(CASE WHEN is_final = 0 THEN 1 END) as total_sales_deposit
            FROM sale
            WHERE MONTHNAME(sale_date) = %s AND EXTRACT(YEAR FROM sale_date) = %s
        '''
        if sales_agent_id:
            sales_sql += ' AND sales_agent_id = %s'
            cursor.execute(sales_sql, (month, year, sales_agent_id))
        else:
            cursor.execute(sales_sql, (month, year))
        sales_data = cursor.fetchone()

        # Combine all data
        performance_metrics = {
            'total_call_slots': projection_data[0],
            'closure_percentage_goal': projection_data[1],
            'closure_percentage_projected': projection_data[2],
            'sales_value_projected': projection_data[3],
            'sales_value_goal': projection_data[4],
            'total_appointments_booked': appointment_data[0],
            'total_appointments_attended': appointment_data[1],
            'total_sales_final': sales_data[0],
            'total_sales_deposit': sales_data[1]
        }

        return performance_metrics

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_projection_for_sales_agent_for_month(sales_agent_id, month, year):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = '''SELECT id, total_call_slots, closure_percentage_goal, closure_percentage_projected, 
            sales_value_projected, sales_value_goal
            FROM sales_projections 
            WHERE sales_agent_id=%s AND month=%s AND year=%s'''
        
        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (sales_agent_id, month, year))

        # Fetch the result
        projection = cursor.fetchone()
        
        if projection:
            projection_data = {
                'id': projection[0],
                'total_call_slots': projection[1],
                'closure_percentage_goal': projection[2],
                'closure_percentage_projected': projection[3],
                'sales_value_projected': projection[4],
                'sales_value_goal': projection[5],
            }
            return projection_data
        else:
            return None
    finally:
        if cursor:  
            cursor.close()
        if connection:
            connection.close()

def get_all_projections_for_month(month, year):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = '''SELECT * FROM sales_projections WHERE month=%s AND year=%s'''  
        
        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (month, year))

        # Fetch the results
        projections = cursor.fetchall()

        return projections
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_projection(projection_id, data):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = '''UPDATE sales_projections SET month=%s, year=%s, sale_price=%s, total_call_slots=%s, 
                closure_percentage_goal=%s, closure_percentage_projected=%s, sales_value_projected=%s, 
                sales_value_goal=%s, actual_sales_value=%s, total_calls_made=%s, total_calls_scheduled=%s, 
                total_sales_closed=%s, total_deposits_collected=%s, sales_agent_id=%s WHERE id=%s'''

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (data['month'], data['year'], data['sale_price'], data['total_call_slots'], 
                             data['closure_percentage_goal'], data['closure_percentage_projected'], 
                             data['sales_value_projected'], data['sales_value_goal'], data['actual_sales_value'], 
                             data['total_calls_made'], data['total_calls_scheduled'], data['total_sales_closed'], 
                             data['total_deposits_collected'], data['sales_agent_id'], projection_id))
        
        connection.commit()
        
        print("Data Updated successfully.")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_projection_config(data):
    projection_config = get_projection_config(data['month'], data['year'])
    try:
        connection = create_connection()
        cursor = connection.cursor()

        if projection_config:
            sql = '''UPDATE sales_projection_config SET cost_per_lead=%s, sale_price=%s, 
                show_up_rate_goal=%s,  appointment_booked_goal=%s, 
                show_up_rate_projection=%s, appointment_booked_projection=%s 
                WHERE month=%s AND year=%s'''
            cursor.execute(sql, (data['cost_per_lead'], data['sale_price'], data['show_up_rate_goal'], 
                                 data['appointment_booked_goal'], data['show_up_rate_projection'], 
                                 data['appointment_booked_projection'], data['month'], data['year']))
        else:
            sql = '''INSERT INTO sales_projection_config (cost_per_lead, sale_price,
                show_up_rate_goal, appointment_booked_goal, show_up_rate_projection, 
                appointment_booked_projection, month, year) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(sql, (data['cost_per_lead'], data['sale_price'], data['show_up_rate_goal'], 
                                 data['appointment_booked_goal'], data['show_up_rate_projection'], 
                                 data['appointment_booked_projection'], data['month'], data['year']))

        connection.commit()
        print("Data Updated successfully.")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_sales_kpi_for_month(month, year):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''SELECT SUM(total_call_slots), AVG(closure_percentage_projected) AS projected_closure_rate,
            AVG(closure_percentage_goal) AS goal_closure_rate, AVG(sales_value_projected) AS projected_sales_value
            FROM sales_projections 
            WHERE month=%s AND year=%s'''
        cursor.execute(sql, (month, year))
        total_call_slots = cursor.fetchone()
        return {
            'total_call_slots': total_call_slots[0] if total_call_slots[0] else 0,
            'projected_closure_rate': total_call_slots[1] if total_call_slots[1] else 0,
            'goal_closure_rate': total_call_slots[2] if total_call_slots[2] else 0,
            'projected_sales_value': total_call_slots[3] if total_call_slots[3] else 0
        }
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_projection_config(month, year):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''SELECT cost_per_lead, sale_price, show_up_rate_projection, 
            show_up_rate_goal, appointment_booked_projection, appointment_booked_goal 
            FROM sales_projection_config 
            WHERE month=%s AND year=%s'''

        cursor.execute(sql, (month, year))

        config = cursor.fetchone()
        if config:
            return { 'cost_per_lead': config[0], 'sale_price': config[1],   
                'show_up_rate_projection': config[2], 'show_up_rate_goal': config[3], 
                'appointment_booked_projection': config[4], 'appointment_booked_goal': config[5] }
        else:
            return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_funnel_metrics_for_month_sales_agent(month, year, sales_agent_id = None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Get the sum of total call slots for each sales agent, 

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
