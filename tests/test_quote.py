import unittest
from app import app
from flask import session
from unittest.mock import patch


class TestQuote(unittest.TestCase):
    def setUp(self):
        # Set up a test client
        self.client = app.test_client()

    @patch("app.lookup")
    def test_quote(self, mock_lookup):
        # Mock the lookup function to simulate a valid quote
        mock_lookup.return_value = {"name": "AAPL", "price": 150.0, "symbol": "AAPL"}

        # Authenticate the user by adding user_id to the session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Send a POST request to the /quote route with valid data
        response = self.client.post(
            "/quote",
            data={"symbol": "AAPL"},
        )

        # Check if the response renders the quoted.html template
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AAPL", response.data)
        self.assertIn(b"$150.00", response.data)


if __name__ == "__main__":
    unittest.main()
