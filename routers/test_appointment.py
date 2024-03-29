import unittest
from unittest.mock import patch, Mock
from flask import jsonify, Flask
from routers.appointment import create_new_appointment
app = Flask(__name__)

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

        with app.test_request_context(json=request_data):
            # Call the function
            response = create_new_appointment(request_data)

            # Assert the response
            expected_response = jsonify({'status': 'success'}), 200
            self.assertEqual(response, expected_response)
            mock_store_appointment.assert_called_once_with({
                'name': 'Test Gen',
                'email': 'test.com20@test.com',
                'telephone': '+911234512346'
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

        with app.test_request_context(json=request_data):
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

        with app.test_request_context(json=request_data):
            # Mock an exception to simulate invalid details
            mock_store_appointment.side_effect = Exception('Invalid details')

            # Call the function
            response = create_new_appointment(request_data)
            # Assert the response
            expected_response = jsonify({'status': 'error', 'message': 'Invalid details'}), 403
            self.assertEqual(response, expected_response)
            mock_store_appointment.assert_called_once_with({
                'name': 'Test Gen',
                'email': 'test.com20@test.com',
                'telephone': '+911234512346'
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
def test_opportunity_lookup_and_match(self, mock_store_appointment):
    # Mock request.json data
    request_data = {
        'name': 'Test Gen',
        'email': 'test.com20@test.com',  # This email exists in the database
        'telephone': '+911234512346',
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

    with app.test_request_context(json=request_data):
        # Mock store_appointment to return an appointment with an opportunity_id
        mock_store_appointment.return_value = Mock(opportunity_id=123)

        # Call the function
        response = create_new_appointment(request_data)

        # Assert that the response has a status code of 200 and an opportunity_id
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['opportunity_id'], 123)

@patch('routers.appointment.store_appointment')
def test_no_opportunity_match(self, mock_store_appointment):
    # Mock request.json data
    request_data = {
        'name': 'Test Gen',
        'email': 'nonexistent@test.com',  # This email does not exist in the database
        'telephone': '+911234512346',
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

    with app.test_request_context(json=request_data):
        # Mock store_appointment to return an appointment without an opportunity_id
        mock_store_appointment.return_value = Mock(opportunity_id=None)

        # Call the function
        response = create_new_appointment(request_data)

        # Assert that the response has a status code of 200 and no opportunity_id
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json.get('opportunity_id'))

if __name__ == '__main__':
    unittest.main()