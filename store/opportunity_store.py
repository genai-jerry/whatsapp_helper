from db.connection_manager import *
import json

opportunities = {}

def get_opportunity_status_id(cursor, opportunity_status_name):
    sql_opportunity_status = "SELECT id FROM opportunity_status WHERE name = %s"
    cursor.execute(sql_opportunity_status, (opportunity_status_name,))
    opportunity_status = cursor.fetchone()[0]
    return opportunity_status

def get_call_status_id(cursor, call_status_name):
    sql_call_status = "SELECT id FROM lead_call_status WHERE name = %s"
    cursor.execute(sql_call_status, (call_status_name,))
    call_status = cursor.fetchone()[0]
    return call_status

def get_sales_agent_id(cursor, sales_agent_name):
    sql_sales_agent = "SELECT id FROM sales_agent WHERE name = %s"
    cursor.execute(sql_sales_agent, (sales_agent_name,))
    sales_agent = cursor.fetchone()[0]
    return sales_agent

def store_opportunity(opportunity_data):
    date = opportunity_data['date']
    name = opportunity_data['name']
    email = opportunity_data['email']
    phone = opportunity_data['phone']
    call_status_name = opportunity_data['call_status']
    opportunity_status_name = opportunity_data['opportunity_status']
    sales_agent_name = opportunity_data['agent']
    campaign = opportunity_data['campaign']
    # Insert the opportunity
    connection = create_connection()
    cursor = connection.cursor()

    print(f'Getting opportunity status id for {opportunity_status_name}')
    opportunity_status = get_opportunity_status_id(cursor, opportunity_status_name)
    print(f'Getting call status id for {call_status_name}')
    call_status = get_call_status_id(cursor, call_status_name)
    print(f'Getting sales agent id for {sales_agent_name}')
    sales_agent = get_sales_agent_id(cursor, sales_agent_name)
    print(f'Got {opportunity_status}, {call_status} and {sales_agent}')

    sql_insert = """
        INSERT INTO opportunity (name, email, phone, register_time, opportunity_status, call_status, sales_agent)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql_insert, (name, email, phone, date, opportunity_status, call_status, sales_agent))
    connection.commit()
    print("Opportunity inserted successfully.")
    cursor.close()

def remove_opportunity(email):
    # Delete data from 'opportunities' table using a prepared statement
    try:
        connection = create_connection()

        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "DELETE FROM opportunities where email = %s"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (email,))

        connection.commit()
        print("Opportunity deleted successfully.")
    finally:
        if cursor:
            cursor.close()

def update_opportunity(email, opportunity_data):
    status = opportunity_data['status']
    # Update data in 'opportunities' table using a prepared statement
    try:
        print('Modifying opportunity')
        connection = create_connection()
        
        cursor = connection.cursor()

        # Define the SQL query with placeholders
        sql = "UPDATE opportunities set status=%s where email=%s"

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (status, email))

        connection.commit()
        print("Opportunity updated successfully.")
    finally:
        if cursor:
            cursor.close()

def get_opportunities():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        sql = """
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
            INNER JOIN 
                lead_call_status cs ON o.call_status = cs.id
            INNER JOIN 
                opportunity_status os ON o.opportunity_status = os.id
            INNER JOIN 
                sales_agent sa ON o.sales_agent = sa.id
            ORDER BY o.register_time desc
        """
        cursor.execute(sql)
        results = cursor.fetchall()

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

        return opportunities

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
                opportunity_status.name AS opportunity_status,
                lead_call_status.id AS call_status,
                sales_agent.name AS sales_agent
            FROM 
                opportunity
            LEFT JOIN 
                opportunity_status ON opportunity.opportunity_status = opportunity_status.id
            LEFT JOIN 
                lead_call_status ON opportunity.call_status = lead_call_status.id
            LEFT JOIN 
                sales_agent ON opportunity.sales_agent = sales_agent.id
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
        cursor.execute(sql, (phone_number,))

        opportunity_id = cursor.fetchone()[0]
        return opportunity_id
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
        SET name = %s, email = %s, phone = %s, call_status = %s
        WHERE id = %s
        """

        # Prepare the values for the query
        values = (
            opportunity_data['name'],
            opportunity_data['email'],
            opportunity_data['phone'],
            opportunity_data['call_status'],
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