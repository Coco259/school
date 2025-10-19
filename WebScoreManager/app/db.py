import os
import pymysql


def get_db():
    """Create a new database connection using environment-backed settings."""
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'y210093'),
        database=os.getenv('DB_NAME', 'school_db'),
        port=int(os.getenv('DB_PORT', 3306)),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
    )
