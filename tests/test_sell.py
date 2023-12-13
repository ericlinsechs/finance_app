import unittest
from unittest.mock import patch
from flask import Flask, session
from app import app


class TestSell(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test_secret_key"
        self.client = app.test_client()

    @patch("app.db.execute_query")
    @patch("app.lookup")
    def test_sell_successful(self, mock_lookup, mock_execute_query):
        # Assume that the user is logged in with user_id 1
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Mock the database responses
        mock_execute_query.side_effect = [
            [{"shares": 2}, {"shares": 3}],  # Response for the SELECT shares query
            [],  # Update user's cash
            [],  # Update transaction record
        ]

        # Mock the lookup function response
        mock_lookup.return_value = {"price": 100.0}  # Response for the lookup function

        # Make a request to the sell route
        response = self.client.post("/sell", data={"symbol": "AAPL", "shares": 2})

        # Check the response
        self.assertEqual(response.status_code, 302)  # Expecting a redirect

    @patch("app.db.execute_query")
    @patch("app.lookup")
    def test_sell_insufficient_shares(self, mock_lookup, mock_execute_query):
        # Assume that the user is logged in with user_id 1
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Mock the database responses
        mock_execute_query.side_effect = [
            [{"shares": 1}],  # Response for the SELECT shares query
        ]

        # Mock the lookup function response
        mock_lookup.return_value = {"price": 100.0}  # Response for the lookup function

        # Make a request to the sell route with insufficient shares
        response = self.client.post("/sell", data={"symbol": "AAPL", "shares": 2})

        # Check the response
        self.assertEqual(response.status_code, 400)  # Expecting a bad request response

    @patch("app.db.execute_query")
    def test_sell_get_request(self, mock_execute_query):
        # Assume that the user is logged in with user_id 1
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Mock the database response
        mock_execute_query.return_value = [
            {"symbol": "AAPL"},
            {"symbol": "GOOGL"},
        ]  # Response for the SELECT symbol query

        # Make a request to the sell route with a GET request
        response = self.client.get("/sell")

        # Check the response
        self.assertEqual(response.status_code, 200)  # Expecting a successful response
        self.assertIn(b"AAPL", response.data)
        self.assertIn(b"GOOGL", response.data)


if __name__ == "__main__":
    unittest.main()
