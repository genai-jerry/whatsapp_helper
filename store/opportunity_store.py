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

        # Define the SQL query with placeholders
        sql = "UPDATE opportunity set opportunity_status=%s where id=%s"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (status, opportunity_data['id']))

        if status == "2":
            # Update the sale_date to current date
            print('Updating sale date')
            sql_update_sale_date = "UPDATE opportunity SET sales_date = CURRENT_DATE() WHERE id = %s"
            cursor.execute(sql_update_sale_date, (opportunity_data['id'],))

        connection.commit()
        print("Opportunity updated successfully.")
    finally:
        if cursor:
            cursor.close()

def get_opportunities(page, per_page, search_term=None, search_type=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        print("Getting opportiunities")

        # Prepare the SQL queries
        count_sql = "SELECT COUNT(*) FROM opportunity"
        select_sql = """
            SELECT 
                o.name, 
                o.email, 
                o.phone, 
                o.register_time, 
                os.name AS opportunity_status, 
                cs.name AS call_status, 
                sa.name AS sales_agent, 
                o.id
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
        if search_term and search_type:
            count_sql += f" WHERE {search_type} LIKE %s"
            select_sql += f" WHERE o.{search_type} LIKE %s"
            params.append("%" + search_term + "%")

        select_sql += " ORDER BY o.register_time desc LIMIT %s OFFSET %s"
        print(count_sql, params)
        # Count the total number of opportunities
        cursor.execute(count_sql, params)  # Only pass the search term to the count query
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
                'id': row[7]
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
                opportunity.sales_agent AS sales_agent
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
        SET name = %s, email = %s, phone = %s, call_status = %s, opportunity_status = %s, sales_agent = %s,
        comment = %s
        WHERE id = %s
        """

        # Prepare the values for the query
        values = (
            opportunity_data['name'],
            opportunity_data['email'],
            format_phone_number(opportunity_data['phone']),
            opportunity_data['call_status'] if int(opportunity_data['call_status']) > 0 else None,
            opportunity_data['opportunity_status'] if int(opportunity_data['opportunity_status']) > 0 else None,
            opportunity_data['sales_agent'] if int(opportunity_data['sales_agent']) > 0 else None,
            opportunity_data['comment'],
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

        sql = "SELECT id, name FROM lead_call_status"
        cursor.execute(sql)
        results = cursor.fetchall()

        call_status_list = []
        for row in results:
            call_status = {
                'id': row[0],
                'name': row[1]
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

        sql = "SELECT id, name FROM opportunity_status"
        cursor.execute(sql)
        results = cursor.fetchall()

        opportunity_status_list = []
        for row in results:
            opportunity_status = {
                'id': row[0],
                'name': row[1]
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

        sql = "SELECT id, name FROM sales_agent"
        cursor.execute(sql)
        results = cursor.fetchall()

        sales_agents_list = []
        for row in results:
            sales_agent = {
                'id': row[0],
                'name': row[1]
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