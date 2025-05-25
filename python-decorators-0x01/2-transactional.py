#!/usr/bin/python3
"""
Module that contains decorators for database operations:
1. with_db_connection - automatically handles opening and closing connections
2. transactional - ensures operations are wrapped in a transaction
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


def transactional(func):
    """
    Decorator that manages database transactions
    
    This decorator:
    1. Begins a transaction
    2. Executes the function
    3. Commits the transaction if successful
    4. Rolls back the transaction if an exception occurs
    
    Args:
        func: The function to be decorated
        
    Returns:
        wrapper: The wrapped function with transaction management
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function
            result = func(conn, *args, **kwargs)
            
            # If no exceptions, commit the transaction
            conn.commit()
            print(f"Transaction committed successfully")
            return result
            
        except Exception as e:
            # If an exception occurs, roll back the transaction
            conn.rollback()
            print(f"Transaction rolled back due to error: {e}")
            # Re-raise the exception for further handling
            raise
            
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """
    Update a user's email address
    
    Args:
        conn: The database connection (provided by the decorator)
        user_id: The ID of the user to update
        new_email: The new email address
        
    Returns:
        int: The number of rows affected
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    rows_affected = cursor.rowcount
    print(f"Updated email for user {user_id}: {new_email} (Rows affected: {rows_affected})")
    return rows_affected


# Example usage
if __name__ == "__main__":
    # Create a test database with sample data if it doesn't exist
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist (now with email field)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        email TEXT
    )
    ''')
    
    # Insert sample data if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users_data = [
            (1, 'John', 30, 'john@example.com'),
            (2, 'Jane', 45, 'jane@example.com'),
            (3, 'Bob', 25, 'bob@example.com'),
            (4, 'Alice', 50, 'alice@example.com')
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", users_data)
        conn.commit()
        print("Sample data inserted into users table")
    
    # Check if email column exists, add it if not
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'email' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        conn.commit()
        print("Added email column to users table")
    
    conn.close()
    
    # Show initial user data
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = 1")
        user = cursor.fetchone()
        print(f"Before update - User: ID={user[0]}, Name={user[1]}, Email={user[2]}")
    
    # Update user's email with automatic transaction handling
    try:
        update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
        
        # Verify the update
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email FROM users WHERE id = 1")
            user = cursor.fetchone()
            print(f"After successful update - User: ID={user[0]}, Name={user[1]}, Email={user[2]}")
        
        # Test with a transaction that should fail (invalid user ID)
        print("\nTesting transaction rollback with invalid user ID:")
        update_user_email(user_id=999, new_email='nonexistent@example.com')
        
    except Exception as e:
        print(f"Error handling caught at top level: {e}")
        
    # Demonstrate rollback with intentional error
    try:
        @with_db_connection
        @transactional
        def update_with_error(conn, user_id):
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET email = ? WHERE id = ?", ('error@example.com', user_id))
            print("About to raise an exception...")
            # Simulate an error during the transaction
            raise ValueError("Simulated error to trigger rollback")
        
        print("\nTesting transaction rollback with simulated error:")
        update_with_error(user_id=2)
        
    except Exception as e:
        print(f"Expected error caught at top level: {e}")
        
        # Verify email was not changed due to rollback
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email FROM users WHERE id = 2")
            user = cursor.fetchone()
            print(f"After rollback - User: ID={user[0]}, Name={user[1]}, Email={user[2]}")
