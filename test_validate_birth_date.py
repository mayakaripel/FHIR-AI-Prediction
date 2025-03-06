import unittest
from datetime import datetime

# Assuming the validate_birth_date function is in a module named fhir_module
from fhir_query import validate_birth_date

class TestValidateBirthDate(unittest.TestCase):
    def test_valid_date(self):
        self.assertEqual(validate_birth_date('2000-01-01'), '2000-01-01')

    def test_invalid_date_format(self):
        self.assertIsNone(validate_birth_date('01-01-2000'))

    def test_none_date(self):
        self.assertIsNone(validate_birth_date(None))

    def test_empty_string_date(self):
        self.assertIsNone(validate_birth_date(''))

    def test_invalid_date_value(self):
        self.assertIsNone(validate_birth_date('2000-02-30'))

if __name__ == '__main__':
    unittest.main()