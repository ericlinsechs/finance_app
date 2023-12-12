import unittest
import tempfile
import os
from db_module import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = Database(self.db_path)

        # Initialize the database schema (assuming it's the same as finance.db)
        schema = """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                username TEXT NOT NULL,
                hash TEXT NOT NULL,
                cash NUMERIC NOT NULL DEFAULT 10000.00
            );
            CREATE UNIQUE INDEX username ON users (username);
        """
        self.db.cursor.executescript(schema)
        self.db.connection.commit()

    def tearDown(self):
        # Close and remove the temporary database file
        self.db.connection.close()
        os.close(self.db_fd)
        os.remove(self.db_path)

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
