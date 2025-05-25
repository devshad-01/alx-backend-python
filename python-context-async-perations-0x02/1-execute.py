#!/usr/bin/python3
"""
Module that contains a reusable context manager for executing database queries
"""
import mysql.connector
from mysql.connector import Error


class ExecuteQuery:
    """
    A reusable context manager for executing database queries
    
    This class implements the __enter__ and __exit__ methods to handle
    database connection, query execution, and resource cleanup automatically
    when used with the 'with' statement.
    """
    
    def __init__(self, query, params=None, host='localhost', user='root', 
                password='root', database='ALX_prodev'):
        """
        Initialize the context manager with query and connection parameters
        
        Args:
            query (str): The SQL query to execute
            params (tuple, list, dict): The parameters for the query
            host (str): The database host
            user (str): The database user
            password (str): The database password
            database (str): The database name
        """
        self.query = query
        self.params = params
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager - open connection and execute the query
        
        Returns:
            self: The instance with query results
        """
        try:
            # Establish database connection
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            if self.connection.is_connected():
                print(f"Connected to {self.database} database")
                
                # Create cursor and execute query with parameters if provided
                self.cursor = self.connection.cursor(dictionary=True)
                
                if self.params is not None:
                    self.cursor.execute(self.query, self.params)
                else:
                    self.cursor.execute(self.query)
                
                # Store the results
                self.results = self.cursor.fetchall()
                print(f"Query executed successfully. Found {len(self.results)} results.")
                
                # Return self so we can access the results
                return self
                
        except Error as e:
            print(f"Error while executing query: {e}")
            if self.connection and self.connection.is_connected():
                self.connection.close()
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager - close cursor and connection
        
        Args:
            exc_type: The exception type if an exception was raised
            exc_val: The exception value if an exception was raised
            exc_tb: The traceback if an exception was raised
        """
        # Close cursor if it exists
        if self.cursor:
            self.cursor.close()
            print("Cursor closed")
        
        # Close connection if it exists and is connected
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print(f"Connection to {self.database} closed")
        
        # Log exception if one occurred
        if exc_type:
            print(f"An exception occurred: {exc_val}")
            # Return False to propagate the exception
            return False


if __name__ == "__main__":
    # Example usage with the specific query and parameter
    try:
        query = "SELECT * FROM users WHERE age > ?"
        params = (25,)
        
        with ExecuteQuery(query, params) as query_result:
            if query_result.results:
                print("Users over 25 years old:")
                for user in query_result.results:
                    print(user)
            else:
                print("No users found over 25 years old.")
                
    except Error as e:
        print(f"Query execution failed: {e}")
