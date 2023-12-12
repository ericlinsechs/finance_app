import unittest
from app import app

from flask import session
from unittest.mock import patch


class TestRegister(unittest.TestCase):
    def setUp(self):
        # Set up a test client
        self.client = app.test_client()

    @patch("app.db.execute_query")
    def test_register_missing_username(self, mock_execute_query):
        # Send a POST request to the /register route with missing username
        response = self.client.post(
            "/register", data={"password": "password", "confirmation": "password"}
        )

        self.assertEqual(response.status_code, 400)

    @patch("app.db.execute_query")
    def test_register_missing_password(self, mock_execute_query):
        # Send a POST request to the /register route with missing password
        response = self.client.post(
            "/register", data={"username": "new_user", "confirmation": "password"}
        )

        self.assertEqual(response.status_code, 400)

        # Check if the user is not logged in after a failed registration
        with app.test_request_context():
            self.assertFalse("user_id" in session)

    @patch("app.db.execute_query")
    def test_register_missing_confirmation(self, mock_execute_query):
        # Send a POST request to the /register route with missing confirmation
        response = self.client.post(
            "/register", data={"username": "new_user", "password": "password"}
        )

        self.assertEqual(response.status_code, 400)

    @patch("app.db.execute_query")
    def test_register_existing_username(self, mock_execute_query):
        # Mock database execute to return a non-empty list (indicating username already exists)
        mock_execute_query.return_value = [
            {"id": 1, "username": "existing_user", "hash": "hashed_password"}
        ]

        # Send a POST request to the /register route with an existing username
        response = self.client.post(
            "/register",
            data={
                "username": "existing_user",
                "password": "password",
                "confirmation": "password",
            },
        )

        self.assertEqual(response.status_code, 400)

    @patch("app.db.execute_query")
    def test_register_passwords_do_not_match(self, mock_execute_query):
        # Send a POST request to the /register route with mismatched passwords
        response = self.client.post(
            "/register",
            data={
                "username": "new_user",
                "password": "password",
                "confirmation": "different_password",
            },
        )

        self.assertEqual(response.status_code, 400)

    @patch("app.db.execute_query")
    def test_register_successful(self, mock_execute_query):
        # Define different return values for different calls
        mock_execute_query.side_effect = [
            [],
            [],
            [{"id": 1}],
        ]

        # Send a POST request to the /register route with valid data
        response = self.client.post(
            "/register",
            data={
                "username": "new_user",
                "password": "password",
                "confirmation": "password",
            },
        )

        # Check if the response redirects to the home page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Location"], "/")


if __name__ == "__main__":
    unittest.main()
