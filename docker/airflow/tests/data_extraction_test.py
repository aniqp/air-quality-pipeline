import unittest
from air_quality_functions import *
from dags.mysql_dag import *

class TestDataExtraction(unittest.TestCase):

    def test_extract_data_from_api_success(self):
        # Simulate a successful API request and test the result
        result = get_data()
        
        # Add assertions based on the expected behavior
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_extract_data_from_api_failure(self):
        # Simulate a failed API request and test the result
        result = get_data()
        
        # Add assertions based on the expected behavior in case of failure
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()