import unittest
import tempfile
import os
from db_module import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = Database(self.db_path)

    def tearDown(self):
        # Close and remove the temporary database file
        self.db.connection.close()
        os.remove(self.db_path)

    def test_create_tables(self):
        # Call the create_tables method
        self.db.create_tables()

        # Check if the 'users' table exists
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='users';"
        result_users = self.db.execute_query(query)

        # Check if the 'transactions' table exists
        query = (
            "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';"
        )
        result_transactions = self.db.execute_query(query)

        # Check if the 'users' table has the correct columns
        query = "PRAGMA table_info(users);"
        columns_users = self.db.execute_query(query)

        # Check if the 'transactions' table has the correct columns
        query = "PRAGMA table_info(transactions);"
        columns_transactions = self.db.execute_query(query)

        # Assertions
        self.assertTrue(result_users)
        self.assertTrue(result_transactions)
        self.assertEqual(len(columns_users), 4)  # id, username, hash, cash
        self.assertEqual(
            len(columns_transactions), 6
        )  # id, user_id, symbol, price, shares

    def test_execute_query(self):
        # Test a simple query
        query = "INSERT INTO users (username, hash, cash) VALUES (?, ?, ?)"
        args = ("test_user", "hashed_password", 5000.0)
        self.db.execute_query(query, *args)

        # Retrieve the inserted data for verification
        query = "SELECT * FROM users WHERE username = ?"
        args = "test_user"
        result = self.db.execute_query(query, args)

        # Check if the data was inserted correctly
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["username"], "test_user")
        self.assertEqual(result[0]["hash"], "hashed_password")
        self.assertEqual(result[0]["cash"], 5000.0)


if __name__ == "__main__":
    unittest.main()
