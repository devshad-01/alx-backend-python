# Python Generators

## Description

This project demonstrates how to use Python generators to stream rows from an SQL database one by one. It includes:

- Setting up a MySQL database
- Creating tables with appropriate fields
- Populating the database with sample data
- Using generators to efficiently stream data from the database

## Files

- `seed.py`: Contains functions to set up the database and includes a generator for streaming rows
- `0-main.py`: Test script provided by ALX
- `0-demo_generator.py`: Demonstration of the generator functionality
- `user_data.csv`: Sample data for populating the database

## Functions in seed.py

- `connect_db()`: Connects to the MySQL database server
- `create_database(connection)`: Creates the database ALX_prodev if it does not exist
- `connect_to_prodev()`: Connects to the ALX_prodev database in MySQL
- `create_table(connection)`: Creates a table user_data if it does not exist with the required fields
- `insert_data(connection, data)`: Inserts data in the database if it does not exist
- `db_row_generator(connection, batch_size)`: Generator that streams rows from the database one by one

## Usage

```bash
# Set up the database and insert data
./0-main.py

# Demonstrate the generator functionality
./0-demo_generator.py
```

## Database Schema

- Table: user_data
  - user_id (VARCHAR(36), Primary Key, Indexed)
  - name (VARCHAR(255), NOT NULL)
  - email (VARCHAR(255), NOT NULL)
  - age (DECIMAL, NOT NULL)

## Requirements

- Python 3
- MySQL
- mysql-connector-python package
