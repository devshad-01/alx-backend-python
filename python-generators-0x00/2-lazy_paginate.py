#!/usr/bin/python3
"""
Module that implements lazy loading of paginated data using generators
"""
seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetches a page of user data from the database
    
    Args:
        page_size (int): Number of records per page
        offset (int): Starting position for fetching records
        
    Returns:
        list: A list of user dictionaries for the requested page
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator function that lazily loads paginated data
    
    Args:
        page_size (int): Number of records per page
        
    Yields:
        list: A page of user data (list of dictionaries)
    """
    offset = 0
    
    while True:
        # Fetch the next page only when needed
        page = paginate_users(page_size, offset)
        
        # If no more data, stop iteration
        if not page:
            break
        
        # Yield the current page
        yield page
        
        # Move to the next page
        offset += page_size
