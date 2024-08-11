import unittest
from app import create_app

class RoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_checkout(self):
        response = self.client.post('/checkout')
        self.assertEqual(response.status_code, 200)

    def test_get_customer_info(self):
        response = self.client.get('/customer?apiKey=testKey')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
