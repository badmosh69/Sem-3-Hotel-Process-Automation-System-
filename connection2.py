import mysql.connector
from mysql.connector import Error

# connection2.py (modified to remove print statements)
def create_database_if_not_exists(db_name="hotel1"):
    try:
        # Removed: print("Checking database existence...")
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = connection.cursor()

        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        database_exists = cursor.fetchone() is not None

        if not database_exists:
            cursor.execute(f"CREATE DATABASE `{db_name}`")
            # Removed: print(f"Database '{db_name}' created successfully. wow this is unexpected ")

        cursor.close()
        connection.close()
    except Exception as e:
        print("Error while connecting to MySQL:", e)