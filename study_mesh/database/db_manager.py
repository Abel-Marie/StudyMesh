import sqlite3
import os
from datetime import datetime

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "planner.db")

class DatabaseManager:
    """
    Manages all database operations.
    
    This class provides methods to:
    - Initialize the database
    - Perform CRUD operations on all tables
    - Query data with filters
    """
    
    def __init__(self):
        """Initialize database manager and create tables if needed."""
        self.db_path = DB_PATH
        self.init_database()
    
    def init_database(self):
        """
        Initialize database with schema if it doesn't exist.
        
        Reads schema.sql and creates all tables.
        """
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        
        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
            conn.commit()
    
    def get_connection(self):
        """
        Get a database connection.
        
        Returns:
            sqlite3.Connection: Database connection with row factory
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn