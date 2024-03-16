import unittest
from unittest.mock import MagicMock, patch

from message_store import get_all_messages

class TestGetAllMessages(unittest.TestCase):
    @patch('message_store.create_connection')
    def test_get_all_messages(self, mock_create_connection):
        # Mocking the database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Mocking the database query results
        mock_cursor.fetchone.return_value = (10,)  # Total items
        mock_cursor.fetchall.return_value = [
            (1, 'John', 'Hello', 'Sent', '2022-01-01 10:00:00', 1),
            (2, 'Alice', 'Hi', 'Received', '2022-01-02 12:00:00', 2),
            (3, 'Bob', 'Hey', 'Sent', '2022-01-03 15:00:00', 3)
        ]

        # Calling the function under test
        messages, total_pages, total_items = get_all_messages(1, 10)

        # Assertions
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]['id'], 1)
        self.assertEqual(messages[0]['receiver'], 'John')
        self.assertEqual(messages[0]['template'], 'Hello')
        self.assertEqual(messages[0]['status'], 'Sent')
        self.assertEqual(messages[0]['create_time'], '2022-01-01 10:00:00')
        self.assertEqual(messages[0]['receiver_id'], 1)

        self.assertEqual(total_pages, 1)
        self.assertEqual(total_items, 10)

        # Verify database queries
        mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM messages")
        mock_cursor.execute.assert_called_with("""
            SELECT 
                m.id, 
                m.receiver, 
                m.template, 
                m.status, 
                m.create_time,
                m.receiver_id
            FROM 
                messages m
            ORDER BY m.create_time desc
            LIMIT %s OFFSET %s
        """, (10, 0))

    def test_get_all_messages_empty(self):
        # Mocking the database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        with patch('message_store.create_connection', return_value=mock_connection):
            mock_connection.cursor.return_value = mock_cursor

            # Mocking the database query results
            mock_cursor.fetchone.return_value = (0,)  # Total items
            mock_cursor.fetchall.return_value = []

            # Calling the function under test
            messages, total_pages, total_items = get_all_messages(1, 10)

            # Assertions
            self.assertEqual(len(messages), 0)
            self.assertEqual(total_pages, 0)
            self.assertEqual(total_items, 0)

            # Verify database queries
            mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM messages")
            mock_cursor.execute.assert_not_called()

if __name__ == '__main__':
    unittest.main()