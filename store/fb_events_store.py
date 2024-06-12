from db.connection_manager import *

def check_events_fired(opportunity_id):
    # Get the opportunity from the database
    connection = create_connection()
    cursor = connection.cursor()

    # Fetch opportunity from the database
    cursor.execute(
        """
        SELECT 
            opportunity.id,
            opportunity.lead_event_fired as lead_even_fired,
            opportunity.submit_application_event_fired as submit_application_event_fired,
            opportunity.sale_event_fired as sale_event_fired
        FROM 
            opportunity
        WHERE 
            opportunity.id = %s;
        """, (opportunity_id,)
    )
    row = cursor.fetchone()

    opportunity = {
            'id': row[0],
            'lead_event_fired': row[1],
            'submit_application_event_fired': row[2],
            'sale_event_fired': row[3],
        }

    return {'lead_event_fired': opportunity['lead_event_fired'], 
            'submit_application_event_fired': opportunity['submit_application_event_fired'],
            'sale_event_fired': opportunity['sale_event_fired']}

def update_event_fired(opportunity_id, event_type):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Prepare the SQL query with placeholders
        if event_type == 'lead_event_fired':
            sql = "UPDATE opportunity SET lead_event_fired = 1 WHERE id = %s"
        elif event_type == 'submit_application_event_fired':
            sql = "UPDATE opportunity SET submit_application_event_fired = 1 WHERE id = %s"
        elif event_type == 'sale_event_fired':
            sql = "UPDATE opportunity SET sale_event_fired = 1 WHERE id = %s"
        else:
            raise ValueError("Invalid event type")

        # Prepare the query and execute it with the provided values
        cursor.execute(sql, (opportunity_id,))

        connection.commit()
    finally:
        if cursor:
            cursor.close()