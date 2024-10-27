import calendar
from db.connection_manager import *
from datetime import datetime, timedelta
from store.sales_store import get_sales_agent_id_for_user

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
            sql = '''UPDATE sales_projections SET sale_price=%s, total_call_slots=%s, 
                closure_percentage_goal=%s, closure_percentage_projected=%s, commission_percentage=%s,
                sales_value_goal=%s, sales_value_projected=%s
                WHERE sales_agent_id=%s AND month=%s AND year=%s''' 
        else:
            sql = '''INSERT INTO sales_projections (sale_price, total_call_slots, 
                closure_percentage_goal, closure_percentage_projected, commission_percentage, 
                sales_value_goal, sales_value_projected,
                sales_agent_id,
                month, year) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''  

        cursor.execute(sql, (projection_config_data['sale_price'], 
                             projection_config_data['total_calls_slots'], 
                             projection_config_data['sales_closed_goal'], 
                             projection_config_data['sales_closed_projection'],  
                             projection_config_data['commission_percentage'],
                             projection_config_data['sales_value_goal'],
                             projection_config_data['sales_value_projection'],
                             projection_config_data['sales_agent_id'],
                             projection_config_data['month'],
                             projection_config_data['year']))
        
        connection.commit()
        print("Data Inserted successfully.")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_performance_metrics_for_date_range(start_date, end_date, sales_agent_id=None):
    try:
        start_date = start_date.strftime('%Y-%m-%d 00:00:00')
        end_date = end_date.strftime('%Y-%m-%d 23:59:59')

        connection = create_connection()
        cursor = connection.cursor()

        # Get projection data
        if sales_agent_id:
            projection_sql = '''
                SELECT SUM(total_call_slots), AVG(closure_percentage_goal), AVG(closure_percentage_projected), 
                    AVG(sales_value_projected), AVG(sales_value_goal)
                FROM sales_projections 
                WHERE DATE(CONCAT(year, '-', LPAD(MONTH(STR_TO_DATE(month, '%M')), 2, '0'), '-01')) BETWEEN %s AND %s
                AND sales_agent_id = %s
            '''
            cursor.execute(projection_sql, (start_date, end_date, sales_agent_id))
        else:
            projection_sql = '''
                SELECT SUM(total_call_slots), AVG(closure_percentage_goal), AVG(closure_percentage_projected), 
                    AVG(sales_value_projected), AVG(sales_value_goal)
                FROM sales_projections 
                WHERE DATE(CONCAT(year, '-', LPAD(MONTH(STR_TO_DATE(month, '%M')), 2, '0'), '-01')) BETWEEN %s AND %s
            '''
            cursor.execute(projection_sql, (start_date, end_date))
        projection_data = cursor.fetchone()

        # Get appointment data
        appointment_sql = '''
            SELECT 
                COUNT(DISTINCT(a.opportunity_id)) as total_appointments_booked,
                COUNT(DISTINCT CASE WHEN a.status NOT IN (1, 5, 6) THEN a.opportunity_id END) as total_appointments_attended
            FROM appointments a
            WHERE a.appointment_time BETWEEN %s AND %s
        '''
        if sales_agent_id:
            appointment_sql += ' AND a.mentor_id = %s'
            cursor.execute(appointment_sql, (start_date, end_date, sales_agent_id))
        else:
            cursor.execute(appointment_sql, (start_date, end_date))
        appointment_data = cursor.fetchone()

        # Get sales data
        sales_sql = '''
            SELECT 
                COUNT(CASE WHEN is_final = 1 THEN 1 END) as total_sales_final,
                COUNT(CASE WHEN is_final = 0 THEN 1 END) as total_sales_deposit,
                SUM(CASE WHEN is_final = 1 THEN sale_value ELSE 0 END) as total_final_sale_value
            FROM sale
            WHERE sale_date BETWEEN %s AND %s
        '''
        if sales_agent_id:
            sales_sql += ' AND sales_agent = %s'
            cursor.execute(sales_sql, (start_date, end_date, sales_agent_id))
        else:
            cursor.execute(sales_sql, (start_date, end_date))
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
            'total_sales_deposit': sales_data[1],
            'total_final_sale_value': sales_data[2]
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
        config = get_projection_config(month, year)

        # Define the SQL query with placeholders
        if sales_agent_id:
            sql = '''SELECT total_call_slots, closure_percentage_goal, closure_percentage_projected, 
                sales_value_projected, sales_value_goal, sale_price, commission_percentage
                FROM sales_projections 
                WHERE sales_agent_id=%s AND month=%s AND year=%s'''
            # Prepare the query and execute it with the provided values
            cursor.execute(sql, (sales_agent_id, month, year))
        else:
            sql = '''SELECT SUM(total_call_slots), AVG(closure_percentage_goal), AVG(closure_percentage_projected), 
                AVG(sales_value_projected), AVG(sales_value_goal), AVG(sale_price), AVG(commission_percentage)
                FROM sales_projections 
                WHERE month=%s AND year=%s'''
            # Prepare the query and execute it with the provided values
            cursor.execute(sql, (month, year))
        
        # Fetch the result
        projection = cursor.fetchone()
        show_up_rate_goal = config['show_up_rate_goal'] if config else 0
        if projection:
            projection_data = {
                'apps': projection[0],
                'closure_percentage_goal': projection[1],
                'calls': projection[0],
                'closure_percentage_projected': projection[2],
                'sale_price': projection[5],
                'commission_percentage': projection[6],
                'projection': projection[3],
                'goal': projection[4]
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

def update_marketing_spend(month, year, marketing_spend):
    update_projection_config({'month': month, 'year': year, 'marketing_spend': marketing_spend})

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
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Check if the projection config exists for the given month and year
        check_sql = '''SELECT COUNT(*) FROM sales_projection_config 
                       WHERE month=%s AND year=%s'''
        cursor.execute(check_sql, (data['month'], data['year']))
        config_exists = cursor.fetchone()[0] > 0

        if config_exists:
            # Update existing record
            update_fields = []
            update_values = []
            for field in ['cost_per_lead', 'sale_price', 'show_up_rate_goal', 'appointment_booked_goal',
                          'show_up_rate_projection', 'appointment_booked_projection', 'marketing_spend']:
                if data.get(field, 0) != 0:
                    update_fields.append(f"{field}=%s")
                    update_values.append(data[field])
            
            if update_fields:
                update_fields.append("marketing_spend_updated_at=%s")
                update_values.extend([datetime.now(), data['month'], data['year']])
                
                sql = f'''UPDATE sales_projection_config 
                          SET {', '.join(update_fields)}
                          WHERE month=%s AND year=%s'''
                cursor.execute(sql, update_values)
            else:
                print("No fields to update.")
        else:
            # Insert new record
            sql = '''INSERT INTO sales_projection_config 
                     (cost_per_lead, sale_price, show_up_rate_goal, appointment_booked_goal, 
                      show_up_rate_projection, appointment_booked_projection, 
                      marketing_spend, marketing_spend_updated_at, month, year) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(sql, (data.get('cost_per_lead', 0), 
                                 data.get('sale_price', 0), 
                                 data.get('show_up_rate_goal', 0), 
                                 data.get('appointment_booked_goal', 0), 
                                 data.get('show_up_rate_projection', 0), 
                                 data.get('appointment_booked_projection', 0),
                                 data.get('marketing_spend', 0), datetime.now(),
                                 data['month'], data['year']))

        connection.commit()
        print("Sales projection config updated successfully.")
        return True
    except Exception as e:
        print(f"Error updating sales projection config: {str(e)}")
        raise e
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
            show_up_rate_goal, appointment_booked_projection, appointment_booked_goal,
            marketing_spend, marketing_spend_updated_at
            FROM sales_projection_config 
            WHERE month=%s AND year=%s'''

        cursor.execute(sql, (month, year))

        config = cursor.fetchone()
        if config:
            return { 'cost_per_lead': config[0], 'sale_price': config[1],   
                'show_up_rate_projection': config[2], 'show_up_rate_goal': config[3], 
                'appointment_booked_projection': config[4], 'appointment_booked_goal': config[5],
                'marketing_spend': config[6], 'marketing_spend_updated_at': config[7] }
        else:
            return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_monthly_performance_for_agent(month, year, user_id):
    start_date_of_month = datetime(year, month, 1)
    end_date_of_month = datetime(year, month, calendar.monthrange(year, month)[1])

    # Find the Monday of the first week of the month
    first_monday = start_date_of_month - timedelta(days=start_date_of_month.weekday())    
    # Find the Sunday of the last week of the month
    last_sunday = end_date_of_month + timedelta(days=6 - end_date_of_month.weekday())

    # Calculate the number of weeks
    num_weeks = (last_sunday - first_monday).days // 7 + 1
    start_date = first_monday

    if user_id:
        agent_id = get_sales_agent_id_for_user(user_id)
    else:
        agent_id = None

    monthly_data = {"weeks": []}
    for week in range(num_weeks):
        week_start = start_date + timedelta(days=7*week)
        week_end = min(week_start + timedelta(days=6), last_sunday)
        
        # Fetch actual data for this week
        data = get_performance_metrics_for_date_range(week_start, week_end, agent_id)
        
        week_data = {
            'week_number': week + 1,
            'start_date': week_start.strftime('%Y-%m-%d'),
            'end_date': week_end.strftime('%Y-%m-%d'),
            'total_call_slots': data['total_call_slots'],
            'closure_percentage_goal': data['closure_percentage_goal'],
            'closure_percentage_projected': data['closure_percentage_projected'],
            'sales_value_projected': data['sales_value_projected'],
            'sales_value_goal': data['sales_value_goal'],
            'apps_actual': data['total_appointments_booked'],
            'calls_actual': data['total_appointments_attended'],
            'goal_actual': data['total_sales_final'],
            'projection_actual': data['total_sales_final']
        }
        monthly_data['weeks'].append(week_data)

    return monthly_data

