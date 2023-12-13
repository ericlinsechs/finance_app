import sqlite3


class Database:
    def __init__(self, db_path, check_same_thread=False):
        self.connection = sqlite3.connect(db_path, check_same_thread=check_same_thread)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def execute_query(self, query, *args):
        self.cursor.execute(query, args)
        self.connection.commit()  # Commit changes to the database
        columns = (
            [column[0] for column in self.cursor.description]
            if self.cursor.description
            else []
        )
        result = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        return result

    def create_tables(self):
        # Create 'users' table if not exists
        create_users_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                username TEXT NOT NULL,
                hash TEXT NOT NULL,
                cash NUMERIC NOT NULL DEFAULT 10000.00
            );
        """
        self.execute_query(create_users_table_query)

        # Create unique index for 'users' table if not exists
        create_users_index_query = """
            CREATE UNIQUE INDEX IF NOT EXISTS username ON users (username);
        """
        self.execute_query(create_users_index_query)

        # Create 'transactions' table if not exists
        create_transactions_table_query = """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY NOT NULL,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                price NUMERIC NOT NULL,
                shares NUMERIC NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """
        self.execute_query(create_transactions_table_query)
