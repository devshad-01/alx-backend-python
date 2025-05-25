#!/usr/bin/python3
"""
Module that contains a decorator to log database queries
"""
import sqlite3
import functools
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('database')


def log_queries(func):
    """
    Decorator that logs SQL queries before executing them
    
    Args:
        func: The function to be decorated
        
    Returns:
        wrapper: The wrapped function that logs the query before execution
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from args or kwargs
        query = None
        if 'query' in kwargs:
            query = kwargs['query']
        elif args and isinstance(args[0], str):
            query = args[0]
            
        # Log the query if found
        if query:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{timestamp}] Executing query: {query}")
            
            # Optionally measure execution time
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"Query executed in {execution_time:.4f} seconds")
            return result
        else:
            # If no query found, just execute the function
            logger.warning("No SQL query found in function arguments")
            return func(*args, **kwargs)
    
    return wrapper


@log_queries
def fetch_all_users(query):
    """
    Fetch all users from the database
    
    Args:
        query: SQL query to execute
        
    Returns:
        list: Results of the query
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


# Example usage
if __name__ == "__main__":
    # Create a test database with sample data if it doesn't exist
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL
    )
    ''')
    
    # Insert sample data if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users_data = [
            (1, 'John', 30),
            (2, 'Jane', 45),
            (3, 'Bob', 25),
            (4, 'Alice', 50)
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", users_data)
        conn.commit()
        print("Sample data inserted into users table")
    
    conn.close()
    
    # Fetch users while logging the query
    users = fetch_all_users(query="SELECT * FROM users")
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"ID: {user[0]}, Name: {user[1]}, Age: {user[2]}")
    
    # Test with a WHERE clause
    older_users = fetch_all_users("SELECT * FROM users WHERE age > 40")
    print(f"\nFound {len(older_users)} users older than 40:")
    for user in older_users:
        print(f"ID: {user[0]}, Name: {user[1]}, Age: {user[2]}")
