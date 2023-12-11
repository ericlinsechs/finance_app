import sqlite3

class Database:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def execute_query(self, query, *args):
        return self.cursor.execute(query, args).fetchall()
