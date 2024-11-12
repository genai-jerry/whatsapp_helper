from flask_login import current_user
from db.connection_manager import *
from utils import format_phone_number
from datetime import datetime, timedelta
from facebook.fb_ads_manager import handle_opportunity_update
from typing import Optional
from store.employee_store import get_sales_agent_id_for_user
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

def get_user_id_for_sales_agent(cursor, agent_id):
    if agent_id == None:
        return None
    sql_user = "SELECT user_id FROM sales_agent WHERE id = %s"
    cursor.execute(sql_user, (agent_id,))
    user = cursor.fetchone()[0]
    return user

def store_opportunity(opportunity_data):
    try:
        date_str = opportunity_data['date'] if opportunity_data['date'] else None
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ') if date_str else None
        print(f'Got date {date}')
        name = opportunity_data['name'] if opportunity_data['name'] else None
        email = opportunity_data['email'] if opportunity_data['email'] else ''
        phone = format_phone_number(opportunity_data['phone']) if opportunity_data['phone'] else None

        comment = opportunity_data['comment'] if 'comment' in opportunity_data and opportunity_data['comment'] else None
        optin_status_name = opportunity_data['optin_status'] if 'optin_status' in opportunity_data and opportunity_data['optin_status'] else None
        opportunity_status_name = opportunity_data['opportunity_status'] if 'opportunity_status' in opportunity_data and opportunity_data['opportunity_status'] else None
        sales_agent_name = opportunity_data['agent'] if 'agent' in opportunity_data and opportunity_data['agent'] else None
        campaign = opportunity_data['campaign'] if 'campaign' in opportunity_data and opportunity_data['campaign'] else None
        ad_name = opportunity_data['ad_name'] if 'ad_name' in opportunity_data and opportunity_data['ad_name'] else None
        ad_id = opportunity_data['ad_id'] if 'ad_id' in opportunity_data and opportunity_data['ad_id'] else None
        ad_medium = opportunity_data['ad_medium'] if 'ad_medium' in opportunity_data and opportunity_data['ad_medium'] else None
        ad_fbp = opportunity_data['ad_fbp'] if 'ad_fbp' in opportunity_data and opportunity_data['ad_fbp'] else None
        ad_fbc = opportunity_data['ad_fbc'] if 'ad_fbc' in opportunity_data and opportunity_data['ad_fbc'] else None
        ad_placement = opportunity_data['ad_placement'] if 'ad_placement' in opportunity_data and opportunity_data['ad_placement'] else None
        ad_account = opportunity_data['ad_account'] if 'ad_account' in opportunity_data and opportunity_data['ad_account'] else None

        # Insert the opportunity
        connection = create_connection()
        cursor = connection.cursor()
        print(f'Getting ids for {opportunity_status_name}, {optin_status_name} and {sales_agent_name}')
        opportunity_status = get_opportunity_status_id(cursor, opportunity_status_name) if opportunity_status_name != None else None
        optin_status = get_optin_status_id(cursor, optin_status_name) if optin_status_name != None else None
        sales_agent = get_sales_agent_id(cursor, sales_agent_name) if sales_agent_name != None else None

        print(f'Got {opportunity_status}, {optin_status} and {sales_agent}')


        # Check if the email already exists in the table
        sql_check_email = "SELECT COUNT(*) FROM opportunity WHERE email = %s"
        cursor.execute(sql_check_email, (email,))
        email_exists = cursor.fetchone()[0]
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if email_exists == 0:
            # Insert the opportunity
            sql_insert = """
                INSERT INTO opportunity (name, email, phone, register_time, last_register_time, 
                opportunity_status, call_status, call_setter, comment, campaign, ad_name, ad_id, medium,
                ad_fbp, ad_fbc, video_watched, ad_placement, ad_account)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (name, email, phone, date, current_datetime, opportunity_status, optin_status, sales_agent, comment, campaign, 
                                        ad_name, ad_id, ad_medium, ad_fbp, ad_fbc, False, ad_placement, ad_account))
            connection.commit()
            print("Opportunity inserted successfully.")
        else:
            print("Email already exists in the table.")
            
            # Update the opportunity
            sql_update = """
                UPDATE opportunity 
                SET opportunity_status = %s, call_status = %s, call_setter = %s, comment = %s, campaign = %s,
                ad_name = %s, ad_id = %s, medium = %s, ad_fbp = %s, ad_fbc = %s, last_register_time = %s, ad_placement = %s, ad_account = %s
                WHERE email = %s or phone = %s
            """
            cursor.execute(sql_update, (opportunity_status, optin_status, sales_agent, comment, campaign, ad_name, 
                                        ad_id, ad_medium, ad_fbp, ad_fbc, current_datetime, ad_placement, ad_account,
                                        email, 
                                        phone))
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

def update_opportunity_status(opportunity_data, status_columns=None, agent_user_id=None):
    status = opportunity_data['status']
    # Update data in 'opportunities' table using a prepared statement
    try:
        print(f'Modifying opportunity with status {status}')
        connection = create_connection()
        cursor = connection.cursor()
        status_type = opportunity_data['status_type']
        params = []
        sales_agent_id = get_sales_agent_id_for_user(agent_user_id, cursor) if agent_user_id else None
        print(f'Sales agent id {sales_agent_id}')
        # Define the SQL query with placeholders
        if status_type == "call_status":
            sql = "UPDATE opportunity SET call_status = %s, last_updated = NOW()"
        elif status_type == "opportunity_status":
            sql = "UPDATE opportunity SET opportunity_status = %s, last_updated = NOW()"
        elif status_type == "agent":
            sql = "UPDATE opportunity SET assigned_to = %s, optin_caller = %s, last_updated = NOW()"
            params.append(sales_agent_id)
        else:
            raise ValueError("Invalid status type")

        params.append(status)
        if status_columns:
            for column, value in status_columns.items():
                sql += f", {column} = %s "
                params.append(value)
        params.append(opportunity_data['opportunity_id'])

        sql = sql + " WHERE id = %s"
        # Prepare the query and execute it with the provided values
        cursor.execute(sql, params)

        connection.commit()
        print("Opportunity updated successfully.")  

        # Retrieve the updated opportunity data
        select_sql = """
            SELECT 
            o.id,
            o.name,
            o.email,
            o.phone,
            o.ad_fbp,
            o.ad_fbc,
            o.ad_account
            FROM 
            opportunity o
            WHERE o.id = %s
        """
        cursor.execute(select_sql, (opportunity_data['opportunity_id'],))
        row = cursor.fetchone() # Fetch the updated opportunity data
        opportunity = {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'phone': row[3],
            'fbp': row[4],
            'fbc': row[5],
            'ad_account': row[6]
        }
        if status_type == "call_status":
            print(f'Storing optin call record for call status {status} and agent {sales_agent_id}')
            store_optin_call_record({'opportunity_id': opportunity_data['opportunity_id'],
                                     'call_date': datetime.now(),
                                     'call_duration': 0,
                                     'call_type': status_type,
                                     'call_status': status,
                                     'agent_id': sales_agent_id})
        if status_type != "agent":
            handle_opportunity_update(opportunity, status_type, status)

    finally:
        if cursor:
            cursor.close()

def store_optin_call_record(opportunity_data):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        sql = '''INSERT INTO optin_call_record (opportunity_id, call_date, call_duration, 
                call_type, call_status, agent_id) 
                VALUES (%s, %s, %s, %s, %s, %s)'''
        cursor.execute(sql, (opportunity_data['opportunity_id'], 
                             opportunity_data['call_date'], 
                             opportunity_data['call_duration'], 
                             opportunity_data['call_type'], 
                             opportunity_data['call_status'], 
                             opportunity_data['agent_id']))
        connection.commit()
    except Exception as e:
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

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
            sales_agent sa ON o.call_setter = sa.id
            """
        select_sql = """
            SELECT 
            o.name, 
            o.email, 
            o.phone, 
            o.last_register_time, 
            os.name AS opportunity_status, 
            cs.name AS call_status, 
            sa.name AS sales_agent,
            o.id,
            os.color_code AS opportunity_status_color,
            cs.color_code AS call_status_color,
            sa.color_code AS sales_agent_color,
            os.text_color AS opportunity_status_text_color,
            cs.text_color AS call_status_text_color,
            sa.text_color AS sales_agent_text_color,
            o.campaign,
            o.ad_name,
            o.medium,
            o.video_watched,
            o.ad_placement,
            o.ad_account
            FROM 
            opportunity o
            LEFT JOIN 
            lead_call_status cs ON o.call_status = cs.id
            LEFT JOIN 
            opportunity_status os ON o.opportunity_status = os.id
            LEFT JOIN 
            sales_agent sa ON o.optin_caller = sa.id
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
            filter_types = filter_type.split(",")
            filter_values = filter_value.split(",")
            print(f'Filter Types {filter_values}')
            if search_term or search_type:
                count_sql += " AND"
                select_sql += " AND"
            for i in range(len(filter_types)):
                if i>0:
                    count_sql += " AND"
                    select_sql += " AND"
                if isinstance(filter_values[i], int) and int(filter_values[i]) == 11:
                    count_sql += f" {filter_types[i]} IS NULL"
                    select_sql += f" {filter_types[i]} IS NULL"
                else:
                    count_sql += f" {filter_types[i]} = %s"
                    select_sql += f" {filter_types[i]} = %s"
                    if isinstance(filter_values[i], int):
                        params.append(int(filter_values[i]))
                    else:
                        params.append(filter_values[i])

        select_sql += " ORDER BY o.last_register_time desc LIMIT %s OFFSET %s"

        print(f'Count SQL {count_sql}')
        # Count the total number of opportunities
        cursor.execute(count_sql, params)  # Only pass the search term and filter value to the count query
        params.extend([per_page, (page - 1) * per_page])
        total_items = cursor.fetchone()[0]

        # Calculate the total number of pages
        total_pages = (total_items + per_page - 1) // per_page
        print(f'Select SQL {select_sql}')
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
            'sales_agent_text_color': row[13],
            'campaign': row[14],
            'ad_name': row[15],
            'ad_medium': row[16],
            'video_watched': row[17],
            'ad_placement': row[18],
            'ad_account': row[19]
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
                opportunity.call_setter AS call_setter,
                opportunity.gender AS gender,
                opportunity.company_type AS company_type,
                opportunity.challenge_type AS challenge_type,
                opportunity.lead_event_fired as lead_even_fired,
                opportunity.submit_application_event_fired as submit_application_event_fired,
                opportunity.sale_event_fired as sale_event_fired,
                opportunity.ad_fbp as fbp,
                opportunity.ad_fbc as fbc,
                opportunity.ad_account as ad_account,
                opportunity.optin_caller as optin_caller,
                opportunity.address,
                opportunity.same_state,
                opportunity.gst
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
            SELECT CONVERT_TZ(a.appointment_time, 'UTC', 'Asia/Kolkata') AS appointment_time, cs.name AS call_status, 
                       os.name AS appointment_status, a.canceled, 
                       CONVERT_TZ(a.created_at, 'UTC', 'Asia/Kolkata') AS appointment_create_time
            FROM appointments a
            LEFT JOIN opportunity o ON a.opportunity_id = o.id
            LEFT JOIN lead_call_status cs ON o.call_status = cs.id
            LEFT JOIN opportunity_status os ON a.status = os.id
            WHERE a.opportunity_id = %s
        """, (opportunity_id,))
        appointments = cursor.fetchall()
        # Prepare the appointment data to return
        appointment_data = [{'time': appointment[0], 'call_status': appointment[1],
                              'appointment_status': appointment[2], 
                              'cancelled': appointment[3],
                               'appointment_create_time': appointment[4] } for appointment in appointments]

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
            'call_setter': opportunity[8],
            'gender': opportunity[9],
            'company_type': opportunity[10],
            'challenge_type': opportunity[11],
            'lead_event_fired': opportunity[12],
            'submit_application_event_fired': opportunity[13],
            'sale_event_fired': opportunity[14],
            'fbp': opportunity[15],
            'fbc': opportunity[16],
            'ad_account': opportunity[17],
            'optin_caller': opportunity[18],
            'address': opportunity[19],
            'same_state': opportunity[20],
            'gst': opportunity[21],
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

