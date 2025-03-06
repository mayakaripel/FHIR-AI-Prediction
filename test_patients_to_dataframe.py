import unittest
import pandas as pd
from  fhir_query import patients_to_dataframe, validate_birth_date

class TestPatientsToDataFrame(unittest.TestCase):
    def test_patients_to_dataframe(self):
        patients = [
            {
                "id": "1",
                "birthDate": "2000-01-01",
                "gender": "male",
                "name": [{"given": ["John"], "family": "Doe"}]
            },
            {
                "id": "2",
                "birthDate": "1990-05-15",
                "gender": "female",
                "name": [{"given": ["Jane"], "family": "Smith"}]
            },
            {
                "id": "3",
                "birthDate": "invalid-date",
                "gender": "unknown",
                "name": [{"given": ["Unknown"], "family": "Unknown"}]
            }
        ]

        df = patients_to_dataframe(patients)

        expected_data = {
            'id': ['1', '2', '3'],
            'gender': ['male', 'female', 'unknown'],
            'birthDate': ['2000-01-01', '1990-05-15', None],
            'given_name': ['John', 'Jane', 'Unknown'],
            'family_name': ['Doe', 'Smith', 'Unknown']
        }
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(df, expected_df)

if __name__ == '__main__':
    unittest.main()