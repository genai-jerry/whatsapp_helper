from db.connection_manager import *
from datetime import datetime
from store.opportunity_store import get_opportunity_by_email

def store_payment(sale_id, payment_data):
    try:
        payment_date = payment_data['payment_date'] if 'payment_date' in payment_data else None
        payment_amount = payment_data['payment_amount'] if 'payment_amount' in payment_data else None
        charges = payment_data['charges'] if 'charges' in payment_data else None
        payment_mode = payment_data['payment_mode'] if 'payment_mode' in payment_data else None
        invoice_link = payment_data['invoice_link'] if 'invoice_link' in payment_data else None
        is_deposit = payment_data['is_deposit'] if 'is_deposit' in payment_data else False

        # Insert the payment
        connection = create_connection()
        cursor = connection.cursor()

        # Insert the payment
        sql_insert = """
        INSERT INTO payments (payment_date, payment_value, charges, payment_mode, invoice_link, is_deposit, sale)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (payment_date, payment_amount, charges, payment_mode, invoice_link, is_deposit, sale_id))
        
        update_sale_payment(cursor, sale_id, payment_amount, is_deposit)

        connection.commit()
        print("Payment inserted successfully.")
    except Exception as e:
        print(str(e))
        raise e
    finally:
        if cursor:
            cursor.close()

def update_sale_payment(cursor, sale_id, payment_amount, payment_is_deposit):
    try:
        is_sale_final = not payment_is_deposit
        # Get the sale details
        sql_select_sale = "SELECT total_paid FROM sale WHERE id = %s"
        cursor.execute(sql_select_sale, (sale_id,))
        sale_details = cursor.fetchone()
        paid_amount = sale_details[0]
        
        # Update the paid amount and pending amount based on the payment amount received
        updated_paid_amount = int(paid_amount) + int(payment_amount)
        
        # Update the sale details
        sql_update_sale = "UPDATE sale SET total_paid = %s, is_final = %s WHERE id = %s"
        cursor.execute(sql_update_sale, (updated_paid_amount, is_sale_final, sale_id))
        
        print("Sale payment updated successfully.")
    except Exception as e:
        print(str(e))
        raise e
    finally:
        if cursor:
            cursor.close()

def list_payments_for_sale(sale_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql_select = '''SELECT payment_date, payment_value, pm.name, charges, invoice_link
            FROM payments 
            JOIN payment_mode as pm ON payments.payment_mode = pm.id
            WHERE sale = %s'''
        cursor.execute(sql_select, (sale_id,))
        payments = cursor.fetchall()
        payment_data = []
        for payment in payments:
            payment_date = payment[0]
            payment_amount = payment[1]
            payment_mode = payment[2]
            charges = payment[3]
            invoice_link = payment[4]
            payment_data.append({
            'date': payment_date,
            'amount': payment_amount,
            'mode': payment_mode,
            'charges': charges,
            'invoice_link': invoice_link
            })
        
        return payment_data
    except Exception as e:
        print(str(e))
        raise e
    finally:
        if cursor:
            cursor.close()

def store_sales(sale_details):
    try:
        # Assuming db_connection is your database connection object
        connection = create_connection()
        cursor = connection.cursor()
        # Prepare the SQL query to insert sale details
            # This is a generic template, adjust the table name and columns as per your database schema
        query = """
            INSERT INTO sale (sale_value, sale_date, total_paid, is_final, note, opportunity_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        # Loop through the sale details and insert each sale object
        for sale in sale_details:
            print(f'Checking for opportunity with email: {sale["email"]}')
            opportunity = get_opportunity_by_email(sale['email'])
            if not opportunity:
                print(f'Opportunity not found for email: {sale["email"]}')
                continue
            
            is_final = False if sale['token'] else True
            gross_amount = float(sale['gross'].replace(',', ''))
            sale_date = datetime.strptime(sale['date'], '%b %d %Y')
            # Execute the query with the sale details
            cursor.execute(query, (gross_amount, sale_date, 0, is_final, sale['comments'], opportunity['id']))
        # Commit the transaction
        connection.commit()
        
        print("Sale details stored successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        cursor.rollback()  # Rollback in case of error
    finally:
        if cursor:
            cursor.close()

def get_first_sale_id(opportunity_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql_select = "SELECT id FROM sale WHERE opportunity_id = %s ORDER BY sale_date ASC LIMIT 1"
        cursor.execute(sql_select, (opportunity_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        print(str(e))
        raise e
    finally:
        if cursor:
            cursor.close()

def store_payments(payment_details):
    cursor = None
    try:
        # Assuming db_connection is your database connection object
        connection = create_connection()
        cursor = connection.cursor()
        
        # SQL query to insert payment data into the payments table
        query = """
        INSERT INTO payments (payment_value, charges, payment_mode_reference, currency, payment_date, is_deposit, invoice_link, sale, opportunity, accountant, payment_mode, refunded)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Assuming default values for some fields and mapping others directly
        default_charges = 0  # Assuming a default value for demonstration
        default_is_deposit = False  # Assuming a default value
        default_refunded = False  # Assuming a default value
        
        # Other fields like sale, opportunity, accountant, and payment_mode are set to NULL for this example

        # Execute the query with the payment details
        for payment in payment_details:
            opportunity = get_opportunity_by_email(payment['email'])
            if opportunity:
                payment_amount = float(payment['payment_amount'].replace(',', ''))
                sale_id = get_first_sale_id(opportunity['id'])
                payment_date = datetime.strptime(payment['payment_date'], '%b %d %Y')
                cursor.execute(query, (
                    payment_amount,  # payment_value maps to payment_amount
                    default_charges,  # charges set to a default value
                    None,  # payment_mode_reference not provided, assuming NULL
                    None,  # currency not provided, assuming NULL
                    payment_date,
                    default_is_deposit,  # is_deposit set to a default value
                    payment['link'],  # Assuming invoice_link maps to link
                    sale_id,  # sale not provided, assuming NULL
                    opportunity['id'],  # opportunity not provided, assuming NULL
                    None,  # accountant not provided, assuming NULL
                    None,  # payment_mode not provided, assuming NULL
                    default_refunded  # refunded set to a default value
                ))
        
        # Commit the transaction
        connection.commit()
        print("Payment details stored successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if cursor:
            cursor.rollback()  # Rollback in case of error
    finally:
        if cursor:
            cursor.close()