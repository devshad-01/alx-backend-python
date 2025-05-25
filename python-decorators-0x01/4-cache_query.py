#!/usr/bin/python3
"""
Module that contains decorators for database operations:
1. with_db_connection - automatically handles opening and closing connections
2. cache_query - caches the results of database queries to avoid redundant calls
"""
import time
import sqlite3
import functools
import hashlib


# Global cache dictionary to store query results
query_cache = {}


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


def cache_query(func):
    """
    Decorator that caches the results of database queries
    
    This decorator:
    1. Creates a cache key based on the query string
    2. Checks if the result is already in the cache
    3. If found, returns the cached result without executing the query
    4. If not found, executes the query and stores the result in the cache
    
    Args:
        func: The function to be decorated
        
    Returns:
        wrapper: The wrapped function with caching capabilities
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Extract the query from args or kwargs
        query = None
        if 'query' in kwargs:
            query = kwargs['query']
        elif args and isinstance(args[0], str):
            query = args[0]
            
        if not query:
            # If no query found, just execute the function without caching
            print("No query found for caching, executing without cache")
            return func(conn, *args, **kwargs)
        
        # Create a cache key based on the query
        # Using MD5 hash to create a compact, consistent key
        cache_key = hashlib.md5(query.encode('utf-8')).hexdigest()
        
        # Check if result is in cache
        if cache_key in query_cache:
            print(f"Cache hit! Using cached result for query: {query}")
            return query_cache[cache_key]
        
        # Not in cache, execute the query
        print(f"Cache miss. Executing query: {query}")
        start_time = time.time()
        result = func(conn, *args, **kwargs)
        execution_time = time.time() - start_time
        
        # Store the result in cache
        query_cache[cache_key] = result
        print(f"Query executed in {execution_time:.4f} seconds and cached for future use")
        
        return result
    
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetch users from the database with caching
    
    Args:
        conn: The database connection (provided by the with_db_connection decorator)
        query: The SQL query to execute
        
    Returns:
        list: The query results
    """
    cursor = conn.cursor()
    cursor.execute(query)
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
    
    # Demonstration 1: First call - should execute the query and cache the result
    print("\n=== DEMONSTRATION 1: FIRST QUERY CALL (CACHE MISS) ===")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Fetched {len(users)} users from database")
    
    # Demonstration 2: Second call with the same query - should use the cached result
    print("\n=== DEMONSTRATION 2: SECOND QUERY CALL (CACHE HIT) ===")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Fetched {len(users_again)} users from cache")
    
    # Demonstration 3: Different query - should miss the cache
    print("\n=== DEMONSTRATION 3: DIFFERENT QUERY (CACHE MISS) ===")
    older_users = fetch_users_with_cache(query="SELECT * FROM users WHERE age > 40")
    print(f"Fetched {len(older_users)} users older than 40")
    
    # Demonstration 4: Repeat the different query - should hit the cache
    print("\n=== DEMONSTRATION 4: REPEAT DIFFERENT QUERY (CACHE HIT) ===")
    older_users_again = fetch_users_with_cache(query="SELECT * FROM users WHERE age > 40")
    print(f"Fetched {len(older_users_again)} users older than 40 from cache")
    
    # Display cache contents
    print("\n=== CACHE CONTENTS ===")
    print(f"Number of cached queries: {len(query_cache)}")
    for i, (key, value) in enumerate(query_cache.items()):
        print(f"Cache entry {i+1}:")
        print(f"  Key: {key}")
        print(f"  Value: {len(value)} rows")
