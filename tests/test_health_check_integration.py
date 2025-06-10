import unittest
from scripts.health_check import check_service


class TestHealthCheckIntegration(unittest.TestCase):

    def test_example_health_check(self):
        result = check_service("HTTPBin", "https://httpbin.org/status/200")
        self.assertIn("OK", result)


if __name__ == '__main__':
    unittest.main()
