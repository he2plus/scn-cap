import sqlite3

class MetadataManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS captures (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            file_path TEXT NOT NULL,
                            capture_type TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )''')
        self.conn.commit()

    def add_metadata(self, file_path, capture_type):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO captures (file_path, capture_type) VALUES (?, ?)", (file_path, capture_type))
            self.conn.commit()
            print(f"Metadata added for file: {file_path}")
        except Exception as e:
            print(f"Error adding metadata: {e}")

    def get_metadata(self, file_path):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM captures WHERE file_path = ?", (file_path,))
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Error retrieving metadata: {e}")
            return None

    def close(self):
        try:
            self.conn.close()
            print("Database connection closed.")
        except Exception as e:
            print(f"Error closing database connection: {e}")
