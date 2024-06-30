from db.connection_manager import *
from datetime import datetime

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