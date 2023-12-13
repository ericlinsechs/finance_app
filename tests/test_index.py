import unittest
from unittest.mock import patch
from flask import Flask, session
from app import app


class TestIndex(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test_secret_key"
        self.client = app.test_client()

    @patch("app.db.execute_query")
    @patch("app.lookup")
    def test_index_with_transactions(self, mock_lookup, mock_execute_query):
        # Assume that the user is logged in with user_id 1
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Mock the database responses
        mock_execute_query.side_effect = [
            [{"cash": 10000.0}],  # Response for the SELECT cash query
            [
                {"symbol": "AAPL", "price": 150.0, "shares": 1},
                {"symbol": "GOOGL", "price": 2000.0, "shares": 2},
                {"symbol": "AAPL", "price": 300.0, "shares": 1},
            ],  # Response for the SELECT transactions query
        ]

        # Mock the lookup function responses
        mock_lookup.side_effect = [
            {"price": 150.0},  # Response for AAPL lookup
            {"price": 2000.0},  # Response for GOOGL lookup
        ]

        # Make a request to the index route
        response = self.client.get("/")

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AAPL", response.data)
        self.assertIn(b"GOOGL", response.data)
        self.assertIn(b"$450.00", response.data)
        self.assertIn(b"$4000.00", response.data)

    @patch("app.db.execute_query")
    def test_index_no_transactions(self, mock_execute_query):
        # Assume that the user is logged in with user_id 1
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Mock the database responses
        mock_execute_query.side_effect = [
            [{"cash": 1000.0}],  # Response for the SELECT cash query
            [],  # Response for the SELECT transactions query
        ]

        # Make a request to the index route
        response = self.client.get("/")

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"$1000.00", response.data)


if __name__ == "__main__":
    unittest.main()
