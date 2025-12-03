import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        # Handle empty password correctly
        password = os.getenv('DB_PASSWORD', '')
        self.password = password if password else ''  # Use empty string if None
        self.database = os.getenv('DB_NAME', 'classroom_reservation_db')
        self.port = os.getenv('DB_PORT', '3306')
        self.connection = None
    
    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            if self.connection.is_connected():
                return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE queries"""
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()
    
    def fetch_one(self, query, params=None):
        """Fetch single record"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching data: {e}")
            return None
        finally:
            cursor.close()
    
    def fetch_all(self, query, params=None):
        """Fetch multiple records"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
        finally:
            cursor.close()

# Singleton instance
db = Database()