def get_opportunity_by_email(email):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Define the SQL query with placeholders
        sql = '''SELECT id, name, email, phone, ad_fbp as fbp, ad_fbc as fbc, ad_account as ad_account 
                FROM opportunity where email = %s'''

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (email,))

        row = cursor.fetchone()
        if row:
            opportunity = {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'fbp': row[4],
                'fbc': row[5],
                'ad_account': row[6]
            }
            print(f'Returning Opportunity {opportunity}')
            return opportunity
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
        SET name = %s, email = %s, phone = %s, call_status = %s, call_setter = %s, optin_caller = %s,
        comment = %s, gender = %s, company_type = %s, challenge_type = %s, address = %s, same_state = %s, gst = %s
        WHERE id = %s
        """

        # Prepare the values for the query
        values = (
            opportunity_data['name'],
            opportunity_data['email'],
            format_phone_number(opportunity_data['phone']),
            opportunity_data['call_status'] if int(opportunity_data['call_status']) > 0 else None,
            #opportunity_data['opportunity_status'] if int(opportunity_data['opportunity_status']) > 0 else None,
            opportunity_data['call_setter'] if int(opportunity_data['call_setter']) > 0 else None,
            opportunity_data['optin_caller'] if int(opportunity_data['optin_caller']) > 0 else None,
            opportunity_data['comment'],
            opportunity_data['gender'] if opportunity_data['gender'] != '-1' else None,
            opportunity_data['company_type'] if opportunity_data['company_type'] != '-1' else None,
            opportunity_data['challenge_type'] if opportunity_data['challenge_type'] != '-1' else None,
            opportunity_data['address'],
            opportunity_data['same_state'],
            opportunity_data['gst'],
            opportunity_id
        )

        # Execute the query with the provided values
        cursor.execute(sql, values)
        if int(opportunity_data['call_status']) > 0:
            opportunity = get_opportunity_by_id(opportunity_id)
            data = {
                'id': opportunity['id'],
                'name': opportunity['name'],
                'email': opportunity['email'],
                'phone': opportunity['phone'],
                'opportunity_status': opportunity['opportunity_status'],
                'call_status': opportunity['call_status'],
                'fbp': opportunity['fbp'],
                'fbc': opportunity['fbc'],
                'ad_account': opportunity['ad_account']
             }
            handle_opportunity_update(data, 
                                  'call_status', f'{data["call_status"]}')
        connection.commit()
    finally:
        if cursor:
            cursor.close()

def get_all_call_status():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = "SELECT id, name, color_code, text_color FROM lead_call_status where active = 1"
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

        sql = "SELECT id, name, color_code, text_color FROM opportunity_status where active = 1"
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

def get_all_company_types():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "SELECT id, name FROM company_type"
        cursor.execute(sql)
        results = cursor.fetchall()
        company_types_list = []
        for row in results:
            company_types_list.append({'id': row[0], 'name': row[1]})
        return company_types_list
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_all_challenge_types():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "SELECT id, name FROM challenge_type"
        cursor.execute(sql)
        results = cursor.fetchall()
        challenge_types_list = []
        for row in results:
            challenge_types_list.append({'id': row[0], 'name': row[1]})
        return challenge_types_list
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

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


def generate_report(start_date, end_date):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        end_date = f'{end_date} 23:59:59'
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
        end_date = f'{end_date} 23:59:59'
        print(f'Getting metrics for {start_date} and {end_date}')
        # Define the SQL queries to get the data for the conversion metrics
        load_total_opportunities = 'SELECT COUNT(*) FROM opportunity WHERE register_time BETWEEN %s AND %s'
        load_followup_opportunities = 'select count(distinct(o.id)) from appointments a join opportunity o on o.id = a.opportunity_id where o.call_setter != 4 and o.call_setter is not Null'
        load_self_opportunities = 'select count(distinct(o.id)) from appointments a join opportunity o on o.id = a.opportunity_id where (a.status !=6 and a.status != 5) AND (o.call_setter = 4 or o.call_setter is Null)'
        load_opportunities_not_canceled = 'select count(distinct(o.id)) from appointments a join opportunity o on o.id = a.opportunity_id join sale s on s.opportunity_id = o.id where (a.status !=6 and a.status != 5)'
        queries = {
            'total_leads': load_total_opportunities,
            'call_booked_follow_up': f"{load_followup_opportunities} and a.appointment_time BETWEEN %s AND %s",
            'call_show_up_follow_up': f"{load_followup_opportunities} AND a.status in (2,3,4) AND a.appointment_time BETWEEN %s AND %s",
            'call_booked_vsl': f"{load_self_opportunities} AND a.appointment_time BETWEEN %s AND %s",
            'call_show_up_self': f"{load_self_opportunities} AND a.status in (2,3,4) AND a.appointment_time BETWEEN %s AND %s",
            'sale_conversion': f"SELECT count(s.id) from sale s where s.sale_date BETWEEN %s AND %s AND s.is_final = 1 AND s.cancelled != 1",
            'total_calls_booked': f"{load_opportunities_not_canceled} AND a.appointment_time BETWEEN %s AND %s",
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
        total_calls_booked = call_booked_through_followup + call_booked_by_self
        total_leads = metrics['total_leads']
        total_calls_showed_up = call_show_up_followup + call_show_up_self

        print(f'Total Calls Showed {total_calls_showed_up}/ Total Calls Booked {total_calls_booked}')

        # Calculate the percentages
        metrics_data = {}
        metrics_data['Total Leads'] = [total_leads, -1]
        metrics_data['Call booked through Follow up'] = [call_booked_through_followup, round((call_booked_through_followup / total_leads) * 100, 2) if total_leads != 0 else 0]
        metrics_data['Call Show up for follow up bookings'] = [call_show_up_followup, round((call_show_up_followup / call_booked_through_followup) * 100, 2) if call_booked_through_followup != 0 else 0]
        metrics_data['Call booked via VSL'] = [call_booked_by_self, round((call_booked_by_self / total_leads) * 100, 2) if total_leads != 0 else 0]
        metrics_data['Call Show up for self bookings'] = [call_show_up_self, round((call_show_up_self / call_booked_by_self) * 100, 2) if call_booked_by_self != 0 else 0]
        metrics_data['Overall Show-up'] = [total_calls_showed_up, round((total_calls_showed_up / total_calls_booked) * 100, 2) if total_calls_booked != 0 else 0]
        metrics_data['Sale Conversion'] = [sale_conversion, round((sale_conversion / (total_calls_showed_up)) * 100, 2) if total_calls_showed_up != 0 else 0]

        return metrics_data
    finally:
        if cursor:
            cursor.close()

def handle_video_watch_event(email):
    # Lookup opportunity by email
    opportunity = get_opportunity_by_email(email)
    if opportunity is None:
        print(f'Opportunity with email {email} not found')
        return
    print(f'Opportunity ID {opportunity}')
    # Fire the Facebook event
    handle_opportunity_update(opportunity, 'video_watched')
    # Set the opportunity status to 15
    opportunity_data = {'status': '15', 'status_type': 'call_status', 'opportunity_id': opportunity['id']}
    # Update the opportunity status in your database
    update_opportunity_status(opportunity_data)

def search_opportunities(search_term, search_type):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Prepare the SQL query with placeholders
        sql = f"SELECT id, name, email, phone FROM opportunity WHERE {search_type} LIKE %s"
        formatted_search_term = "%" + search_term + "%"
        cursor.execute(sql, (formatted_search_term,))
        results = cursor.fetchall()
        opportunities = []
        for row in results:
            opportunity = {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],   
            }
            opportunities.append(opportunity)
        return opportunities
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        
def get_total_opportunity_count_for_month(month, year):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = '''SELECT 
            SUM(CASE WHEN ad_name IS NULL THEN 1 ELSE 0 END) as direct_leads,
            SUM(CASE WHEN ad_name IS NOT NULL THEN 1 ELSE 0 END) as ad_leads
        FROM opportunity 
        WHERE MONTHNAME(last_register_time) = %s AND EXTRACT(YEAR FROM last_register_time) = %s'''
        cursor.execute(sql, (month, year))
        result = cursor.fetchone()
        return {
            'direct_leads': result[0] or 0,  # Handle NULL case
            'ad_leads': result[1] or 0,      # Handle NULL case
            'total_leads': (result[0] or 0) + (result[1] or 0)
        }
    finally:
        if cursor:
            cursor.close()

def list_all_new_leads(assigned = False, user_id=None, page=1, page_size=10):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        agent_id = get_sales_agent_id_for_user(user_id)
        sql = '''SELECT id, name, email, phone, register_time, call_status, register_time FROM opportunity 
                WHERE call_status IS NULL'''
        if user_id:
            sql += f" AND (assigned_to = %s OR optin_caller = %s) ORDER BY register_time DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * page_size
            cursor.execute(sql, (user_id, agent_id, page_size, offset))
        else:
            if assigned:
                sql += " AND (assigned_to IS NOT NULL OR optin_caller IS NOT NULL) ORDER BY register_time DESC LIMIT %s OFFSET %s"
            else:
                sql += " AND (assigned_to IS NULL) ORDER BY register_time DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * page_size
            cursor.execute(sql, (page_size, offset))
        results = cursor.fetchall()

        # Get the total count of opportunities
        count_sql = "SELECT COUNT(*) FROM opportunity WHERE call_status IS NULL"
        if user_id:
            count_sql += " AND (assigned_to = %s OR optin_caller = %s)"
            cursor.execute(count_sql, (user_id, agent_id))
        else:
            if assigned:
                count_sql += " AND (assigned_to IS NOT NULL OR optin_caller IS NOT NULL)"
            else:
                count_sql += " AND assigned_to IS NULL"
            cursor.execute(count_sql)
        total_count = cursor.fetchone()[0]

        opportunities = []
        for row in results:
            opportunities.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'register_time': row[4],
                'call_status': row[5],
                'last_updated': row[6],
            })
        return opportunities, total_count
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def list_all_leads_for_follow_up(assigned = False, user_id=None, page=1, page_size=10):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        agent_id = get_sales_agent_id_for_user(user_id)
        # Return all leads that have a call_status of 12, 13, 14
        sql = '''SELECT id, name, email, phone, register_time, call_status, last_updated FROM opportunity 
                WHERE call_status IN (3,12, 13)'''
        if user_id:
            sql += f" AND (assigned_to = %s OR optin_caller = %s) "
            if assigned:
                sql += "ORDER BY COALESCE(last_updated, register_time) ASC LIMIT %s OFFSET %s"
            else:
                sql += "ORDER BY register_time DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * page_size
            cursor.execute(sql, (user_id, agent_id, page_size, offset))
        else:
            if assigned:
                sql += " AND (assigned_to IS NOT NULL OR optin_caller IS NOT NULL)"
                sql += " ORDER BY COALESCE(last_updated, register_time) ASC LIMIT %s OFFSET %s"
            else:
                sql += " AND assigned_to IS NULL"
                sql += " ORDER BY register_time DESC LIMIT %s OFFSET %s"
            
            offset = (page - 1) * page_size
            cursor.execute(sql, (page_size, offset))
        results = cursor.fetchall()
        opportunities = []
        for row in results:
            opportunities.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'register_time': row[4],
                'call_status': row[5],
                'last_updated': row[6],
            })
        
        count_sql = "SELECT COUNT(*) FROM opportunity WHERE call_status IN (12, 13)"
        if user_id:
            count_sql += " AND (assigned_to = %s OR optin_caller = %s)"
            cursor.execute(count_sql, (user_id, agent_id))
        else:
            if assigned:
                count_sql += " AND assigned_to IS NOT NULL"
            else:
                count_sql += " AND assigned_to IS NULL"
            cursor.execute(count_sql)
        total_count = cursor.fetchone()[0]
        return opportunities, total_count
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def list_all_leads_for_no_show(assigned = False, user_id=None, page=1, page_size=10):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        agent_id = get_sales_agent_id_for_user(user_id)
        sql = '''SELECT DISTINCT o.id, o.name, o.email, o.phone, o.register_time, o.call_status, 
                o.last_updated, a.appointment_time
                FROM opportunity o
                LEFT JOIN appointments a on a.opportunity_id = o.id
                WHERE (o.call_status IS NULL OR o.call_status not in (14)) 
                AND a.status = 1'''
        if user_id:
            sql += f" AND (o.assigned_to = %s OR o.optin_caller = %s) ORDER BY a.appointment_time DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * page_size
            cursor.execute(sql, (user_id, agent_id, page_size, offset))
        else:
            if assigned:
                sql += " AND (o.assigned_to IS NOT NULL OR o.optin_caller IS NOT NULL) ORDER BY a.appointment_time DESC LIMIT %s OFFSET %s"
            else:
                sql += " AND o.assigned_to IS NULL ORDER BY a.appointment_time DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * page_size
            cursor.execute(sql, (page_size, offset))
        results = cursor.fetchall()
        opportunities = []
        for row in results:
            opportunities.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'register_time': row[4],
                'call_status': row[5],
                'last_updated': row[7],
                'appointment_time': row[7],
            })
        count_sql = '''SELECT COUNT(*) FROM opportunity o
                    LEFT JOIN appointments a on a.opportunity_id = o.id 
                    WHERE (o.call_status IS NULL OR o.call_status not in (14)) 
                    AND a.status = 1'''
        if user_id:
            count_sql += " AND (o.assigned_to = %s OR o.optin_caller = %s)"
            cursor.execute(count_sql, (user_id, agent_id))
        else:
            if assigned:
                count_sql += " AND o.assigned_to IS NOT NULL"
            else:
                count_sql += " AND o.assigned_to IS NULL"
            cursor.execute(count_sql)
        total_count = cursor.fetchone()[0]
        return opportunities, total_count
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def assign_opportunity_to_agent(opportunity_id, agent_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sales_agent_id = get_sales_agent_id_for_user(agent_id)
            
        # If not assigned, proceed with assignment
        sql = "UPDATE opportunity SET assigned_to = %s, optin_caller = %s WHERE id = %s AND assigned_to IS NULL"
        cursor.execute(sql, (agent_id, sales_agent_id, opportunity_id))
        updated_count = cursor.rowcount
        print(f'Updated {updated_count} rows')
        if updated_count == 0:
            print(f'Opportunity {opportunity_id} is already assigned to an agent')
            raise ValueError("Failed to assign opportunity - may already be assigned")
            
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_all_opportunities_updated(since_days=7, agent_user_id=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Create a list of the last 7 days
        days = []
        for i in range(since_days):
            day = datetime.now() - timedelta(days=i)
            days.append(day.date())
        agent_id = get_sales_agent_id_for_user(agent_user_id, cursor) if agent_user_id else None
        # Get the data from database
        start_date = datetime.now() - timedelta(days=since_days)
        sql = '''SELECT COUNT(DISTINCT(opportunity_id)), DATE(call_date) as update_date 
                FROM optin_call_record 
                WHERE DATE(call_date) >= %s'''
        if agent_id:
            sql += " AND agent_id = %s GROUP BY DATE(call_date)"
            cursor.execute(sql, (start_date, agent_id))
        else:
            sql += " GROUP BY DATE(call_date)"
            cursor.execute(sql, (start_date,))
            
        # Convert results to dictionary for easier lookup
        results = cursor.fetchall()
        updates_dict = {row[1]: row[0] for row in results}

        sql = '''SELECT COUNT(a.id), DATE(a.created_at) as book_date 
                FROM appointments a
                JOIN opportunity o on o.id = a.opportunity_id
                WHERE DATE(a.created_at) >= %s'''
        if agent_id:
            sql += " AND o.call_setter = %s GROUP BY DATE(a.created_at)"
            cursor.execute(sql, (start_date, agent_id))
        else:
            sql += " AND o.call_setter IS NOT NULL GROUP BY DATE(a.created_at)"
            cursor.execute(sql, (start_date,))
        results = cursor.fetchall()
        book_dict = {row[1]: row[0] for row in results}
        
        sql = '''SELECT COUNT(s.id), DATE(s.sale_date) as sale_date 
                FROM sale s
                WHERE DATE(s.sale_date) >= %s'''
        if agent_id:
            sql += " AND s.call_setter = %s GROUP BY DATE(s.sale_date)"
            cursor.execute(sql, (start_date, agent_id))
        else:
            sql += " AND s.call_setter IS NOT NULL GROUP BY DATE(s.sale_date)"
            cursor.execute(sql, (start_date,))
        results = cursor.fetchall()
        sale_dict = {row[1]: row[0] for row in results}
        
        # Create final list with all days, using 0 for days with no updates
        opportunities = []
        for day in days:
            opportunities.append({
                'date': day,
                'count': updates_dict.get(day, 0),
                'book_count': book_dict.get(day, 0),
                'sale_count': sale_dict.get(day, 0),
                'is_today': day == datetime.now().date()
            })
            
        return opportunities
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_call_setter(opportunity_id, user_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sales_agent_id = get_sales_agent_id_for_user(user_id)
        sql = "UPDATE opportunity SET call_setter = %s WHERE id = %s"
        cursor.execute(sql, (sales_agent_id, opportunity_id))
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()