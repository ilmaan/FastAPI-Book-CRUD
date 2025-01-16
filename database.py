import sqlite3

def get_db_connection() -> sqlite3.Connection:
    """Establishes a connection to the SQLite database and sets the row factory."""
    conn = sqlite3.connect('books.db')  # Connect to the database file
    conn.row_factory = sqlite3.Row  # Set the row factory to return rows as dictionaries
    return conn  # Return the database connection


