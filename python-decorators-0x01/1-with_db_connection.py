#!/usr/bin/python3
"""
Module that contains a decorator to handle database connections automatically
"""
import sqlite3
import functools


def with_db_connection(func):
    """
    Decorator that automatically handles opening and closing database connections
    
    This decorator:
    1. Opens a new SQLite database connection
    2. Passes the connection to the decorated function
    3. Closes the connection after the function execution
    4. Returns the result of the function
    
    Args:
        func: The function to be decorated
        
    Returns:
        wrapper: The wrapped function with automatic connection handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a new SQLite connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Pass the connection as the first argument to the function
            # Merge with any other arguments
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Ensure the connection is closed even if an exception occurs
            conn.close()
            
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Get a user from the database by their ID
    
    Args:
        conn: The database connection (provided by the decorator)
        user_id: The ID of the user to fetch
        
    Returns:
        tuple: The user data or None if not found
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


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
    
    # Fetch user by ID with automatic connection handling
    user = get_user_by_id(user_id=1)
    print(f"User found: {user}")
    
    # Try with a non-existent user
    non_existent_user = get_user_by_id(user_id=99)
    if non_existent_user:
        print(f"User found: {non_existent_user}")
    else:
        print("User with ID 99 not found")
