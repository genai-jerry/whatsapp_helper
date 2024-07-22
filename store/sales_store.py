from db.connection_manager import *
from store.opportunity_store import get_opportunity_by_id, handle_opportunity_update

def get_sales_data(page_number, page_size, opportunity_name):
    try:
        sales_data = []
        # Assuming db_connection is your database connection object
        connection = create_connection()
        cursor = connection.cursor()

        # Calculate the offset based on the page number and page size
        offset = (page_number - 1) * page_size

        # SQL query to select sales data with pagination
        query = f'''SELECT o.name, s.sale_value as sale_value,
            s.total_paid as amount_paid,
            (s.sale_value - s.total_paid) as balance,
            pd.due_date as due_date,
            o.id as opportunity_id,
            prd.name as product_name,
            s.id as sale_id
            FROM sale s
            JOIN opportunity o ON s.opportunity_id = o.id
            LEFT JOIN payment_due pd ON s.id = pd.sale_id
            LEFT JOIN products prd ON s.product = prd.id
            WHERE o.name LIKE '%{opportunity_name}%'
            ORDER BY pd.due_date DESC, balance DESC, o.name ASC
            LIMIT {page_size} OFFSET {offset};'''

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Format each row into a dictionary and append to sales_data list
        for row in rows:
            sales_data.append({
                'opportunity_name': row[0],
                'sale_value': row[1],
                'amount_paid': row[2],
                'balance': row[3],
                'due_date': row[4],
                'opportunity_id': row[5],
                'product_name': row[6],
                'sale_id': row[7]
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

        # Insert data into 'sales' table
        sql_sales = '''INSERT INTO sale (opportunity_id, sale_date, sale_value, 
                note, sales_agent, product, total_paid, is_final, currency, cancelled) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        sales_data = (opportunity_id, sale_date, sale_value, note, sales_agent, product, 0, False, 'INR', False)
        cursor.execute(sql_sales, sales_data)
        connection.commit()
        opportunity = get_opportunity_by_id(opportunity_id)
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