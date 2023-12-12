import unittest
from unittest.mock import patch
from flask import Flask, session
from app import app


class TestBuy(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test_secret_key"
        self.client = app.test_client()

    @patch("app.lookup")
    @patch("app.db.execute_query")
    # @patch("app.db.cursor")
    def test_buy_successful(self, mock_execute_query, mock_lookup):
        # Mocking lookup function
        mock_lookup.return_value = {"name": "AAPL", "price": 150.0, "symbol": "AAPL"}

        # Mocking execute_query for user cash
        mock_execute_query.side_effect = [
            [{"cash": 10000.0}],  # Initial cash for the user
            [],
            [],
        ]

        # Authenticate the user by adding user_id to the session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Send a POST request to the /buy route with valid data
        response = self.client.post(
            "/buy",
            data={"symbol": "AAPL", "shares": "2"},
        )

        # Check if the response redirects to the home page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Location"], "/")

    @patch("app.lookup")
    @patch("app.db.execute_query")
    def test_buy_insufficient_funds(self, mock_execute_query, mock_lookup):
        # Mocking lookup function
        mock_lookup.return_value = {"name": "AAPL", "price": 150.0, "symbol": "AAPL"}

        # Mocking execute_query for user cash (insufficient funds)
        mock_execute_query.side_effect = [
            [{"cash": 100.0}],  # Insufficient funds for the user
        ]

        # Authenticate the user by adding user_id to the session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Send a POST request to the /buy route with insufficient funds
        response = self.client.post(
            "/buy",
            data={"symbol": "AAPL", "shares": "2"},
        )

        self.assertEqual(response.status_code, 400)

    @patch("app.lookup")
    def test_buy_invalid_symbol(self, mock_lookup):
        # Mocking lookup function for an invalid symbol
        mock_lookup.return_value = None

        # Authenticate the user by adding user_id to the session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        # Send a POST request to the /buy route with an invalid symbol
        response = self.client.post(
            "/buy",
            data={"symbol": "INVALID", "shares": "2"},
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
