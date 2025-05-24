#!/usr/bin/python3
"""
Module that contains functions for batch processing of user data
"""
from seed import connect_to_prodev
from mysql.connector import Error


def streamusersinbatches(batchsize):
    """
    Generator function that streams users from the database in batches
    
    Args:
        batchsize (int): Number of rows to fetch in each batch
        
    Yields:
        list: A batch of user dictionaries
    """
    connection = connect_to_prodev()
    
    try:
        if connection:
            cursor = connection.cursor(dictionary=True)
            offset = 0
            
            while True:
                # Fetch a batch of users
                cursor.execute(f"SELECT * FROM user_data LIMIT {batchsize} OFFSET {offset}")
                batch = cursor.fetchall()
                
                # If no more rows, exit the loop
                if not batch:
                    break
                    
                yield batch
                offset += batchsize
                
            cursor.close()
            connection.close()
    except Error as e:
        print(f"Error in streamusersinbatches: {e}")
        if connection:
            connection.close()


def batch_processing(batchsize=50):
    """
    Process batches of user data and filter users over age 25
    
    Args:
        batchsize (int): Number of rows to process in each batch
    """
    for batch in streamusersinbatches(batchsize):
        for user in batch:
            # Filter users over age 25
            if user['age'] > 25:
                print(user)
                print()  # Empty line for better readability
