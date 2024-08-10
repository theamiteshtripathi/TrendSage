import os
import mysql.connector
from crewai_tools import tool
from tools.connect_db import connect_to_db

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
