import sqlite3


class Database:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def execute_query(self, query, *args):
        self.cursor.execute(query, args)
        columns = (
            [column[0] for column in self.cursor.description]
            if self.cursor.description
            else []
        )
        result = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        self.connection.commit()  # Commit changes to the database
        return result
