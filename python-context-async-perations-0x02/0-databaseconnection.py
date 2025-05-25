#!/usr/bin/python3
"""
Module that contains a custom context manager for database connections
"""
import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    """
    A custom context manager for handling database connections
    
    This class implements the __enter__ and __exit__ methods to handle
    opening and closing database connections automatically when used
    with the 'with' statement.
    """
    
    def __init__(self, host='localhost', user='root', password='root', database='ALX_prodev'):
        """
        Initialize the database connection parameters
        
        Args:
            host (str): The database host
            user (str): The database user
            password (str): The database password
            database (str): The database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """
        Enter the context manager - open the database connection
        
        Returns:
            cursor: The database cursor object for executing queries
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            if self.connection.is_connected():
                print(f"Connected to {self.database} database")
                self.cursor = self.connection.cursor(dictionary=True)
                return self.cursor
            
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager - close the connection
        
        Args:
            exc_type: The exception type if an exception was raised
            exc_val: The exception value if an exception was raised
            exc_tb: The traceback if an exception was raised
        """
        if self.cursor:
            self.cursor.close()
            print("Cursor closed")
            
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print(f"Connection to {self.database} closed")
        
        if exc_type:
            print(f"An exception occurred: {exc_val}")
            # Return False to propagate the exception
            return False


if __name__ == "__main__":
    # Example usage of the context manager
    try:
        with DatabaseConnection() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            
            if not results:
                print("No users found")
            else:
                print(f"Found {len(results)} users:")
                for user in results:
                    print(user)
                    
    except Error as e:
        print(f"Database operation failed: {e}")
