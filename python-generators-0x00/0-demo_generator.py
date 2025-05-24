#!/usr/bin/python3
"""
Main script to demonstrate the use of the generator
"""
import seed

def main():
    # Connect to the database
    connection = seed.connect_to_prodev()
    if connection:
        print("Connected to ALX_prodev database")
        
        # Use the generator to stream rows
        print("Streaming rows from database using generator:")
        for i, row in enumerate(seed.db_row_generator(connection)):
            print(f"Row {i+1}: {row}")
            if i >= 4:  # Just show the first 5 rows
                break
                
        connection.close()
    else:
        print("Failed to connect to the database")

if __name__ == "__main__":
    main()
