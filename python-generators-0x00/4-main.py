#!/usr/bin/python3
"""
Test script for the age streaming and average calculation functionality
"""
import sys
from itertools import islice
from time import time
stream_ages = __import__('4-stream_ages')


def main():
    try:
        print("First 10 ages from the generator:")
        for age in islice(stream_ages.stream_user_ages(), 10):
            print(f"User age: {age}")
            
        print("\nCalculating average age...")
        start_time = time()
        average = stream_ages.calculate_average_age()
        end_time = time()
        
        print(f"Time taken: {end_time - start_time:.5f} seconds")
        
    except BrokenPipeError:
        sys.stderr.close()


if __name__ == "__main__":
    main()
