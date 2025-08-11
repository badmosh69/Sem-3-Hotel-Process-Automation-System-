import mysql.connector
# from datetime import datetime


# Database connection
def connect_to_database():
    """Establish connection to the MySQL database (without creating the database)."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Default user for XAMPP
            password="",  # Default password for XAMPP
            database="hotel1"
        )
        return conn
    except mysql.connector.Error as e:
        print("Error connecting to the database:", e)
        return None

# Verify Credentials
def verify_credentials(username, password, user_type):
    """Verify username and password based on the user type."""
    file_name = "adminCredentials.txt" if user_type == "admin" else "userCredentials.txt"
    try:
        with open(file_name, "r") as file:
            for line in file:
                stored_username, stored_password = line.strip().split(",")
                if stored_username.strip() == username and stored_password.strip() == password:
                    return True
        return False
    except FileNotFoundError:
        print(f"The file '{file_name}' was not found.")
        return False

# Create Tables 
# Usage


def check_table_exists(cursor, table_name):
    """Check if a table exists in the database."""
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    return result is not None

def create_tables():
    """Create the necessary tables in the Hotel1 database."""
    db_name = "hotel1"
    # Connect to the database
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()

            # Check and create customer table
            if not check_table_exists(cursor, 'customer'):
                cursor.execute("""
                    CREATE TABLE customer (
                        cust_id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        age INT NOT NULL,
                        gender ENUM('Male', 'Female', 'Other') NOT NULL,
                        contact VARCHAR(20) UNIQUE,
                        address TEXT,
                        aadhaar BIGINT UNIQUE
                    );
                """)
                print("Customer table created.")

            # Check and create rooms table
            if not check_table_exists(cursor, 'rooms'):
                cursor.execute("""
                    CREATE TABLE rooms (
                        room_no INT PRIMARY KEY,
                        type VARCHAR(50),
                        price DECIMAL(10, 2),
                        status BOOLEAN DEFAULT TRUE
                    );
                """)
                print("Rooms table created.")

                # Populate the rooms table with default entries
                room_types = {
                    "Normal": 1000.00,
                    "Deluxe": 2000.00,
                    "Supreme Deluxe": 3000.00,
                    "Luxury Sumpreme Deluxe": 4000.00
                }
                room_number = 1
                for room_type, price in room_types.items():
                    for _ in range(5):  # Add 5 rooms for each type
                        cursor.execute("""
                            INSERT INTO rooms (room_no, type, price, status)
                            VALUES (%s, %s, %s, TRUE)
                        """, (room_number, room_type, price))
                        room_number += 1
                print("20 rooms added to the rooms table.")

            # Check and create bill table
            if not check_table_exists(cursor, 'bill'):
                cursor.execute("""
                    CREATE TABLE bill (
                        bill_no INT AUTO_INCREMENT PRIMARY KEY,
                        room_no INT,
                        cust_id INT,
                        amount DECIMAL(10, 2),
                        FOREIGN KEY (room_no) REFERENCES rooms(room_no),
                        FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
                    );
                """)
                print("Bill table created.")

            # Check and create booking table
            if not check_table_exists(cursor, 'booking'):
                cursor.execute("""
                    CREATE TABLE booking (
                        book_id INT AUTO_INCREMENT PRIMARY KEY,
                        cust_id INT,
                        room_no INT,
                        check_in DATE,
                        check_out DATE,
                        bill_no INT,
                        FOREIGN KEY (cust_id) REFERENCES customer(cust_id),
                        FOREIGN KEY (room_no) REFERENCES rooms(room_no),
                        FOREIGN KEY (bill_no) REFERENCES bill(bill_no)
                    );
                """)
                print("Booking table created.")

            # Check and create staff table
            if not check_table_exists(cursor, 'staff'):
                cursor.execute("""
                    CREATE TABLE staff (
                        staff_id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        age INT NOT NULL,
                        gender ENUM('Male', 'Female', 'Other') NOT NULL,
                        contact VARCHAR(20),
                        address TEXT,
                        designation VARCHAR(50),
                        shift ENUM('Morning', 'Evening') NOT NULL
                    );
                """)
                print("Staff table created.")
                default_staff = [
                    ('John Doe', 35, 'Male', '1111111111', '123 Main St', 'Manager', 'Morning'),
                    ('Jane Smith', 28, 'Female', '2222222222', '456 Oak Ave', 'Receptionist', 'Evening'),
                    ('Bob Johnson', 32, 'Male', '3333333333', '789 Pine Rd', 'Housekeeping', 'Morning'),
                    ('Alice Brown', 30, 'Female', '4444444444', '321 Elm St', 'Chef', 'Evening'),
                    ('Mike Wilson', 40, 'Male', '5555555555', '654 Maple Dr', 'Security', 'Night')
                ]

                for staff in default_staff:
                    cursor.execute("""
                        INSERT INTO staff (name, age, gender, contact, address, designation, shift)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, staff)

                print("5 default staff members added to the staff table.")

            connection.commit()
        except mysql.connector.Error as e:
            print("Error creating tables:", e)
        finally:
            cursor.close()
            connection.close()