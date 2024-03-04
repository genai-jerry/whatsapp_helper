import unittest

from utils import format_phone_number, is_valid_phone_number

class TestFormatPhoneNumber(unittest.TestCase):
    def test_format_phone_number(self):
        self.assertEqual(format_phone_number('9900167226'), '+919900167226')
        self.assertEqual(format_phone_number('919900167226'), '+919900167226')
        self.assertEqual(format_phone_number('+919900167226'), '+919900167226')

class TestIsValidPhoneNumber(unittest.TestCase):
    def test_is_valid_phone_number(self):
        self.assertTrue(is_valid_phone_number('+919900167226'))
        self.assertTrue(is_valid_phone_number('+11234567890'))
        self.assertFalse(is_valid_phone_number('1234567890'))
        self.assertFalse(is_valid_phone_number('abc123'))

if __name__ == '__main__':
    unittest.main()