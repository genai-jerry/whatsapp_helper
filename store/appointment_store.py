from db.connection_manager import *

def store_appointment(profile_details, application_form_details, mentor_name):
    try:
        grade = grade_application(application_form_details)

        # Create a new database connection
        cnx = create_connection()
        # Create a new cursor
        cursor = cnx.cursor()
        # Look up the opportunity using the name or email in the opportunities table
        query = "SELECT id FROM opportunities WHERE name = %s OR email = %s"
        cursor.execute(query, (profile_details['name'], profile_details['email']))
        opportunity_id = cursor.fetchone()
        if opportunity_id is not None:
            opportunity_id = opportunity_id[0]
        else:
            opportunity_id = None

        # Look up the mentor using the mentor name in the mentors table
        query = "SELECT id FROM sales_agent WHERE name = %s"
        cursor.execute(query, (mentor_name,))
        mentor_id = cursor.fetchone()
        if mentor_id is not None:
            mentor_id = mentor_id[0]
        else:
            mentor_id = None

        # Define the SQL query for inserting a new appointment with opportunity_id and mentor_id as foreign keys
        query = """
        INSERT INTO appointments (name, email, telephone, career_challenge, challenge_description, urgency, salary_range, expected_salary, current_employer, financial_situation, grade, mentor_id, opportunity_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

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
            opportunity_id
        )

        # Execute the SQL query
        cursor.execute(query, values)

        # Commit the transaction
        cnx.commit()

        # Get the ID of the newly inserted appointment
        appointment_id = cursor.lastrowid

        # Return the appointment ID
        return appointment_id

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

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
        max_scores = {row[0]: row[1] for row in rows}

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

    # Calculate the max possible score
    # Get the max possible score from the config store
    max_possible_score = retrieve_config('max_possible_score')

    # Calculate the score percentage
    score_percentage = total_score / max_possible_score

    # Determine the grade based on the score percentage
    if score_percentage >= 0.8:
        grade = 3
    elif score_percentage >= 0.5:
        grade = 2
    else:
        grade = 1

    # Return the grade
    return grade

def calculate_final_score(application_form_details):
    # Get the max scores from the database
    max_scores = get_scores_from_database()

    # Initialize the final score
    final_score = 0

    # Add the score for each detail to the final score
    for detail, value in application_form_details.items():
        if detail in max_scores and value in max_scores[detail]:
            final_score += max_scores[detail][value]

    # Return the final score
    return final_score