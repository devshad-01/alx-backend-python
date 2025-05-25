#!/usr/bin/python3
"""
Module for executing concurrent asynchronous database queries using asyncio and aiosqlite
"""
import asyncio
import aiosqlite
import time
import os


async def async_fetch_users():
    """
    Asynchronous function to fetch all users from the database
    
    Returns:
        list: List of all users
    """
    print("Starting to fetch all users...")
    # Connect to an in-memory SQLite database
    async with aiosqlite.connect(':memory:') as db:
        # Create a table and insert some test data
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')
        
        # Insert sample data
        await db.executemany(
            "INSERT INTO users (name, age) VALUES (?, ?)",
            [
                ('John', 30),
                ('Jane', 45),
                ('Bob', 25),
                ('Alice', 50),
                ('Charlie', 35),
                ('Diana', 42),
                ('Edward', 28),
                ('Fiona', 55)
            ]
        )
        await db.commit()
        
        # Fetch all users
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        
        # Convert to list of dictionaries for better readability
        result = [{'id': user[0], 'name': user[1], 'age': user[2]} for user in users]
        
        print(f"Fetched {len(result)} users")
        return result


async def async_fetch_older_users():
    """
    Asynchronous function to fetch users older than 40 from the database
    
    Returns:
        list: List of users older than 40
    """
    print("Starting to fetch older users (>40)...")
    # Connect to an in-memory SQLite database
    async with aiosqlite.connect(':memory:') as db:
        # Create a table and insert some test data
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')
        
        # Insert sample data
        await db.executemany(
            "INSERT INTO users (name, age) VALUES (?, ?)",
            [
                ('John', 30),
                ('Jane', 45),
                ('Bob', 25),
                ('Alice', 50),
                ('Charlie', 35),
                ('Diana', 42),
                ('Edward', 28),
                ('Fiona', 55)
            ]
        )
        await db.commit()
        
        # Fetch users older than 40
        cursor = await db.execute("SELECT * FROM users WHERE age > 40")
        older_users = await cursor.fetchall()
        
        # Convert to list of dictionaries for better readability
        result = [{'id': user[0], 'name': user[1], 'age': user[2]} for user in older_users]
        
        print(f"Fetched {len(result)} users older than 40")
        return result


async def fetch_concurrently():
    """
    Execute both database queries concurrently using asyncio.gather
    
    Returns:
        tuple: Results from both queries (all_users, older_users)
    """
    print("Starting concurrent fetching...")
    start_time = time.time()
    
    # Execute both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    execution_time = time.time() - start_time
    print(f"Concurrent execution completed in {execution_time:.2f} seconds")
    
    # Display results
    print("\nAll Users:")
    for user in all_users:
        print(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}")
    
    print("\nUsers Older Than 40:")
    for user in older_users:
        print(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}")
    
    return all_users, older_users


def sequential_fetch():
    """
    Execute both database queries sequentially for comparison
    This helps demonstrate the advantage of async concurrency
    """
    print("\nStarting sequential fetching for comparison...")
    start_time = time.time()
    
    # Run the event loop twice, one after another
    all_users = asyncio.run(async_fetch_users())
    older_users = asyncio.run(async_fetch_older_users())
    
    execution_time = time.time() - start_time
    print(f"Sequential execution completed in {execution_time:.2f} seconds")
    
    return all_users, older_users


if __name__ == "__main__":
    # Run the concurrent fetch
    print("=== CONCURRENT EXECUTION ===")
    result = asyncio.run(fetch_concurrently())
    
    # Optional: Run sequential fetch for comparison
    print("\n=== SEQUENTIAL EXECUTION ===")
    sequential_fetch()
