import unittest
from unittest.mock import patch
from flask import jsonify

from routers.appointment import create_new_appointment

class TestCreateNewAppointment(unittest.TestCase):
    @patch('routers.appointment.store_appointment')
    def test_create_new_appointment_valid_details(self, mock_store_appointment):
        # Mock request.json data
        request_data = {
            'name': 'Test Gen',
            'email': 'test.com20@test.com',
            'phone': '+911234512346',
            'mentor_name': 'Jane Smith',
            'career_challenge': 'Challenge 1',
            'challenge_description': 'Description 1',
            'urgency': 'High',
            'salary_range': '10000-20000',
            'expected_salary': '15000',
            'current_employer': 'ABC Company',
            'financial_situation': 'Stable',
            'availability': 'Weekdays',
            'whatsapp_number': '9876543210'
        }

        # Call the function
        response = create_new_appointment(request_data)

        # Assert the response
        expected_response = jsonify({'status': 'success'}), 200
        self.assertEqual(response, expected_response)
        mock_store_appointment.assert_called_once_with({
            'name': 'John Doe',
            'email': 'johndoe@example.com',
            'phone': '1234567890'
        }, {
            'career_challenge': 'Challenge 1',
            'challenge_description': 'Description 1',
            'urgency': 'High',
            'salary_range': '10000-20000',
            'expected_salary': '15000',
            'current_employer': 'ABC Company',
            'financial_situation': 'Stable',
            'availability': 'Weekdays',
            'whatsapp_number': '9876543210'
        }, 'Jane Smith')

    @patch('routers.appointment.store_appointment')
    def test_create_new_appointment_missing_details(self, mock_store_appointment):
        # Mock request.json data with missing details
        request_data = {
            'name': 'Test Gen',
            'email': 'test.com20@test.com',
            'phone': '+911234512346',
            'mentor_name': 'Jane Smith',
            'career_challenge': 'Challenge 1',
            'challenge_description': 'Description 1',
            'urgency': 'High',
            'salary_range': '10000-20000',
            'expected_salary': '15000',
            'current_employer': 'ABC Company',
            'financial_situation': 'Stable',
            'availability': 'Weekdays'
            # Missing whatsapp_number
        }

        # Call the function
        response = create_new_appointment(request_data)

        # Assert the response
        expected_response = jsonify({'status': 'error', 'message': 'Some required details are missing'}), 400
        self.assertEqual(response, expected_response)
        mock_store_appointment.assert_not_called()

    @patch('routers.appointment.store_appointment')
    def test_create_new_appointment_invalid_details(self, mock_store_appointment):
        # Mock request.json data with invalid details
        request_data = {
            'name': 'Test Gen',
            'email': 'test.com20@test.com',
            'phone': '+911234512346',
            'mentor_name': 'Jane Smith',
            'career_challenge': 'Challenge 1',
            'challenge_description': 'Description 1',
            'urgency': 'High',
            'salary_range': '10000-20000',
            'expected_salary': '15000',
            'current_employer': 'ABC Company',
            'financial_situation': 'Stable',
            'availability': 'Weekdays',
            'whatsapp_number': '9876543210'
        }

        # Mock an exception to simulate invalid details
        mock_store_appointment.side_effect = Exception('Invalid details')

        # Call the function
        response = create_new_appointment(request_data)

        # Assert the response
        expected_response = jsonify({'status': 'error', 'message': 'Invalid details'}), 400
        self.assertEqual(response, expected_response)
        mock_store_appointment.assert_called_once_with({
            'name': 'John Doe',
            'email': 'johndoe@example.com',
            'phone': '1234567890'
        }, {
            'career_challenge': 'Challenge 1',
            'challenge_description': 'Description 1',
            'urgency': 'High',
            'salary_range': '10000-20000',
            'expected_salary': '15000',
            'current_employer': 'ABC Company',
            'financial_situation': 'Stable',
            'availability': 'Weekdays',
            'whatsapp_number': '9876543210'
        }, 'Jane Smith')

        

if __name__ == '__main__':
    unittest.main()