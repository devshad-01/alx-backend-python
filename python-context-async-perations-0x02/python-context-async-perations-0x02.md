# Python Context Managers and Asynchronous Operations

This directory contains implementations of Python context managers and asynchronous operations for database access. These projects demonstrate key Python features for resource management and concurrent execution.

## Overview

Modern Python applications often need to manage resources efficiently and handle operations concurrently. This project showcases:

1. **Context Managers**: Using the `with` statement to manage resources automatically
2. **Parameterized Queries**: Safe handling of SQL queries with parameters
3. **Asynchronous Database Operations**: Using `asyncio` and `aiosqlite` for concurrent database access

## Files and Implementations

### 1. `0-databaseconnection.py`
**Custom Class-based Context Manager for Database Connection**

This file implements a context manager `DatabaseConnection` that automatically handles opening and closing MySQL database connections.

Key features:
- Implements `__enter__` and `__exit__` methods for use with the `with` statement
- Handles connection creation and cleanup
- Provides proper error handling and resource management
- Returns a cursor for executing queries

Usage example:
```python
with DatabaseConnection() as cursor:
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    # Process results
```

### 2. `1-execute.py`
**Reusable Query Context Manager**

This file implements a context manager `ExecuteQuery` that executes parameterized SQL queries and manages the connection lifecycle.

Key features:
- Takes a query string and parameters as input
- Executes the query during context entry
- Manages both connection and query execution
- Returns query results for processing
- Ensures proper cleanup of database resources

Usage example:
```python
query = "SELECT * FROM users WHERE age > ?"
params = (25,)

with ExecuteQuery(query, params) as query_result:
    for user in query_result.results:
        print(user)
```

### 3. `3-concurrent.py`
**Concurrent Asynchronous Database Queries**

This file demonstrates how to execute multiple database queries concurrently using `asyncio.gather()` and `aiosqlite`.

Key features:
- Uses `aiosqlite` for asynchronous SQLite operations
- Implements two async query functions:
  - `async_fetch_users()`: Fetches all users
  - `async_fetch_older_users()`: Fetches users older than 40
- Uses `asyncio.gather()` to run both queries concurrently
- Provides performance comparison between concurrent and sequential execution

Usage example:
```python
# Run both queries concurrently
all_users, older_users = asyncio.run(fetch_concurrently())
```

## Technical Concepts

### Context Managers

Context managers in Python provide a clean way to manage resources by ensuring proper acquisition and release, even when exceptions occur. The protocol consists of implementing `__enter__` and `__exit__` methods:

- `__enter__`: Acquires resources and returns an object
- `__exit__`: Releases resources and handles exceptions

### Parameterized Queries

Using parameterized queries helps prevent SQL injection attacks by separating SQL code from data. The database connector handles proper escaping and formatting of parameters.

### Asynchronous Execution

Asynchronous programming allows operations that involve waiting (like I/O) to run concurrently:

- `async`/`await` syntax provides clear asynchronous code
- `asyncio.gather()` runs multiple coroutines concurrently
- Event loops manage the execution of asynchronous tasks

## Benefits

1. **Resource Management**: Automatic cleanup of resources, even when exceptions occur
2. **Code Readability**: Structured approach to handling database operations
3. **Performance**: Improved performance through concurrent execution
4. **Security**: Protection against SQL injection through parameterized queries
5. **Maintainability**: Better separation of concerns and reusable components

## Requirements

- Python 3.7+
- MySQL Connector for Python (`mysql.connector`)
- `aiosqlite` for asynchronous SQLite operations
