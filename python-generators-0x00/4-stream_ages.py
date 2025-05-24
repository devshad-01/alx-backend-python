#!/usr/bin/python3
"""
Module that contains a generator to stream user ages and calculate average age
"""
from seed import connect_to_prodev
from mysql.connector import Error


def streamuserages():
    """
    Generator function that yields user ages one by one
    
    Yields:
        int: Age of a user
    """
    connection = connect_to_prodev()
    
    try:
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT age FROM user_data")
            
            for row in cursor:
                yield row['age']
                
            cursor.close()
            connection.close()
    except Error as e:
        print(f"Error in streamuserages: {e}")
        if connection:
            connection.close()


def calculate_average_age():
    """
    Calculate the average age of all users without loading the entire dataset into memory
    
    Returns:
        float: The average age of all users
    """
    total_age = 0
    count = 0
    
    for age in streamuserages():
        total_age += age
        count += 1
    
    if count > 0:
        average_age = total_age / count
        print(f"Average age: {average_age:.2f}")
        print(f"Total users: {count}")
        return average_age
    else:
        print("No users found")
        return 0
