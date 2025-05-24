#!/usr/bin/python3
"""
Module that contains a generator function to stream rows from a database
"""
from seed import connect_to_prodev
from mysql.connector import Error


def stream_users():
    """
    Generator function that streams users from the database one by one
    Returns: Dictionary with user information for each row
    """
    connection = connect_to_prodev()
    
    try:
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_data")
            
            for row in cursor:
                # Convert the row to the expected format
                yield {
                    'user_id': row['user_id'],
                    'name': row['name'],
                    'email': row['email'],
                    'age': row['age']
                }
                
            cursor.close()
            connection.close()
    except Error as e:
        print(f"Error in stream_users: {e}")
        if connection:
            connection.close()
