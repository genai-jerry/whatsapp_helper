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
                sales_agent sa ON o.sales_agent = sa.id;
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