# tools/save_blog_post_tool.py
import mysql.connector
from crewai_tools import tool
import os

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

@tool
def save_blog_post(blog_content: str, title: str):
    """
    Saves the generated blog post to the database.

    Args:
        blog_content (str): The content of the blog post.
        title (str): The title of the blog post.

    Returns:
        str: A confirmation message.
    """
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO blogs (title, content)
        VALUES (%s, %s)
    """, (title, blog_content))

    conn.commit()
    cursor.close()
    conn.close()
    return "Blog post saved successfully."
