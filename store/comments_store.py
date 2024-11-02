from db.connection_manager import *

def get_comments_for_opportunity(opportunity_id, page=1, per_page=10):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = '''SELECT c.id, c.content, c.created_at, u.name as creator_name
                 FROM comments c
                 JOIN users u ON c.user_id = u.id
                 WHERE c.opportunity_id = %s
                 ORDER BY c.created_at ASC
                 LIMIT %s OFFSET %s'''
        cursor.execute(sql, (opportunity_id, per_page, (page-1)*per_page))
        comments = cursor.fetchall()
        comments_list = []
        for comment in comments:
            comments_list.append({
                "id": comment[0],
                "content": comment[1],
                "created_at": comment[2],
                "creator_name": comment[3]
            })
        comments_count = '''SELECT COUNT(*) FROM comments WHERE opportunity_id = %s'''
        cursor.execute(comments_count, (opportunity_id,))
        total_comments = cursor.fetchone()[0]
        return comments_list, total_comments
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []
    finally:
        connection.close()

def create_comment(opportunity_id, content, creator_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        sql = '''INSERT INTO comments (content, opportunity_id, user_id)
                 VALUES (%s, %s, %s)'''
        cursor.execute(sql, (content, opportunity_id, creator_id))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error creating comment: {e}")
        return False
    finally:
        connection.close()
