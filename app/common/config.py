import os
import time

import mysql.connector as conn
from dotenv import load_dotenv


# Load env variables
load_dotenv()

db_credentials = dict(
    host=os.getenv("HOST"),
    user=os.getenv("USER"),
    passwd=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE"),
)


# Create connection to database
def get_mysql_cursor(max_attempts=5):
    attempts = 0
    while attempts < max_attempts:
        try:
            mydb = conn.connect(**db_credentials)
            cursor = mydb.cursor(dictionary=True)
            print("Database connection was successful!")
            return mydb, cursor
        except Exception as error:
            attempts += 1
            print(f"Connection to database failed. Attempt: {attempts}")
            print("Error: ", error)
            time.sleep(3)

    raise Exception(f"Failed to connect to the database after {max_attempts} attempts")


def close_mysql_cursor(mydb, cursor):
    try:
        cursor.close()
        mydb.close()
        print("Database connection closed.")
    except Exception as error:
        print("Error closing database connection.")
        print("Error: ", error)
