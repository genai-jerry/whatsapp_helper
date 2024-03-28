from datetime import datetime

import pytz
from db.connection_manager import *

def store_appointment(profile_details, application_form_details, mentor_name):
    try:
        # Create a new database connection
        cnx = create_connection()
        # Create a new cursor
        cursor = cnx.cursor()

        grade = grade_application(application_form_details)
        # Set verified to true if grade is 0, else set it to false
        verified = True if grade == 0 else False

        # Look up the opportunity using the name or email in the opportunities table
        query = "SELECT id FROM opportunity WHERE name = %s OR email = %s"
        cursor.execute(query, (profile_details['name'], profile_details['email']))
        opportunity_id = cursor.fetchone()
        if opportunity_id is not None:
            opportunity_id = opportunity_id[0]
        else:
            opportunity_id = None

        # Look up the mentor using the mentor name in the mentors table
        query = "SELECT id FROM sales_agent WHERE name = %s"
        mentor_name = ''.join(c for c in mentor_name if c.isalpha())
        cursor.execute(query, (mentor_name,))
        mentor_id = cursor.fetchone()
        if mentor_id is not None:
            mentor_id = mentor_id[0]
        else:
            mentor_id = None

        # Define the SQL query for inserting a new appointment with opportunity_id and mentor_id as foreign keys
        query = """
        INSERT INTO appointments (name, email, telephone, career_challenge, challenge_description, urgency, salary_range, 
        expected_salary, current_employer, financial_situation, grade, mentor_id, opportunity_id, appointment_time, verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        date_str = application_form_details['appointment_time']
        appointment_time = datetime.strptime(date_str, '%A, %d %B %Y %I:%M %p') if date_str else None
        # Convert appointment_time from IST to GMT
        if appointment_time:
            appointment_time = appointment_time.astimezone(pytz.timezone('GMT'))
        # Define the values for the SQL query
        values = (
            profile_details['name'],
            profile_details['email'],
            profile_details['telephone'],
            application_form_details['career_challenge'],
            application_form_details['challenge_description'],
            application_form_details['urgency'],
            application_form_details['salary_range'],
            application_form_details['expected_salary'],
            application_form_details['current_employer'],
            application_form_details['financial_situation'],
            grade,
            mentor_id,
            opportunity_id,
            appointment_time,
            verified
        )

        # Execute the SQL query
        cursor.execute(query, values)

        # Commit the transaction
        cnx.commit()

        # Get the ID of the newly inserted appointment
        appointment_id = cursor.lastrowid

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

def retrieve_appointments(page_number, page_size):
    # Define the SQL query for retrieving appointments with associated opportunities and mentors
    query = """
    SELECT a.id, a.name, a.email, a.telephone, o.name AS opportunity_name, o.id AS opportunity_id, m.name AS mentor_name, m.id AS mentor_id, a.appointment_time AS appointment_time,
    a.career_challenge, a.challenge_description, a.urgency, a.salary_range, a.expected_salary, a.current_employer, a.financial_situation, a.grade, a.verified
    FROM appointments AS a
    LEFT JOIN opportunity AS o ON a.opportunity_id = o.id
    LEFT JOIN sales_agent AS m ON a.mentor_id = m.id
    WHERE a.appointment_time > NOW()
    ORDER BY a.appointment_time ASC
    LIMIT %s OFFSET %s
    """
    count_query = "SELECT COUNT(*) FROM appointments"
    try:
        # Create a new database connection
        cnx = create_connection()

        # Create a new cursor
        cursor = cnx.cursor()

        # Calculate the offset based on the page number and page size
        offset = (page_number - 1) * page_size
        print(f'Retrieving appointments for page size {page_size} with page offset {offset}')
        # Execute the SQL query with the page size and offset as parameters
        cursor.execute(query, (page_size, offset))

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
                'verified': row[17]
            }
            appointments.append(appointment)

        # Calculate the total number of appointments
        cursor.execute(count_query)
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