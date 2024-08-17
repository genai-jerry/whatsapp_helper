from db.connection_manager import *
from store.opportunity_store import get_opportunity_by_id, handle_opportunity_update
import datetime
import json

def get_sales_data(page_number, page_size, opportunity_name):
    try:
        sales_data = []
        # Assuming db_connection is your database connection object
        connection = create_connection()
        cursor = connection.cursor()

        # Calculate the offset based on the page number and page size
        offset = (page_number - 1) * page_size

        # SQL query to select sales data with pagination
        query = f'''SELECT DISTINCT s.id as sale_id, o.id as opportunity_id, o.name, 
            s.sale_value as sale_value,
            s.total_paid as amount_paid,
            (s.sale_value - s.total_paid) as balance,
            pd.due_date as due_date,
            prd.name as product_name,
            pd.payment_value as due_amount,
            o.email,
            o.phone,
            pd.id
        FROM sale s
        LEFT JOIN (
            SELECT sale_id, MIN(due_date) as due_date
            FROM payment_due
            WHERE paid=0 and cancelled=0
            GROUP BY sale_id
        ) pd_min ON s.id = pd_min.sale_id
        LEFT JOIN payment_due pd ON s.id = pd.sale_id AND pd.due_date = pd_min.due_date
        LEFT JOIN products prd ON s.product = prd.id
        JOIN opportunity o ON s.opportunity_id = o.id
        WHERE o.name LIKE '%{opportunity_name}%'
        ORDER BY CASE WHEN pd.due_date IS NULL THEN 1 ELSE 0 END, pd.due_date ASC, balance DESC, o.name ASC
        LIMIT {page_size} OFFSET {offset}'''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to sales_data list
        for row in rows:
            sales_data.append({
                'opportunity_name': row[2],
                'sale_value': row[3],
                'amount_paid': row[4],
                'balance': row[5],
                'due_date': row[6],
                'opportunity_id': row[1],
                'product_name': row[7],
                'sale_id': row[0],
                'next_due_amount': row[8],
                'email': row[9],
                'phone': row[10],
                'due_id': row[11]
            })

        # Get the total number of sales records
        total_records_query = 'SELECT COUNT(*) FROM sale;'
        cursor.execute(total_records_query)
        total_records = cursor.fetchone()[0]

        # Calculate the total number of pages
        total_pages = (total_records + page_size - 1) // page_size

        # Return the sales data along with the total pages
        return sales_data, total_pages
    finally:
        # Ensure the cursor is closed in case of error
        if cursor:
            cursor.close()

