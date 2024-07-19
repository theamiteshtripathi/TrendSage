import mysql.connector
import os
from crewai_tools import tool

@tool
def store_blog(title: str, content: str):
    """
    Stores the blog post in the database.

    Args:
        title (str): The title of the blog post.
        content (str): The content of the blog post.
    """
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO blogs (title, content) VALUES (%s, %s)
    """, (title, content))
    conn.commit()
    cursor.close()
    conn.close()
    print("Blog post stored successfully")
