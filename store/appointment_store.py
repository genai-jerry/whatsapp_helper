from datetime import datetime
from utils import format_phone_number
import pytz
from db.connection_manager import *
from facebook.fb_ads_manager import *
from .opportunity_store import get_opportunity_by_id

def store_appointment(profile_details, application_form_details, mentor_name, import_app=False):
    try:
        # Create a new database connection
        cnx = create_connection()
        # Create a new cursor
        cursor = cnx.cursor()

        grade = grade_application(application_form_details)
        # Set verified to true if grade is 0, else set it to false
        verified = True if grade == 0 else False
        print(f'Verified: {verified}')

        # Look up the opportunity using the name or email in the opportunities table
        query = "SELECT id FROM opportunity WHERE email = %s"
        cursor.execute(query, (profile_details['email'],))
        opportunity_id = cursor.fetchone()
        cursor.fetchall()
        if opportunity_id is not None:
            opportunity_id = opportunity_id[0]
        else:
            opportunity_id = None
        print(f'Opportunity ID: {opportunity_id}')
        # Look up the mentor using the mentor name in the mentors table
        query = "SELECT id FROM sales_agent WHERE name = %s"
        mentor_name = ''.join(c for c in mentor_name if c.isalpha())
        cursor.execute(query, (mentor_name,))
        mentor_id = cursor.fetchone()
        cursor.fetchall()
        if mentor_id is not None:
            mentor_id = mentor_id[0]
        else:
            mentor_id = None
        print(f'Mentor ID: {mentor_id}')
        # Define the SQL query for inserting a new appointment with opportunity_id and mentor_id as foreign keys
        query = """
        INSERT INTO appointments (name, email, telephone, career_challenge, challenge_description, urgency, salary_range, 
        expected_salary, current_employer, financial_situation, grade, mentor_id, opportunity_id, appointment_time, 
        verified, conflicted, canceled, confirmed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, False)
        """
        date_str = application_form_details['appointment_time']
        if import_app:
            appointment_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        else:
            appointment_time = datetime.strptime(date_str, '%A, %d %B %Y %I:%M %p') if date_str else None
        # Convert appointment_time from IST to GMT
        if appointment_time:
            appointment_time = appointment_time.astimezone(pytz.timezone('GMT'))

        # Check if there is another appointment with the same appointment time
        print(f'Checking if appointment exists at time {appointment_time}')
        conflict_query = "SELECT id FROM appointments WHERE appointment_time = %s"
        cursor.execute(conflict_query, (appointment_time,))
        existing_appointment = cursor.fetchone()
        cursor.fetchall()

        # If there is an existing appointment, set the conflicted column to True
        if existing_appointment:
            conflicted = True
        else:
            conflicted = False
        print(f'Appointment is conflicted: {conflicted}')
        outcome = application_form_details.get('outcome')
        if outcome == 'Canceled':
            canceled = True
        else:
            canceled = False
        # Define the values for the SQL query
        values = (
            profile_details.get('name', ''),
            profile_details.get('email', ''),
            format_phone_number(profile_details.get('telephone', '')) if profile_details.get('telephone') else None,
            application_form_details.get('career_challenge', ''),
            application_form_details.get('challenge_description', ''),
            application_form_details.get('urgency', ''),
            application_form_details.get('salary_range', ''),
            application_form_details.get('expected_salary', ''),
            application_form_details.get('current_employer', ''),
            application_form_details.get('financial_situation', ''),
            grade,
            mentor_id,
            opportunity_id,
            appointment_time,
            verified,
            conflicted,
            canceled
        )

        # Execute the SQL query
        cursor.execute(query, values)

        # Update the opportunity table if opportunity_id is present
        if opportunity_id is not None:
            print(f'Updating the opportunity status for the opportunity {opportunity_id}')
            update_query = "UPDATE opportunity SET call_status = 8 WHERE id = %s"
            cursor.execute(update_query, (opportunity_id,))
        else:
            print('Opportunity not found. Skipping update of opportunity status')

        # Commit the transaction
        cnx.commit()

        # Get the ID of the newly inserted appointment
        appointment_id = cursor.lastrowid

        # Send a FB event
        handle_opportunity_update(get_opportunity_by_id(opportunity_id), 'call_status', 
                                  '8')

        # Return the appointment ID
        return appointment_id

    except Exception as err:
        print(f"Error: {err}")
        raise err

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()


def get_scores_from_database():
    try:
        # Create a new database connection
        cnx = create_connection()

        # Create a new cursor
        cursor = cnx.cursor()

        # Define the SQL query for getting the max scores
        query = "SELECT * FROM max_scores"

        # Execute the SQL query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Convert rows into a dictionary
        max_scores = {row[1]: row[2] for row in rows}

        # Return the max scores
        return max_scores

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()

from store.config_store import retrieve_config

