import os
import mysql.connector
from mysql.connector import Error

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        return conn
    except Error as err:
        print(f"Error connecting to database: {err}")
        raise