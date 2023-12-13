import unittest
from unittest.mock import patch
from flask import Flask, session
from app import app


class TestHistory(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test_secret_key"
        self.client = app.test_client()

    @patch("app.db.execute_query")
    def test_history(self, mock_execute_query):
        # Assume that the user is logged in with user_id 1
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Mock the database responses
        mock_execute_query.return_value = [
            {
                "symbol": "AAPL",
                "price": 150.0,
                "shares": 1,
                "timestamp": "2023-01-01 12:00:00",
            },
            {
                "symbol": "GOOGL",
                "price": 2000.0,
                "shares": -2,
                "timestamp": "2023-01-02 10:30:00",
            },
        ]

        # Make a request to the history route
        response = self.client.get("/history")

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AAPL", response.data)
        self.assertIn(b"GOOGL", response.data)
        self.assertIn(b"2023-01-01 12:00:00", response.data)
        self.assertIn(b"2023-01-02 10:30:00", response.data)


if __name__ == "__main__":
    unittest.main()
