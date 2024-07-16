from db.connection_manager import *

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
            o.id as opportunity_id
            FROM sale s
            JOIN opportunity o ON s.opportunity_id = o.id
            LEFT JOIN payment_due pd ON s.id = pd.sale_id
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
                'opportunity_id': row[5]
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