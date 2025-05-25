#!/usr/bin/python3
"""
Module that contains decorators for database operations:
1. with_db_connection - automatically handles opening and closing connections
2. retry_on_failure - retries database operations if they fail due to transient errors
"""
import time
import sqlite3
import functools
import random


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


def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries a function if it fails with an exception
    
    This decorator:
    1. Attempts to execute the function
    2. If it fails, waits for a delay period
    3. Retries up to the specified number of times
    4. Uses exponential backoff to increase delay between retries
    
    Args:
        retries (int): Maximum number of retry attempts (default: 3)
        delay (int): Initial delay in seconds between retries (default: 2)
        
    Returns:
        decorator: The decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize variables
            attempts = 0
            current_delay = delay
            last_exception = None
            
            # Attempt the function with retries
            while attempts <= retries:
                try:
                    if attempts > 0:
                        print(f"Retry attempt {attempts}/{retries}...")
                    
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    attempts += 1
                    last_exception = e
                    
                    if attempts <= retries:
                        # Add a small random factor to avoid thundering herd problems
                        jitter = random.uniform(0.1, 0.5)
                        wait_time = current_delay + jitter
                        
                        print(f"Operation failed: {e}")
                        print(f"Waiting {wait_time:.2f} seconds before retry...")
                        
                        # Wait before retrying
                        time.sleep(wait_time)
                        
                        # Exponential backoff - double the delay for each retry
                        current_delay *= 2
                    else:
                        print(f"Maximum retry attempts ({retries}) reached.")
                        # Re-raise the last exception when retries are exhausted
                        raise last_exception
                        
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """
    Fetch all users from the database with automatic retry on failure
    
    Args:
        conn: The database connection (provided by the with_db_connection decorator)
        
    Returns:
        list: List of all users
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


# Example usage
if __name__ == "__main__":
    # Setup: Create a test database with sample data if it doesn't exist
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
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
    
    conn.close()
    
    # Demonstration 1: Normal successful operation
    print("\n=== DEMONSTRATION 1: NORMAL SUCCESSFUL OPERATION ===")
    try:
        users = fetch_users_with_retry()
        print(f"Successfully fetched {len(users)} users:")
        for user in users:
            print(f"ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Email: {user[3]}")
    except Exception as e:
        print(f"Operation failed: {e}")
    
    # Demonstration 2: Simulating transient failures
    print("\n=== DEMONSTRATION 2: SIMULATING TRANSIENT FAILURES ===")
    # Decorator to inject failures
    def inject_failures(num_failures):
        def decorator(func):
            failure_count = [0]  # Using a list for mutable closure
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if failure_count[0] < num_failures:
                    failure_count[0] += 1
                    raise sqlite3.OperationalError(f"Simulated database error (failure {failure_count[0]}/{num_failures})")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    # Apply both decorators: connection handling and retry logic
    @with_db_connection
    @retry_on_failure(retries=3, delay=1)
    @inject_failures(2)  # Simulate 2 failures before success
    def fetch_users_with_simulated_failures(conn):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    
    try:
        users = fetch_users_with_simulated_failures()
        print(f"After retries, successfully fetched {len(users)} users")
    except Exception as e:
        print(f"Even with retries, operation ultimately failed: {e}")
    
    # Demonstration 3: Failing all attempts
    print("\n=== DEMONSTRATION 3: ALL ATTEMPTS FAIL ===")
    @with_db_connection
    @retry_on_failure(retries=2, delay=1)
    @inject_failures(5)  # More failures than retries
    def fetch_users_will_fail_all_retries(conn):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    
    try:
        users = fetch_users_will_fail_all_retries()
        print("This should not be printed as all attempts should fail")
    except Exception as e:
        print(f"All retry attempts failed as expected: {e}")
