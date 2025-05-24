#!/usr/bin/python3
"""
Seed script to set up MySQL database and populate it with data
"""
import csv
import mysql.connector
from mysql.connector import Error


def connect_db():
    """Connects to the MySQL database server"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return None


def create_database(connection):
    """Creates the database ALX_prodev if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ALX_prodev'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
    return None


def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL NOT NULL,
                INDEX (user_id)
            )
        """)
        print("Table user_data created successfully")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, data_file):
    """Inserts data in the database if it does not exist"""
    try:
        cursor = connection.cursor()
        
        # Check if the table already has data
        cursor.execute("SELECT COUNT(*) FROM user_data")
        count = cursor.fetchone()[0]
        
        if count == 0:  # Only insert if table is empty
            with open(data_file, mode='r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Skip header row
                
                for row in csv_reader:
                    # Check if record already exists
                    cursor.execute("SELECT COUNT(*) FROM user_data WHERE user_id = %s", (row[0],))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(
                            "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                            (row[0], row[1], row[2], int(row[3]))
                        )
            
            connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error inserting data: {e}")
    except FileNotFoundError:
        print(f"File {data_file} not found")


def db_row_generator(connection, batch_size=100):
    """Generator function that streams rows from the database one by one"""
    try:
        cursor = connection.cursor()
        offset = 0
        
        while True:
            cursor.execute(f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}")
            rows = cursor.fetchall()
            
            if not rows:
                break
                
            for row in rows:
                yield row
                
            offset += batch_size
            
        cursor.close()
    except Error as e:
        print(f"Error in generator: {e}")
        yield None
