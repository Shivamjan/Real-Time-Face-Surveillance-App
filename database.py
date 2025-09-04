import pymysql
import os
from dotenv import load_dotenv

class DatabaseService:
    """
    Handles all interactions with the MySQL database.
    Manages connections and executes queries.
    """
    def __init__(self):
        load_dotenv()
        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "criminal_detection")
        }
        self.init_database()

    def get_connection(self):
        """Establishes and returns a database connection."""
        try:
            return pymysql.connect(**self.db_config, cursorclass=pymysql.cursors.DictCursor)
        except pymysql.Error as e:
            print(f"Error connecting to MySQL Database: {e}")
            raise

    def init_database(self):
        """Creates the necessary tables if they don't already exist."""
        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS criminals (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        father_name VARCHAR(255),
                        gender VARCHAR(50),
                        dob VARCHAR(50),
                        crimes_done TEXT,
                        embedding LONGBLOB,
                        question VARCHAR(255),
                        answer VARCHAR(255)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        password VARCHAR(255) NOT NULL,
                        security_question VARCHAR(255),
                        security_answer VARCHAR(255)
                    )
                """)
            connection.commit()
            connection.close()
            print("Database initialized successfully.")
        except pymysql.Error as e:
            print(f"Error during database initialization: {e}")
            raise