def grade_application(application_form_details):

    # Calculate the total score
    total_score = calculate_final_score(application_form_details)

    if total_score == 0:
        return 0

    # Calculate the max possible score
    # Get the max possible score from the config store
    max_possible_score = retrieve_config('max_possible_score')
    print(f'Max possible score: {max_possible_score}')

    # Calculate the score percentage
    score_percentage = int(total_score) / int(max_possible_score)
    print(f'Score percentage: {score_percentage}')

    # Determine the grade based on the score percentage
    if score_percentage >= 0.8:
        grade = 3
    elif score_percentage >= 0.5:
        grade = 2
    else:
        grade = 1

    print(f'Grade: {grade}')
    # Return the grade
    return grade

def calculate_final_score(application_form_details):
    # Get the max scores from the database
    max_scores = get_scores_from_database()
    print(f'Got the max scores: {max_scores}')

    # Initialize the final score
    final_score = 0

    # Add the score for each detail to the final score
    for detail, value in application_form_details.items():
        print(f'Detail: {detail}, Value: {value}')
        if value in max_scores:
            final_score += max_scores[value]

    print(f'Final score: {final_score}')
    # Return the final score
    return final_score

def retrieve_appointments(page_number, page_size, max=0):
    # Define the SQL query for retrieving appointments with associated opportunities and mentors
    
    query = """
    SELECT a.id, o.name, o.email, o.phone, o.name AS opportunity_name, o.id AS opportunity_id, m.name AS mentor_name, m.id AS mentor_id, a.appointment_time AS appointment_time,
    a.career_challenge, a.challenge_description, a.urgency, a.salary_range, a.expected_salary, a.current_employer, a.financial_situation, a.grade, 
    a.verified, a.conflicted, a.canceled, a.confirmed
    FROM appointments AS a
    LEFT JOIN opportunity AS o ON a.opportunity_id = o.id
    LEFT JOIN sales_agent AS m ON a.mentor_id = m.id
    WHERE a.appointment_time > %s and (a.canceled = FALSE OR a.canceled IS NULL)
    """
    count_query = "SELECT COUNT(*) FROM appointments WHERE appointment_time > %s and (canceled = FALSE OR canceled IS NULL)"
    try:
        # Create a new database connection
        cnx = create_connection()

        # Get the current time in GMT
        if max == 1:
            current_time = datetime(2023, 1, 1).date()
            query = query + '''
                ORDER BY a.appointment_time DESC
                LIMIT %s OFFSET %s
            '''
        else:
            current_time = datetime.now(pytz.timezone('GMT')).date()
            query = query + '''
                ORDER BY a.appointment_time ASC
                LIMIT %s OFFSET %s
            '''
        # Create a new cursor
        cursor = cnx.cursor()

        # Calculate the offset based on the page number and page size
        offset = (page_number - 1) * page_size
        print(f'Retrieving appointments for page size {page_size} with page offset {offset}')
        # Execute the SQL query with the page size and offset as parameters
        cursor.execute(query, (current_time, page_size, offset))

        # Fetch all rows
        rows = cursor.fetchall()

        # Create a list to store the appointment details
        appointments = []

        # Iterate over the rows and extract the appointment details
        for row in rows:
            appointment = {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'telephone': row[3],
                'opportunity_name': row[4],
                'opportunity_id': row[5],
                'mentor_name': row[6],
                'mentor_id': row[7],
                'appointment_time': row[8],
                'career_challenge': row[9],
                'challenge_description': row[10],
                'urgency': row[11],
                'salary_range': row[12],
                'expected_salary': row[13],
                'current_employer': row[14],
                'financial_situation': row[15],
                'grade': row[16],
                'verified': row[17],
                'conflicted': row[18],
                'canceled': row[19],
                'confirmed': row[20]
            }
            appointments.append(appointment)

        # Calculate the total number of appointments
        cursor.execute(count_query, (current_time,))
        total_appointments = cursor.fetchone()[0]

        # Calculate the total number of pages
        total_pages = (total_appointments + page_size - 1) // page_size
 
        # Return the result
        return total_pages, total_appointments, appointments
    except Exception as err:
        print(f"Error: {err}")
        return None

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()

def cancel_saved_appointment(appointment_id):
    try:
        # Create a new database connection
        cnx = create_connection()

        # Create a new cursor
        cursor = cnx.cursor()

        # Define the SQL query for updating the appointment with the given ID
        query = "UPDATE appointments SET canceled = TRUE WHERE id = %s"

        # Execute the SQL query with the appointment ID as a parameter
        cursor.execute(query, (appointment_id,))

        # Commit the transaction
        cnx.commit()

        # Return True to indicate success
        return True

    except Exception as err:
        raise err
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()

def confirm_saved_appointment(appointment_id):
    try:
        # Create a new database connection
        cnx = create_connection()
        # Create a new cursor
        cursor = cnx.cursor()
        # Define the SQL query for updating the appointment with the given ID
        query = "UPDATE appointments SET confirmed = TRUE WHERE id = %s"
        # Execute the SQL query with the appointment ID as a parameter
        cursor.execute(query, (appointment_id,))
        # Commit the transaction
        cnx.commit()
        # Return True to indicate success
        return True
    except Exception as err:
        raise err
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()