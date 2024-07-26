from db.connection_manager import *
from datetime import datetime
from store.opportunity_store import get_opportunity_by_email

def store_payment(sale_id, payment_data):
    try:
        payment_date = payment_data['payment_date'] if 'payment_date' in payment_data else None
        payment_amount = payment_data['payment_amount'] if 'payment_amount' in payment_data else None
        charges = payment_data['charges'] if 'charges' in payment_data and payment_data['charges'] != '' else 0
        payment_mode = payment_data['payment_mode'] if 'payment_mode' in payment_data else None
        invoice_link = payment_data['invoice_link'] if 'invoice_link' in payment_data else None
        is_deposit = payment_data['is_deposit'] if 'is_deposit' in payment_data else False
        payment_mode_reference = payment_data['payment_mode_reference'] if 'payment_mode_reference' in payment_data else None
        payment_method = payment_data['payment_method'] if 'payment_method' in payment_data else None
        payor_email = payment_data['payor_email'] if 'payor_email' in payment_data else None
        payor_phone = payment_data['payor_phone'] if 'payor_phone' in payment_data else None
        opportunity_id = payment_data['opportunity_id'] if 'opportunity_id' in payment_data else None

        if payor_email is None or payor_phone is None:
            email, phone = get_opportunity_email_and_phone(sale_id)
            if payor_email is None:
                payor_email = email
            if payor_phone is None:
                payor_phone = phone

        # Insert the payment
        connection = create_connection()
        cursor = connection.cursor()

        # Insert the payment
        sql_insert = """
        INSERT INTO payments (payment_date, payment_value, charges, 
            payment_mode, payment_method, payment_mode_reference,
            invoice_link, is_deposit, sale, refunded, payor_email, payor_phone, opportunity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (payment_date, payment_amount, charges, 
                                    payment_mode, payment_method, payment_mode_reference,
                                    invoice_link, is_deposit, sale_id, 0, payor_email, 
                                    payor_phone, opportunity_id))
        
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
        sql_select = '''SELECT payment_date, payment_value, pm.name, 
            charges, invoice_link, is_deposit, payments.id
            FROM payments 
            LEFT JOIN payment_mode as pm ON payments.payment_mode = pm.id
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
            is_deposit = payment[5]
            id = payment[6]
            payment_data.append({
            'date': payment_date,
            'amount': payment_amount,
            'mode': payment_mode,
            'charges': charges,
            'invoice_link': invoice_link,
            'is_deposit': is_deposit,
            'id': id
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
            INSERT INTO sale (sale_value, sale_date, total_paid, is_final, note, cancelled, opportunity_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
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
            cursor.execute(query, (gross_amount, sale_date, 0, is_final, sale['comments'], False, opportunity['id']))
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
   
    # Assuming default values for some fields and mapping others directly
    default_charges = 0  # Assuming a default value for demonstration
    default_is_deposit = False  # Assuming a default value
    
    # Other fields like sale, opportunity, accountant, and payment_mode are set to NULL for this example

    # Execute the query with the payment details
    for payment in payment_details:
        opportunity = get_opportunity_by_email(payment['email'])
        if opportunity:
            payment_amount = float(payment['payment_amount'].replace(',', ''))
            tax = float(payment['GST'].replace(',', ''))
            sale_id = get_first_sale_id(opportunity['id'])
            payment_date = datetime.strptime(payment['payment_date'], '%b %d %Y')

            store_payment(sale_id, {
                'payment_date': payment_date,
                'payment_amount': payment_amount + tax,
                'charges': default_charges,
                'payment_mode': None,
                'invoice_link': payment['link'],
                'is_deposit': default_is_deposit,
                'opportunity_id': opportunity['id']
            })
    
    print("Payment details stored successfully.")

def store_payments_due(sale_id, due_date, amount_due):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO payment_due (payment_value, due_date, sale_id, paid, cancelled)
            VALUES (%s, %s, %s, %s, %s)
            """
        due_date = datetime.strptime(due_date, '%Y-%m-%d')
        payment_value = float(amount_due.replace(',', ''))
        cursor.execute(query, (payment_value, due_date, sale_id, False, False))
        connection.commit()
        print("Payment due details stored successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        cursor.rollback()
    finally:
        if cursor:
            cursor.close()

def list_payment_dues(sale_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql_select = '''SELECT payment_value, due_date, id
            FROM payment_due WHERE sale_id = %s and paid = False and cancelled = False'''
        cursor.execute(sql_select, (sale_id,))
        payment_dues = cursor.fetchall()
        payment_due_data = []
        for payment_due in payment_dues:
            payment_value = payment_due[0]
            due_date = payment_due[1]
            payment_due_id = payment_due[2]
            payment_due_data.append({
            'amount': payment_value,
            'due_date': due_date,
            'id': payment_due_id
            })
        return payment_due_data
    except Exception as e:
        print(str(e))
        raise e
    finally:
        if cursor:
            cursor.close()

def process_payment(email, phone, amount, charges, mode, method, date, reference):
    # Validate the input data
    if not email or amount <= 0 or charges < 0:
        raise ValueError("Invalid payment data")
    
    # Assuming you have a database connection established as db_connection
    
    opportunity_id = None
    opportunity = get_opportunity_by_email(email)   
    print(f'Got payment for the opportunity: {opportunity}')
    if opportunity:
        opportunity_id = opportunity['id']

    payment_date = datetime.now()
    
    payment_mode = get_payment_mode_id_by_name(mode)

    sale_id = get_first_sale_id(opportunity_id)

    if sale_id:
        store_payment(sale_id, {
            'payment_date': payment_date,
            'payment_amount': amount,
            'charges': charges,
            'payment_mode': payment_mode,
            'payment_mode_reference': reference,
            'payment_method': method,
            'payor_email': email,
            'payor_phone': phone,
            'is_deposit': False,
            'opportunity_id': opportunity_id
        })
    else:
        try:
            connection = create_connection()
            cursor = connection.cursor()
        
            # Prepare the SQL query to insert the payment record
            query = """
            INSERT INTO payments (payment_value, charges, payment_method, payment_mode_reference,
            payment_date, opportunity, sale, payment_mode, is_deposit, refunded, payor_email, payor_phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Execute the query with the provided data
            cursor.execute(query, (amount, charges, method, reference, payment_date, 
                                opportunity_id, sale_id, payment_mode, False, False, email, phone))
            
            # Commit the transaction
            connection.commit()
        
            # Return a success message or boolean to indicate success
            return True
        except Exception as e:
            # Optionally, rollback the transaction if something goes wrong
            connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()

def get_payment_mode_id_by_name(mode):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql_select = "SELECT id FROM payment_mode WHERE name = %s"
        cursor.execute(sql_select, (mode,))
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

def get_unassigned_payments():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql_select = '''SELECT payment_date, payment_value, pm.name, charges, 
            invoice_link, payor_email, payor_phone, payments.id
            FROM payments 
            LEFT JOIN payment_mode as pm ON payments.payment_mode = pm.id
            WHERE opportunity IS NULL OR sale IS NULL'''
        cursor.execute(sql_select)
        payments = cursor.fetchall()
        payment_data = []
        for payment in payments:
            payment_date = payment[0]
            payment_amount = payment[1]
            payment_mode = payment[2]
            charges = payment[3]
            invoice_link = payment[4]
            email = payment[5]
            phone = payment[6]
            payment_id = payment[7]
            payment_data.append({
                'date': payment_date,
                'amount': payment_amount,
                'mode': payment_mode,
                'charges': charges,
                'invoice_link': invoice_link,
                'email': email,
                'phone': phone,
                'payment_id': payment_id
            })
        return payment_data
    except Exception as e:
        print(str(e))
        raise e
    finally:
        if cursor:
            cursor.close()

def get_opportunity_id(sale_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql_select = "SELECT opportunity_id FROM sale WHERE id = %s"
        cursor.execute(sql_select, (sale_id,))
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

def get_opportunity_email_and_phone(sale_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql_select = "SELECT o.email, o.phone FROM opportunity AS o INNER JOIN sale AS s ON o.id = s.opportunity_id WHERE s.id = %s"
        cursor.execute(sql_select, (sale_id,))
        result = cursor.fetchone()
        if result:
            email, phone = result
            return email, phone
        else:
            return None, None
    except Exception as e:
        print(str(e))
        raise e
    finally:
        if cursor:
            cursor.close()

def assign_payment_to_sale(payment_id, sale_id, payment_amount):
    try:
        print(f"Assigning payment {payment_id} to sale {sale_id}")
        opportunity_id = get_opportunity_id(sale_id)
        connection = create_connection()
        cursor = connection.cursor()
        sql_update = "UPDATE payments SET sale = %s, opportunity = %s WHERE id = %s"
        cursor.execute(sql_update, (sale_id, opportunity_id, payment_id))

        update_sale_payment(cursor, sale_id, payment_amount, False)
        connection.commit()
        print("Payment assigned to sale successfully.")
        return opportunity_id
    except Exception as e:
        print(str(e))
        raise e
    finally:
        if cursor:
            cursor.close()

def mark_payment_as_deposit(payment_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql_update = "UPDATE payments SET is_deposit = True WHERE id = %s"
        cursor.execute(sql_update, (payment_id,))
        
        # Get the sale ID associated with the payment
        sql_select = "SELECT sale FROM payments WHERE id = %s"
        cursor.execute(sql_select, (payment_id,))
        sale_id = cursor.fetchone()[0]
        
        # Update the sale to be not final
        sql_update_sale = "UPDATE sale SET is_final = False WHERE id = %s"
        cursor.execute(sql_update_sale, (sale_id,))
        
        connection.commit()
        print("Payment marked as deposit successfully.")
    except Exception as e:
        print(str(e))
        raise e
    finally:
        if cursor:
            cursor.close()

def mark_payment_due_as_paid(payment_due_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Update the payment due record based on the is_paid flag
        sql_update = "UPDATE payment_due SET paid = %s WHERE id = %s"
        cursor.execute(sql_update, (1, payment_due_id))
        
        connection.commit()
        print("Payment due marked as paid successfully.")
    except Exception as e:
        raise e
    finally:
        if cursor:
            cursor.close()

def mark_payment_due_as_cancelled(payment_due_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Update the payment due record based on the is_paid flag
        sql_update = "UPDATE payment_due SET cancelled = %s WHERE id = %s"
        cursor.execute(sql_update, (1, payment_due_id))
        
        connection.commit()
        print("Payment due marked as cancelled successfully.")
    except Exception as e:
        raise e
    finally:
        if cursor:
            cursor.close()