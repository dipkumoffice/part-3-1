import unittest
from unittest.mock import patch
from scripts.health_check import check_service


class TestHealthCheckUnit(unittest.TestCase):

    @patch("scripts.health_check.requests.get")
    def test_check_service_success(self, mock_get):
        mock_get.return_value.status_code = 200
        result = check_service("TestService", "http://example.com")
        self.assertIn("OK", result)

    @patch("scripts.health_check.requests.get")
    def test_check_service_failure_status(self, mock_get):
        mock_get.return_value.status_code = 500
        result = check_service("TestService", "http://example.com")
        self.assertIn("FAIL", result)

    @patch("scripts.health_check.requests.get", side_effect=Exception("Connection error"))
    def test_check_service_exception(self, mock_get):
        result = check_service("TestService", "http://example.com")
        self.assertIn("ERROR", result)


if __name__ == '__main__':
    unittest.main()