def record_new_sale(opportunity_id, sale_date, sale_value, note, sales_agent, product):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "UPDATE opportunity SET opportunity_status = %s WHERE id = %s"
        values = (2, opportunity_id)
        cursor.execute(sql, values)
        opportunity = get_opportunity_by_id(opportunity_id)
        
        # Insert data into 'sales' table
        sql_sales = '''INSERT INTO sale (opportunity_id, sale_date, sale_value, 
                note, sales_agent, product, total_paid, is_final, currency, cancelled,
                call_setter) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        sales_data = (opportunity_id, sale_date, sale_value, note, sales_agent, 
                      product, 0, False, 'INR', False, opportunity['call_setter'])
        cursor.execute(sql_sales, sales_data)
        connection.commit()
        opportunity_data = {
                'id': opportunity['id'],
                'name': opportunity['name'],
                'email': opportunity['email'],
                'phone': opportunity['phone'],
                'fbp': opportunity['fbp'],
                'fbc': opportunity['fbc'],
                'ad_account': opportunity['ad_account']
        }
        handle_opportunity_update(opportunity_data, 
                                 'opportunity_status', '2')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_sales_details(opportunity_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "SELECT * FROM sales WHERE opportunity_id = %s"
        cursor.execute(sql, (opportunity_id,))
        results = cursor.fetchall()
        sales_details = []
        for row in results:
            sales_details.append({
                'sale_date': row[1],
                'sale_value': row[2],
                'currency': row[3],
                'note': row[4],
                'sales_agent': row[5],
                'product': row[6]
            })
        return sales_details
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_all_sales(opportunity_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = '''SELECT id, opportunity_id, sale_date, sale_value, total_paid, currency, note, 
            sales_agent, product, is_final FROM sale WHERE opportunity_id = %s'''
        cursor.execute(sql, (opportunity_id,))
        results = cursor.fetchall()
        sales_list = []
        for row in results:
            sales = {
                'id': row[0],
                'opportunity_id': row[1],
                'sale_date': row[2],
                'sale_value': row[3],
                'amount_paid': row[4],
                'currency': row[5],
                'note': row[6],
                'sales_agent': row[7],
                'product': row[8],
                'is_final': row[9]
            }
            sales_list.append(sales)
        return sales_list
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def mark_sale_not_final(sale_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "UPDATE sale SET is_final = %s WHERE id = %s"
        values = (False, sale_id)
        cursor.execute(sql, values)
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def mark_sale_final(sale_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = "UPDATE sale SET is_final = %s WHERE id = %s"
        values = (True, sale_id)
        cursor.execute(sql, values)
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_monthly_sales_data(start_date = None, end_date = None):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = end_date - datetime.timedelta(days=365)

        # SQL query to select sale, collection, and pending amount for each month
        query = f'''SELECT 
                EXTRACT(MONTH FROM month_year) as month,
                EXTRACT(YEAR FROM month_year) as year,
                SUM(total_sales) AS total_sales,
                SUM(total_payments) AS total_payments,
                SUM(total_outstanding) AS total_outstanding
            FROM (
                SELECT 
                    DATE_FORMAT(sale_date, '%Y-%m-01') AS month_year,
                    sale_value AS total_sales,
                    0 AS total_payments,
                    sale_value - total_paid AS total_outstanding
                FROM 
                    sale
                WHERE 
                    sale_date BETWEEN '{start_date}' AND '{end_date}' 
                    AND is_final = 1 AND cancelled != 1
                
                UNION ALL
                
                SELECT 
                    DATE_FORMAT(payment_date, '%Y-%m-01') AS month_year,
                    0 AS total_sales,
                    payment_value AS total_payments,
                    0 AS total_outstanding
                FROM 
                    payments
                WHERE 
                    payment_date BETWEEN '{start_date}' AND '{end_date}' 
                    AND is_deposit = 0
            ) combined_data
            GROUP BY 
                month_year
            ORDER BY 
                month_year;'''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to monthly_sales_data list
        monthly_sales_data = []
        for row in rows:
            month = datetime.datetime.strptime(str(row[0]), '%m').strftime('%b')
            monthly_sales_data.append({
                'month': month,
                'year': datetime.datetime.strptime(str(row[1]), '%Y').strftime('%Y'),
                'sale_amount': int(row[2]),
                'collection_amount': int(row[3]),
                'pending_amount': int(row[4])
            })

        return monthly_sales_data
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_final_sales_for_month(start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select final sales for a specific month
        query = f'''SELECT 
            SUM(s.sale_value) as sale_value,
            SUM(s.total_paid) as total_paid,
            SUM(s.sale_value - s.total_paid) as pending_amount
        FROM sale s
        WHERE s.sale_date >= '{start_date}' AND s.sale_date <= '{end_date}' AND s.is_final = 1'''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to sales list
        sales = []
        for row in rows:
            sales.append({
                'sale_value': int(row[0]),
                'total_paid': int(row[1]),
                'pending_amount': int(row[2])
            })

        return sales
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_all_opportunities_with_final_sales( page, page_size, start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select opportunities with final sales for a specific month
        query = f'''SELECT 
            o.id as opportunity_id,
            o.name as opportunity_name,
            s.sale_date as date_of_sale,
            s.sale_value as sale_amount,
            s.total_paid as amount_paid,
            (s.sale_value - s.total_paid) as pending_amount,
            s.is_final as is_final
        FROM opportunity o
        LEFT JOIN sale s ON o.id = s.opportunity_id
        WHERE s.sale_date >= '{start_date}' AND s.sale_date <= '{end_date}' AND s.is_final = 1
        Order by date_of_sale DESC
        LIMIT {page_size} OFFSET {(page - 1) * page_size}
        '''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to opportunities list
        opportunities = []
        for row in rows:
            opportunities.append({
            'opportunity_id': row[0],
            'opportunity_name': row[1],
            'date_of_sale': row[2],
            'sale_amount': int(row[3]),
            'amount_paid': int(row[4]),
            'pending_amount': int(row[5]),
            'is_final': bool(row[6])
            })
        total_count_query = f'''SELECT COUNT(*) FROM opportunity o
            LEFT JOIN sale s ON o.id = s.opportunity_id
            WHERE s.sale_date >= '{start_date}' AND s.sale_date <= '{end_date}' AND s.is_final = 1'''

        cursor.execute(total_count_query)
        total_count = cursor.fetchone()[0]

        return opportunities, total_count
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()  

def get_sales_report_by_call_setter(start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select sales report grouped by call setter
        query = f'''SELECT 
            s.call_setter as call_setter,
            sa.name as call_setter_name,
            SUM(s.sale_value) as total_sale_value,
            SUM(s.total_paid) as total_payment,
            SUM(s.sale_value - s.total_paid) as pending_amount
        FROM sale s
        LEFT JOIN sales_agent sa ON sa.id = s.call_setter
        WHERE s.sale_date >= '{start_date}' AND s.sale_date <= '{end_date}' AND s.is_final = 1
        GROUP BY call_setter_name, call_setter'''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to sales_report list
        sales_report = []
        for row in rows:
            sales_report.append({
                'call_setter': row[0],
                'call_setter_name': row[1],
                'total_sale_value': int(row[2]),
                'total_payment': int(row[3]),
                'pending_amount': int(row[4])
            })
        return sales_report
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_sales_opportunities_by_call_setter(page, page_size, start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select opportunities with final sales for a specific month
        query = f'''SELECT 
            o.id as opportunity_id,
            o.name as opportunity_name,
            s.sale_value as total_sale_value,
            s.total_paid as total_payment
        FROM opportunity o
        LEFT JOIN sale s ON o.id = s.opportunity_id
        WHERE s.sale_date >= '{start_date}' AND s.sale_date <= '{end_date}' AND s.is_final = 1
        GROUP BY opportunity_name
        ORDER BY opportunity_name
        LIMIT {page_size} OFFSET {(page - 1) * page_size}
        '''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to opportunities list
        opportunities = []
        for row in rows:
            opportunities.append({
                'opportunity_id': row[0],
                'opportunity_name': row[1],
                'total_sale_value': int(row[2]),
                'total_payment': int(row[3])
            })

        return opportunities
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_payments_report_call_setters(start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select payments within the specified duration
        query = f'''SELECT s.call_setter, sa.name as call_setter_name, 
        SUM(p.payment_value) as total_payment,
        SUM(s.sale_value) as total_sale_value,
        SUM(s.sale_value - s.total_paid) as pending_amount
        FROM payments p
        LEFT JOIN sale s ON p.sale = s.id
        LEFT JOIN sales_agent sa ON sa.id = s.call_setter
        WHERE p.payment_date >= '{start_date}' AND p.payment_date <= '{end_date}' AND s.is_final = 1
        GROUP BY call_setter, call_setter_name'''


        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to payments list
        payments = []
        for row in rows:
            payments.append({
                'call_setter': row[0],
                'call_setter_name': row[1],
                'total_payment': int(row[2]),
                'total_sale_value': int(row[3]),
                'pending_amount': int(row[4])
            })

        return payments
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_payments_oppotunities_by_call_setter(page, page_size, start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select opportunities with final sales for a specific month
        query = f'''SELECT 
            o.name as opportunity_name,
            sa.name as call_setter,
            s.sale_date,
            s.sale_value,
            s.total_paid,
            p.payment_value as payment_value,
            s.is_final as sale_status,
            p.payment_date as payment_date,
            o.id as opportunity_id
        FROM opportunity o
        LEFT JOIN sale s ON o.id = s.opportunity_id
        LEFT JOIN sales_agent sa ON sa.id = s.call_setter
        LEFT JOIN payments p ON p.sale = s.id
        WHERE p.payment_date >= '{start_date}' AND p.payment_date <= '{end_date}'
        ORDER BY p.payment_date DESC
        LIMIT {page_size} OFFSET {(page - 1) * page_size}
        '''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to opportunities list
        opportunities = []
        for row in rows:
            opportunities.append({
            'opportunity_name': row[0],
            'call_setter': row[1],
            'sale_date': row[2],
            'sale_value': int(row[3]),
            'total_paid': int(row[4]),
            'payment_value': int(row[5]),
            'is_final': row[6],
            'payment_date': row[7],
            'opportunity_id': row[8]
            })

        # Count the total number of rows
        count_query = f'''SELECT COUNT(*) FROM opportunity o
                LEFT JOIN sale s ON o.id = s.opportunity_id
                LEFT JOIN payments p ON p.sale = s.id
                WHERE p.payment_date >= '{start_date}' AND p.payment_date <= '{end_date}'
                '''
        cursor.execute(count_query)
        total_count = cursor.fetchone()[0]

        return opportunities, total_count
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_payments_oppotunities_by_sales_agent(page, page_size, start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select opportunities with final sales for a specific month
        query = f'''SELECT 
            o.name as opportunity_name,
            sa.name as sales_agent,
            s.sale_date,
            s.sale_value,
            s.total_paid,
            p.payment_value as payment_value,
            s.is_final as sale_status,
            p.payment_date as payment_date,
            o.id as opportunity_id
        FROM opportunity o
        LEFT JOIN sale s ON o.id = s.opportunity_id
        LEFT JOIN sales_agent sa ON sa.id = s.sales_agent
        LEFT JOIN payments p ON p.sale = s.id
        WHERE p.payment_date >= '{start_date}' AND p.payment_date <= '{end_date}'
        ORDER BY p.payment_date DESC
        LIMIT {page_size} OFFSET {(page - 1) * page_size}
        '''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to opportunities list
        opportunities = []
        for row in rows:
            opportunities.append({
            'opportunity_name': row[0],
            'sales_agent': row[1],
            'sale_date': row[2],
            'sale_value': int(row[3]),
            'total_paid': int(row[4]),
            'payment_value': int(row[5]),
            'is_final': row[6],
            'payment_date': row[7],
            'opportunity_id': row[8]
        })

        # Count the total number of rows
        count_query = f'''SELECT COUNT(*) FROM opportunity o
                LEFT JOIN sale s ON o.id = s.opportunity_id
                LEFT JOIN payments p ON p.sale = s.id
                WHERE p.payment_date >= '{start_date}' AND p.payment_date <= '{end_date}'
                '''
        cursor.execute(count_query)
        total_count = cursor.fetchone()[0]

        return opportunities, total_count
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_payments_report_sales_agents(start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select payments within the specified duration
        query = f'''SELECT s.sales_agent, sa.name as sales_agent_name, 
        SUM(p.payment_value) as total_payment,
        SUM(s.sale_value) as total_sale_value,
        SUM(s.sale_value - s.total_paid) as pending_amount
        FROM payments p
        LEFT JOIN sale s ON p.sale = s.id
        LEFT JOIN sales_agent sa ON sa.id = s.sales_agent
        WHERE p.payment_date >= '{start_date}' AND p.payment_date <= '{end_date}' AND s.is_final = 1
        GROUP BY sales_agent, sales_agent_name'''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to payments list
        payments = []
        for row in rows:
            payments.append({
                'sales_agent': row[0],
                'sales_agent_name': row[1],
                'total_payment': int(row[2]),
                'total_sale_value': int(row[3]),
                'pending_amount': int(row[4])
            })

        return payments
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_sales_opportunities_by_sales_agent(page, page_size, start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select opportunities with final sales for a specific month
        query = f'''SELECT 
            o.id as opportunity_id,
            o.name as opportunity_name,
            s.sale_value as total_sale_value,
            s.total_paid as total_payment
        FROM opportunity o
        LEFT JOIN sale s ON o.id = s.opportunity_id
        WHERE s.sale_date >= '{start_date}' AND s.sale_date <= '{end_date}' AND s.is_final = 1
        GROUP BY opportunity_name
        ORDER BY opportunity_name
        LIMIT {page_size} OFFSET {(page - 1) * page_size}
        '''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to opportunities list
        opportunities = []
        for row in rows:
            opportunities.append({
                'opportunity_id': row[0],
                'opportunity_name': row[1],
                'total_sale_value': int(row[2]),
                'total_payment': int(row[3])
            })

        return opportunities
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_payments_collected(start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select payments within the specified duration
        query = f'''SELECT 
            CASE
            WHEN is_deposit = 0 THEN 'Instalments'
            WHEN is_deposit = 1 THEN 'Deposits'
            END as payment_category,
            COUNT(*) as payment_count,
            SUM(payment_value) as total_payment,
            SUM(s.sale_value) as total_sale_value,
            SUM(s.sale_value - s.total_paid) as pending_amount
        FROM payments
        JOIN sale s ON payments.sale = s.id
        WHERE payment_date >= '{start_date}' AND payment_date <= '{end_date}'
        GROUP BY payment_category'''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to payments list
        payments = []
        for row in rows:
            payments.append({
                'payment_category': row[0],
                'payment_count': int(row[1]),
                'total_payment': int(row[2]),
                'total_sale_value': int(row[3]),
                'pending_amount': int(row[4])
            })
        return payments
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_opportunities_for_payments_collected(page, page_size, start_date=None, end_date=None):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Get the current date
        if not end_date:
            end_date = datetime.date.today()

        if not start_date:
            start_date = datetime.date(end_date.year, end_date.month, 1)

        # SQL query to select opportunities with final sales for a specific month
        query = f'''SELECT 
            o.name as opportunity_name,
            s.sale_date,
            s.sale_value,
            s.total_paid,
            p.payment_date,
            p.payment_value,
            s.is_final as sale_status,
            o.id as opportunity_id
        FROM opportunity o
        LEFT JOIN sale s ON o.id = s.opportunity_id
        LEFT JOIN payments p ON p.sale = s.id
        WHERE p.payment_date >= '{start_date}' AND p.payment_date <= '{end_date}'
        ORDER BY p.payment_date DESC
        LIMIT {page_size} OFFSET {(page - 1) * page_size}
        '''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to opportunities list
        opportunities = []
        for row in rows:
            opportunities.append({
            'opportunity_name': row[0],
            'sale_date': row[1],
            'sale_value': int(row[2]),
            'total_paid': int(row[3]),
            'payment_date': row[4],
            'payment_amount': int(row[5]),
            'is_final': row[6],
            'opportunity_id': row[7]
        })

        # Count the total number of rows
        count_query = f'''SELECT COUNT(*) FROM opportunity o
                        LEFT JOIN sale s ON o.id = s.opportunity_id
                        LEFT JOIN payments p ON p.sale = s.id
                        WHERE p.payment_date >= '{start_date}' AND p.payment_date <= '{end_date}'
                        '''
        cursor.execute(count_query)
        total_count = cursor.fetchone()[0]

        return opportunities, total_count
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()