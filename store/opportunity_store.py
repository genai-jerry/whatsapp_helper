from db.connection_manager import *
from utils import format_phone_number
from datetime import datetime

opportunities = {}

def get_opportunity_status_id(cursor, opportunity_status_name):
    if opportunity_status_name == None:
        return None
    sql_opportunity_status = "SELECT id FROM opportunity_status WHERE name = %s"
    cursor.execute(sql_opportunity_status, (opportunity_status_name,))
    opportunity_status = cursor.fetchone()[0]
    return opportunity_status

def get_optin_status_id(cursor, call_status_name):
    if call_status_name == None:
        return None
    sql_call_status = "SELECT id FROM lead_call_status WHERE name = %s"
    cursor.execute(sql_call_status, (call_status_name,))
    call_status = cursor.fetchone()[0]
    return call_status

def get_sales_agent_id(cursor, sales_agent_name):
    if sales_agent_name == None:
        return None
    sql_sales_agent = "SELECT id FROM sales_agent WHERE name = %s"
    cursor.execute(sql_sales_agent, (sales_agent_name,))
    sales_agent = cursor.fetchone()[0]
    return sales_agent

def store_opportunity(opportunity_data):
    try:
        date_str = opportunity_data['date'] if opportunity_data['date'] else None
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ') if date_str else None
        print(f'Got date {date}')
        name = opportunity_data['name'] if opportunity_data['name'] else None
        email = opportunity_data['email'] if opportunity_data['email'] else ''
        phone = format_phone_number(opportunity_data['phone']) if opportunity_data['phone'] else None

        comment = opportunity_data['comment'] if 'comment' in opportunity_data and opportunity_data['comment'] else None
        sale_date_str = opportunity_data['sale_date'] if 'sale_date' in opportunity_data and opportunity_data['sale_date'] else None
        sale_date = datetime.strptime(sale_date_str, '%d/%m/%Y') if sale_date_str else None
        print(f'Got sale date {sale_date}')
        optin_status_name = opportunity_data['optin_status'] if 'optin_status' in opportunity_data and opportunity_data['optin_status'] else None
        opportunity_status_name = opportunity_data['opportunity_status'] if 'opportunity_status' in opportunity_data and opportunity_data['opportunity_status'] else None
        sales_agent_name = opportunity_data['agent'] if 'agent' in opportunity_data and opportunity_data['agent'] else None
        campaign = opportunity_data['campaign'] if 'campaign' in opportunity_data and opportunity_data['campaign'] else None

        # Insert the opportunity
        connection = create_connection()
        cursor = connection.cursor()
        print(f'Getting ids for {opportunity_status_name}, {optin_status_name} and {sales_agent_name}')
        opportunity_status = get_opportunity_status_id(cursor, opportunity_status_name) if opportunity_status_name != None else None
        optin_status = get_optin_status_id(cursor, optin_status_name) if optin_status_name != None else None
        sales_agent = get_sales_agent_id(cursor, sales_agent_name) if sales_agent_name != None else None

        print(f'Got {opportunity_status}, {optin_status} and {sales_agent}')


        # Check if the email already exists in the table
        sql_check_email = "SELECT COUNT(*) FROM opportunity WHERE email = %s or phone = %s"
        cursor.execute(sql_check_email, (email, phone))
        email_exists = cursor.fetchone()[0]
        
        if email_exists == 0:
            # Insert the opportunity
            sql_insert = """
                INSERT INTO opportunity (name, email, phone, register_time, opportunity_status, call_status, sales_agent, sales_date, comment, campaign)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (name, email, phone, date, opportunity_status, optin_status, sales_agent, sale_date, comment, campaign))
            connection.commit()
            print("Opportunity inserted successfully.")
        else:
            print("Email already exists in the table.")
            # Update the opportunity
            sql_update = """
                UPDATE opportunity 
                SET opportunity_status = %s, call_status = %s, sales_agent = %s, sales_date = %s , comment = %s, campaign = %s
                WHERE email = %s or phone = %s
            """
            cursor.execute(sql_update, (opportunity_status, optin_status, sales_agent, sale_date, comment, campaign, email, phone))
            connection.commit()
            print("Opportunity updated successfully.")
    except Exception as e:
        print(str(e))
        raise e
    finally:
        if cursor:
            cursor.close()

def remove_opportunity(email):
    # Delete data from 'opportunities' table using a prepared statement
    try:
        connection = create_connection()

        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "DELETE FROM opportunity where email = %s"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (email,))

        connection.commit()
        print("Opportunity deleted successfully.")
    finally:
        if cursor:
            cursor.close()

def update_opportunity(opportunity_data):
    status = opportunity_data['status']
    # Update data in 'opportunities' table using a prepared statement
    try:
        print(f'Modifying opportunity with status {status}')
        connection = create_connection()
        cursor = connection.cursor()
        status_type = opportunity_data['status_type']
        # Define the SQL query with placeholders
        if status_type == "call_status":
            sql = "UPDATE opportunity SET call_status = %s WHERE id = %s"
        elif status_type == "opportunity_status":
            sql = "UPDATE opportunity SET opportunity_status = %s WHERE id = %s"
        elif status_type == "agent":
            sql = "UPDATE opportunity SET sales_agent = %s WHERE id = %s"
        else:
            raise ValueError("Invalid status type")

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (status, opportunity_data['opportunity_id']))

        if status_type == "opportunity_status" and status == "2":
            # Update the sale_date to current date
            print('Updating sale date')
            sql_update_sale_date = "UPDATE opportunity SET sales_date = CURRENT_DATE() WHERE id = %s"
            cursor.execute(sql_update_sale_date, (opportunity_data['opportunity_id'],))

        connection.commit()
        print("Opportunity updated successfully.")
    finally:
        if cursor:
            cursor.close()

def get_opportunities(page, per_page, search_term=None, search_type=None, filter_type=None, filter_value=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        print("Getting opportiunities")

        # Prepare the SQL queries
        count_sql = """
            SELECT COUNT(*) FROM opportunity o
            LEFT JOIN 
            lead_call_status cs ON o.call_status = cs.id
            LEFT JOIN 
            opportunity_status os ON o.opportunity_status = os.id
            LEFT JOIN 
            sales_agent sa ON o.sales_agent = sa.id
            """
        select_sql = """
            SELECT 
            o.name, 
            o.email, 
            o.phone, 
            o.register_time, 
            os.name AS opportunity_status, 
            cs.name AS call_status, 
            sa.name AS sales_agent,
            o.id,
            os.color_code AS opportunity_status_color,
            cs.color_code AS call_status_color,
            sa.color_code AS sales_agent_color,
            os.text_color AS opportunity_status_text_color,
            cs.text_color AS call_status_text_color,
            sa.text_color AS sales_agent_text_color
            FROM 
            opportunity o
            LEFT JOIN 
            lead_call_status cs ON o.call_status = cs.id
            LEFT JOIN 
            opportunity_status os ON o.opportunity_status = os.id
            LEFT JOIN 
            sales_agent sa ON o.sales_agent = sa.id
        """
        params = []

        # If a search term and search type are provided, add a WHERE clause to the queries
        if search_term or search_type or filter_type or filter_value:
            count_sql += " WHERE"
            select_sql += " WHERE"

        if search_term and search_type:
            count_sql += f" o.{search_type} LIKE %s"
            select_sql += f" o.{search_type} LIKE %s"
            params.append("%" + search_term + "%")

        # If a filter type and filter value are provided, add a WHERE clause to the queries
        print(f'Filter params {filter_type} and {filter_value}')
        
        if filter_type and filter_value:
            if search_term or search_type:
                count_sql += " AND"
                select_sql += " AND"
            if isinstance(filter_value, int) and int(filter_value) == 11:
                count_sql += f" {filter_type} IS NULL"
                select_sql += f" {filter_type} IS NULL"
            else:
                count_sql += f" {filter_type} = %s"
                select_sql += f" {filter_type} = %s"
                if isinstance(filter_value, int):
                    params.append(int(filter_value))
                else:
                    params.append(filter_value)

        select_sql += " ORDER BY o.register_time desc LIMIT %s OFFSET %s"
        print(select_sql)
        print(count_sql, params)
        # Count the total number of opportunities
        cursor.execute(count_sql, params)  # Only pass the search term and filter value to the count query
        params.extend([per_page, (page - 1) * per_page])
        total_items = cursor.fetchone()[0]

        # Calculate the total number of pages
        total_pages = (total_items + per_page - 1) // per_page
        print(select_sql, params)
        # Retrieve the opportunities for the current page
        cursor.execute(select_sql, params)
        results = cursor.fetchall()

        # Prepare the response data
        opportunities = []
        for row in results:
            opportunity = {
            'name': row[0],
            'email': row[1],
            'phone': row[2],
            'date': row[3],
            'opportunity_status': row[4],
            'call_status': row[5],
            'agent': row[6],
            'id': row[7],
            'opportunity_status_color': row[8],
            'call_status_color': row[9],
            'sales_agent_color': row[10],
            'opportunity_status_text_color': row[11],
            'call_status_text_color': row[12],
            'sales_agent_text_color': row[13]
            }
            opportunities.append(opportunity)

        return opportunities, total_pages, total_items

    finally:
        if cursor:
            cursor.close()

def get_opportunity_by_id(opportunity_id):
    try:
        # Create a cursor
        connection = create_connection()
        cursor = connection.cursor()

        # Fetch opportunity from the database
        cursor.execute(
            """
            SELECT 
                opportunity.id,
                opportunity.name,
                opportunity.email,
                opportunity.phone,
                opportunity.comment,
                opportunity.register_time,
                opportunity.opportunity_status AS opportunity_status,
                opportunity.call_status AS call_status,
                opportunity.sales_agent AS sales_agent,
                opportunity.sales_date AS sales_date
            FROM 
                opportunity
            WHERE 
                opportunity.id = %s;
            """, (opportunity_id,)
        )
        opportunity = cursor.fetchone()

        if opportunity is None:
            return None

        # Fetch messages related to the opportunity
        cursor.execute("""
            SELECT m.*, t.name 
            FROM messages m
            LEFT JOIN templates t ON m.template = t.name
            WHERE m.receiver_id = %s order by m.create_time desc
        """, (opportunity_id,))
        messages = cursor.fetchall()

        # Fetch active templates
        cursor.execute("SELECT * FROM templates WHERE active = 1")
        templates = cursor.fetchall()
        # Fetch appointments related to the opportunity
        cursor.execute("""
            SELECT a.appointment_time, cs.name AS call_status, os.name AS opportunity_status, a.canceled
            FROM appointments a
            LEFT JOIN opportunity o ON a.opportunity_id = o.id
            LEFT JOIN lead_call_status cs ON o.call_status = cs.id
            LEFT JOIN opportunity_status os ON o.opportunity_status = os.id
            WHERE a.opportunity_id = %s
        """, (opportunity_id,))
        appointments = cursor.fetchall()
        # Prepare the appointment data to return
        appointment_data = [{'time': appointment[0], 'call_status': appointment[1], 'opportunity_status': appointment[2], 'cancelled': appointment[3]} for appointment in appointments]

        # Prepare the data to return
        data = {
            'id': opportunity[0],
            'name': opportunity[1],
            'email': opportunity[2],
            'phone': opportunity[3],
            'comment': opportunity[4],
            'register_time': opportunity[5],
            'opportunity_status': opportunity[6],
            'call_status': opportunity[7],
            'sales_agent': opportunity[8],
            'sales_date': opportunity[9],
            'appointments': appointment_data,
            'messages': [{'type': message[1], 'sender': message[2], 'receiver': message[3], 'message': message[5], 'template': message[6], 'status': message[7], 'error_message': message[8], 'create_time': message[9], 'update_time': message[10]} for message in messages],
            'templates': [{'id': template[0], 'name': template[1], 'active': template[2], 'template_text': template[3]} for template in templates]
        }
        return data
    finally:
        if cursor:
            cursor.close()
    
def get_opportunity_id_by_phone_number(phone_number):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "SELECT id FROM opportunity where phone = %s"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (format_phone_number(phone_number),))

        opportunity_id = cursor.fetchone()
        if opportunity_id:
            return opportunity_id[0]
        else:
            return None
    finally:
        if cursor:
            cursor.close()

def update_opportunity_data(opportunity_id, opportunity_data):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Prepare the SQL query with placeholders
        sql = """
        UPDATE opportunity
        SET name = %s, email = %s, phone = %s, call_status = %s, sales_agent = %s,
        comment = %s, sales_date = %s
        WHERE id = %s
        """

        # Prepare the values for the query
        values = (
            opportunity_data['name'],
            opportunity_data['email'],
            format_phone_number(opportunity_data['phone']),
            opportunity_data['call_status'] if int(opportunity_data['call_status']) > 0 else None,
            #opportunity_data['opportunity_status'] if int(opportunity_data['opportunity_status']) > 0 else None,
            opportunity_data['sales_agent'] if int(opportunity_data['sales_agent']) > 0 else None,
            opportunity_data['comment'],
            opportunity_data['sales_date'],
            opportunity_id
        )

        # Execute the query with the provided values
        cursor.execute(sql, values)

        connection.commit()
    finally:
        if cursor:
            cursor.close()

def get_all_call_status():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = "SELECT id, name, color_code, text_color FROM lead_call_status"
        cursor.execute(sql)
        results = cursor.fetchall()

        call_status_list = []
        for row in results:
            call_status = {
                'id': row[0],
                'name': row[1],
                'color_code': row[2],
                'text_color': row[3]
            }
            call_status_list.append(call_status)

        return call_status_list

    finally:
        if cursor:
            cursor.close()

def get_all_opportunity_status():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = "SELECT id, name, color_code, text_color FROM opportunity_status"
        cursor.execute(sql)
        results = cursor.fetchall()

        opportunity_status_list = []
        for row in results:
            opportunity_status = {
                'id': row[0],
                'name': row[1],
                'color_code': row[2],
                'text_color': row[3]
            }
            opportunity_status_list.append(opportunity_status)

        return opportunity_status_list

    finally:
        if cursor:
            cursor.close()

def get_all_sales_agents():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = "SELECT id, name, color_code, text_color FROM sales_agent"
        cursor.execute(sql)
        results = cursor.fetchall()

        sales_agents_list = []
        for row in results:
            sales_agent = {
                'id': row[0],
                'name': row[1],
                'color_code': row[2],
                'text_color': row[3]
            }
            sales_agents_list.append(sales_agent)

        return sales_agents_list

    finally:
        if cursor:
            cursor.close()

def search_opportunities(search_term, search_type):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Prepare the SQL query with placeholders
        sql = f"SELECT * FROM opportunity WHERE {search_type} LIKE %s"
        formatted_search_term = "%" + search_term + "%"

        # Execute the query with the provided values
        cursor.execute(sql, (formatted_search_term,))

        # Fetch all matching opportunities
        results = cursor.fetchall()

        # Prepare the response data
        opportunities = []
        for row in results:
            opportunity = {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                # Add other fields as needed
            }
            opportunities.append(opportunity)

        return opportunities
    finally:
        if cursor:
            cursor.close()

def generate_report(start_date, end_date):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        query = """
            SELECT call_status, lcs.name, COUNT(*)  
            FROM opportunity 
            LEFT JOIN lead_call_status as lcs on lcs.id=call_status
            WHERE register_time >= %s AND register_time <= %s
            GROUP BY call_status
        """
        cursor.execute(query, (start_date, end_date))

        report = []
        total = 0
        for row in cursor.fetchall():
            status, name, count = row
            total += count
            report.append({
                'name': name,
                'count': count,
            })

        for item in report:
            item['percentage'] = f"{round((item['count'] / total) * 100, 2)}%"

        # Sort the report by count in descending order
        report.sort(key=lambda item: item['count'], reverse=True)

        return report
    finally:
        if cursor:
            cursor.close()

def generate_metrics(start_date, end_date):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Define the SQL queries to get the data for the conversion metrics
        load_total_opportunities = 'SELECT COUNT(*) FROM opportunity WHERE register_time BETWEEN %s AND %s'
        load_followup_opportunities = 'select count(distinct(o.id)) from appointments a join opportunity o on o.id = a.opportunity_id where (o.call_status !=9) AND o.sales_agent != 4 and o.sales_agent is not Null'
        load_self_opportunities = 'select count(distinct(o.id)) from appointments a join opportunity o on o.id = a.opportunity_id where (o.call_status !=9) AND (o.sales_agent = 4 or o.sales_agent is Null)'
        load_opportunities_not_canceled = 'select count(distinct(o.id)) from appointments a join opportunity o on o.id = a.opportunity_id where (o.call_status !=9)'
        queries = {
            'total_leads': load_total_opportunities,
            'call_booked_follow_up': f"{load_followup_opportunities} and a.appointment_time >= %s AND a.appointment_time <= %s",
            'call_show_up_follow_up': f"{load_followup_opportunities} AND o.opportunity_status != 1 AND a.appointment_time >= %s AND a.appointment_time <= %s",
            'call_booked_vsl': f"{load_self_opportunities} AND a.appointment_time >= %s AND a.appointment_time <= %s",
            'call_show_up_self': f"{load_self_opportunities} AND o.opportunity_status != 1 AND a.appointment_time >= %s AND a.appointment_time <= %s",
            'sale_conversion': f"{load_opportunities_not_canceled} AND o.opportunity_status = 2 AND o.sales_date >= %s AND o.sales_date <= %s",
            'total_calls_booked': f"{load_opportunities_not_canceled} AND a.appointment_time >= %s AND a.appointment_time <= %s",
        }

        metrics = {}
        for metric, query in queries.items():
            cursor.execute(query, (start_date, end_date))
            count = cursor.fetchone()[0]
            metrics[metric] = count

        call_booked_through_followup = metrics['call_booked_follow_up']
        call_show_up_followup = metrics['call_show_up_follow_up']
        call_booked_by_self = metrics['call_booked_vsl']
        call_show_up_self = metrics['call_show_up_self']
        sale_conversion = metrics['sale_conversion']
        total_calls_booked = metrics['total_calls_booked']
        total_leads = metrics['total_leads']
        total_calls_showed_up = call_show_up_followup + call_show_up_self

        print(f'Metrics for {start_date} & {end_date} - {call_booked_through_followup}, {call_show_up_followup}, {call_booked_by_self}, {call_show_up_self}, {sale_conversion}, {total_calls_booked}, {total_calls_showed_up}')

        # Calculate the percentages
        metrics_data = {}
        metrics_data['Total Leads'] = [total_leads, -1]
        metrics_data['Call booked through Follow up'] = [call_booked_through_followup, round((call_booked_through_followup / total_leads) * 100, 2) if total_leads != 0 else 0]
        metrics_data['Call Show up for follow up bookings'] = [call_show_up_followup, round((call_show_up_followup / call_booked_through_followup) * 100, 2) if call_booked_through_followup != 0 else 0]
        metrics_data['Call booked via VSL'] = [call_booked_by_self, round((call_booked_by_self / total_leads) * 100, 2) if total_leads != 0 else 0]
        metrics_data['Call Show up for self bookings'] = [call_show_up_self, round((call_show_up_self / call_booked_by_self) * 100, 2) if call_booked_by_self != 0 else 0]
        metrics_data['Overall Show-up'] = [total_calls_showed_up, round(((total_calls_showed_up) / (total_calls_booked)) * 100, 2) if total_calls_booked != 0 else 0]
        metrics_data['Sale Conversion'] = [sale_conversion, round((sale_conversion / (total_calls_showed_up)) * 100, 2) if total_calls_showed_up != 0 else 0]

        return metrics_data
    finally:
        if cursor:
            cursor.close()