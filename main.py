import mysql.connector
import cv2
import pytesseract
import connection2
import database_connection
import admin_User_functions
from datetime import datetime

# Booking Room
import re
def extract_customer_details_from_text_file():
    try:
        # Open and read the extracted text file
        with open('extracted_text.txt', 'r') as file:
            extracted_text = file.readlines()
        
        # print("Extracted Text from File: ")
        # print(extracted_text)
        
        # Initialize variables for extracted details
        name = dob = gender = address = aadhaar = "Not found"
        age = "Not available"
        address_lines = []
        address_started = False  # Flag to track if address section has started

        # Iterate over each line and check for relevant details
        for line in extracted_text:
            # Extract Name
            if line.startswith("Name :") or line.startswith("Name:"):
                name = line.split(":", 1)[1].strip()
            
            # Extract D.O.B.
            elif line.startswith("D.O.B :")or line.startswith("D.O.B:"):
                dob = line.split(":", 1)[1].strip()
                
                # Calculate Age if D.O.B. is found
                if dob != "Not found":
                    dob_date = datetime.strptime(dob, "%d/%m/%Y")
                    age = (datetime.now() - dob_date).days // 365
            
            # Extract Gender
            elif line.startswith("Sex :")or line.startswith("Sex:"): 
                gender = line.split(":", 1)[1].strip()

            # Start capturing address if "Address :" is found
            elif "address" in line.lower() or address_started:
                if "address" in line.lower() and not address_started:
                    address_started = True
                    # Append only the part after "Address:" and strip redundant parts
                    cleaned_line = line.split(":", 1)[1].strip() if ":" in line else line.strip()
                    address_lines.append(cleaned_line)
                elif address_started and line.strip():  # Add subsequent non-empty lines
                    address_lines.append(line.strip())
                elif address_started and not line.strip():  # Stop capturing address on an empty line
                    address_started = False

        # If address lines are captured, combine them
        if address_lines:
            address = " ".join(address_lines)

        # Extract Aadhaar number (12 digits, with or without spaces)
        aadhaar_pattern = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
        for line in extracted_text:
            match = aadhaar_pattern.search(line)
            if match:
                aadhaar = match.group(0).replace(" ", "")  # Remove spaces
                break

        # Print the extracted details
        print(f"Name: {name}")
        print(f"D.O.B.: {dob}")
        print(f"Age: {age}")
        print(f"Gender: {gender}")
        print(f"Address: {address}")
        print(f"Aadhaar Number: {aadhaar}")
        
        # Return extracted details for further use (e.g., database insertion)
        customer_details = {
            'name': name,
            'dob': dob,
            'age': age,
            'gender': gender,
            'address': address,
            'aadhaar': aadhaar  # Include Aadhaar in the returned details
        }
        return customer_details
    
    except FileNotFoundError:
        print("Error: The file 'extracted_text.txt' was not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def extract_text_from_image(image_path):
    try:
        # Load the image
        img = cv2.imread(image_path)
        
        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Thresholding for better OCR results
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Extract text using pytesseract
        extracted_text = pytesseract.image_to_string(thresh, lang='eng')
        
        # Save the extracted text into a .txt file
        with open('extracted_text.txt', 'w') as file:
            file.write(extracted_text)
        
        print("Text extracted and saved to 'extracted_text.txt'")
        
    except Exception as e:
        print(f"Error: {e}")




import mysql.connector
import os
from decimal import Decimal
# Main Menu
def menu(user_type):
    """Display menu based on the user type."""
    while True:
        if user_type == "admin":
            print("\n--- Admin Menu ---")
            print("1. Manage Staff")
            print("2. Manage Room Bookings")
            print("3. Billing and Discounts")
            print("4. Manage Rooms")
            print("5. Analytics")
            print("6. Exit")
            choice = input("Enter your choice: ").strip()

            connection = database_connection.connect_to_database()
            if not connection:
                print("Database connection error. Please try again.")
                break

            cursor = connection.cursor()

            if choice == '1':  # Manage Staff
                while True:
                    print("\n--- Manage Staff ---")
                    print("1. Add Staff")
                    print("2. Remove Staff")
                    print("3. View All Staff")
                    print("4. Update Staff Details")
                    print("5. Back to Admin Menu")
                    staff_choice = input("Enter your choice: ").strip()

                    if staff_choice == '1':  # Add Staff
                        while True:
                            try:
                                name = input("Enter staff name: ").strip()
                                if not admin_User_functions.validate_name(name):
                                    if not admin_User_functions.ask_retry_or_cancel():
                                        break
                                    continue

                                age = input("Enter staff age: ").strip()
                                if not admin_User_functions.validate_age(age):
                                    if not admin_User_functions.ask_retry_or_cancel():
                                        break
                                    continue
                                age = int(age)

                                gender = input("Enter staff gender (Male/Female/Other): ").strip()
                                if not admin_User_functions.validate_gender(gender):
                                    if not admin_User_functions.ask_retry_or_cancel():
                                        break
                                    continue

                                contact = input("Enter staff contact number (10 digits): ").strip()
                                if not admin_User_functions.validate_contact(contact):
                                    if not admin_User_functions.ask_retry_or_cancel():
                                        break
                                    continue

                                address = input("Enter staff address: ").strip()
                                if not admin_User_functions.validate_address(address):
                                    if not admin_User_functions.ask_retry_or_cancel():
                                        break
                                    continue

                                designation = input("Enter staff designation: ").strip()
                                if not admin_User_functions.validate_designation(designation):
                                    if not admin_User_functions.ask_retry_or_cancel():
                                        break
                                    continue

                                shift = input("Enter staff shift (Morning/Evening): ").strip()
                                if not admin_User_functions.validate_shift(shift):
                                    if not admin_User_functions.ask_retry_or_cancel():
                                        break
                                    continue

                                # Check if staff already exists
                                cursor.execute("SELECT * FROM staff WHERE contact = %s", (contact,))
                                existing_staff = cursor.fetchone()

                                if existing_staff:
                                    print("Staff with this contact already exists. Returning to Admin Menu.")
                                    break
                                else:
                                    cursor.execute("""
                                        INSERT INTO staff (name, age, gender, contact, address, designation, shift) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    """, (name, age, gender, contact, address, designation, shift))
                                    connection.commit()
                                    print("Staff member added successfully!")
                                    break
                            except mysql.connector.Error as e:
                                print("Error adding staff:", e)
                                if not admin_User_functions.ask_retry_or_cancel():
                                    break

                    elif staff_choice == '2':  # Remove Staff
                        try:
                            cursor.execute("SELECT staff_id, name FROM staff")
                            staff_members = cursor.fetchall()

                            if staff_members:
                                print("\n--- Staff Members ---")
                                for staff in staff_members:
                                    print(f"ID: {staff[0]}, Name: {staff[1]}")

                                staff_id = input("\nEnter the Staff ID to remove: ").strip()
                                if not staff_id.isdigit():
                                    print("Error: Staff ID must be a number.")
                                    continue

                                staff_id = int(staff_id)
                                cursor.execute("SELECT * FROM staff WHERE staff_id = %s", (staff_id,))
                                staff = cursor.fetchone()

                                if staff:
                                    cursor.execute("DELETE FROM staff WHERE staff_id = %s", (staff_id,))
                                    connection.commit()
                                    print(f"Staff with ID {staff_id} removed successfully!")
                                else:
                                    print("Staff ID not found. Returning to Admin Menu.")
                            else:
                                print("No staff members available.")
                        except mysql.connector.Error as e:
                            print("Error removing staff:", e)

                    elif staff_choice == '3':  # View All Staff
                        try:
                            cursor.execute("SELECT * FROM staff")
                            staff_members = cursor.fetchall()
                            if staff_members:
                                print("\n--- Staff Details ---")
                                for staff in staff_members:
                                    print(f"ID: {staff[0]}, Name: {staff[1]}, Age: {staff[2]}, Gender: {staff[3]}, "
                                        f"Contact: {staff[4]}, Address: {staff[5]}, Designation: {staff[6]}, Shift: {staff[7]}")
                            else:
                                print("No staff members found.")
                        except mysql.connector.Error as e:
                            print("Error retrieving staff details:", e)

                    elif staff_choice == '4':  # Update Staff Details
                        try:
                            cursor.execute("SELECT staff_id, name FROM staff")
                            staff_members = cursor.fetchall()

                            if staff_members:
                                print("\n--- Staff Members ---")
                                for staff in staff_members:
                                    print(f"ID: {staff[0]}, Name: {staff[1]}")

                                staff_id = input("\nEnter the Staff ID to update: ").strip()
                                if not staff_id.isdigit():
                                    print("Error: Staff ID must be a number.")
                                    continue

                                staff_id = int(staff_id)
                                cursor.execute("SELECT * FROM staff WHERE staff_id = %s", (staff_id,))
                                staff = cursor.fetchone()

                                if staff:
                                    while True:
                                        print("\n--- Update Staff Details ---")
                                        print("1. Update Name")
                                        print("2. Update Age")
                                        print("3. Update Gender")
                                        print("4. Update Contact")
                                        print("5. Update Address")
                                        print("6. Update Designation")
                                        print("7. Update Shift")
                                        print("8. Back to Manage Staff Menu")
                                        update_choice = input("Enter your choice: ").strip()

                                        if update_choice == '1':  # Update Name
                                            new_name = input("Enter new name: ").strip()
                                            if admin_User_functions.validate_name(new_name):
                                                cursor.execute("UPDATE staff SET name = %s WHERE staff_id = %s", (new_name, staff_id))
                                                connection.commit()
                                                print("Name updated successfully!")
                                            else:
                                                if not admin_User_functions.ask_retry_or_cancel():
                                                    break

                                        elif update_choice == '2':  # Update Age
                                            new_age = input("Enter new age: ").strip()
                                            if admin_User_functions.validate_age(new_age):
                                                cursor.execute("UPDATE staff SET age = %s WHERE staff_id = %s", (int(new_age), staff_id))
                                                connection.commit()
                                                print("Age updated successfully!")
                                            else:
                                                if not admin_User_functions.ask_retry_or_cancel():
                                                    break

                                        elif update_choice == '3':  # Update Gender
                                            new_gender = input("Enter new gender (Male/Female/Other): ").strip()
                                            if admin_User_functions.validate_gender(new_gender):
                                                cursor.execute("UPDATE staff SET gender = %s WHERE staff_id = %s", (new_gender, staff_id))
                                                connection.commit()
                                                print("Gender updated successfully!")
                                            else:
                                                if not admin_User_functions.ask_retry_or_cancel():
                                                    break

                                        elif update_choice == '4':  # Update Contact
                                            new_contact = input("Enter new contact number (10 digits): ").strip()
                                            if admin_User_functions.validate_contact(new_contact):
                                                cursor.execute("UPDATE staff SET contact = %s WHERE staff_id = %s", (new_contact, staff_id))
                                                connection.commit()
                                                print("Contact updated successfully!")
                                            else:
                                                if not admin_User_functions.ask_retry_or_cancel():
                                                    break

                                        elif update_choice == '5':  # Update Address
                                            new_address = input("Enter new address: ").strip()
                                            if admin_User_functions.validate_address(new_address):
                                                cursor.execute("UPDATE staff SET address = %s WHERE staff_id = %s", (new_address, staff_id))
                                                connection.commit()
                                                print("Address updated successfully!")
                                            else:
                                                if not admin_User_functions.ask_retry_or_cancel():
                                                    break

                                        elif update_choice == '6':  # Update Designation
                                            new_designation = input("Enter new designation: ").strip()
                                            if admin_User_functions.validate_designation(new_designation):
                                                cursor.execute("UPDATE staff SET designation = %s WHERE staff_id = %s", (new_designation, staff_id))
                                                connection.commit()
                                                print("Designation updated successfully!")
                                            else:
                                                if not admin_User_functions.ask_retry_or_cancel():
                                                    break

                                        elif update_choice == '7':  # Update Shift
                                            new_shift = input("Enter new shift (Morning/Evening): ").strip()
                                            if admin_User_functions.validate_shift(new_shift):
                                                cursor.execute("UPDATE staff SET shift = %s WHERE staff_id = %s", (new_shift, staff_id))
                                                connection.commit()
                                                print("Shift updated successfully!")
                                            else:
                                                if not admin_User_functions.ask_retry_or_cancel():
                                                    break

                                        elif update_choice == '8':  # Back to Manage Staff Menu
                                            break

                                        else:
                                            print("Invalid choice. Please try again.")
                                else:
                                    print("Staff ID not found. Returning to Manage Staff Menu.")
                            else:
                                print("No staff members available.")
                        except mysql.connector.Error as e:
                            print("Error updating staff details:", e)

                    elif staff_choice == '5':  # Back to Admin Menu
                        break

                    else:
                        print("Invalid choice. Please try again.")

            elif choice == '2':  # Manage Room Bookings
                print("\n--- Manage Room Bookings ---")
                admin_User_functions.book_room()

            elif choice == '3':  # Billing and Discounts (Admin)
                print("\n--- Billing and Discounts ---")
                admin_User_functions.generate_bill(user_type)
   
            elif choice == '4':  # Manage Rooms
                while True:
                    print("\n--- Manage Rooms ---")
                    print("1. Add Room")
                    print("2. Remove Room")
                    print("3. View all rooms ")
                    print("4. Back to Admin Menu")
                    room_choice = input("Enter your choice: ").strip()

                    if room_choice == '1':  # Add Room
                        # try:
                        #     room_no = int(input("Enter Room Number: "))
                        #     room_type = input("Enter Room Type: ")
                        #     price = float(input("Enter Room Price: "))
                        #     cursor.execute("""
                        #         INSERT INTO rooms (room_no, type, price, status) 
                        #         VALUES (%s, %s, %s, TRUE)
                        #     """, (room_no, room_type, price))
                        #     connection.commit()
                        #     print("Room added successfully!")
                        # except mysql.connector.Error as e:
                        #     print("Error adding room:", e)
                        try:
                            room_no = int(input("Enter Room Number: "))
                            room_type = input("Enter Room Type: ")
                            price = float(input("Enter Room Price: "))

                            # ✅ Check if room already exists
                            cursor.execute("SELECT room_no FROM rooms WHERE room_no = %s", (room_no,))
                            existing_room = cursor.fetchone()

                            if existing_room:
                                print(f"Error: Room {room_no} already exists!")
                            else:
                                # ✅ Insert new room only if it doesn't exist
                                cursor.execute("""
                                    INSERT INTO rooms (room_no, type, price, status) 
                                    VALUES (%s, %s, %s, TRUE)
                                """, (room_no, room_type, price))
                                connection.commit()
                                print("Room added successfully!")

                        except mysql.connector.Error as e:
                            print("Error:", e)

                        
                    elif room_choice == '2':  # Remove Room
                        try:
                            cursor.execute("SELECT room_no, type FROM rooms WHERE status = TRUE")
                            available_rooms = cursor.fetchall()

                            if available_rooms:
                                print("\n--- Available Rooms ---")
                                for room in available_rooms:
                                    print(f"Room No: {room[0]}, Type: {room[1]}")

                                room_no = int(input("\nEnter Room Number to Remove: "))
                                cursor.execute("SELECT * FROM rooms WHERE room_no = %s", (room_no,))
                                room = cursor.fetchone()

                                if room:
                                    cursor.execute("DELETE FROM rooms WHERE room_no = %s", (room_no,))
                                    connection.commit()
                                    print(f"Room {room_no} removed successfully!")
                                else:
                                    print("Room number not found. Returning to Admin Menu.")
                            else:
                                print("No rooms available.")
                        except mysql.connector.Error as e:
                            print("Error removing room:", e)
                    elif room_choice=='3':
                        try:
                            cursor.execute("SELECT * FROM rooms")
                            rooms = cursor.fetchall()
                            if rooms:
                                print("\n--- Room Details ---")
                                room_types = set()
                                for room in rooms:
                                    if room[1] not in room_types:
                                        print(f"For {room[1]} Type of room only :~ ")
                                        print()
                                        for roomss in rooms:
                                            if room[1] == roomss[1]:
                                                print(f"ID : {roomss[0]} , Price : {roomss[2]} , status : {'Available ' if (roomss[3] == 1) else 'Not Available'}")
                                        room_types.add(room[1]) 
                                        print()  
                        except mysql.connector.Error as e:
                            print("Error retrieving staff details:", e)

                    elif room_choice == '4':  # Back to Admin Menu
                        break

                    else:
                        print("Invalid choice. Please try again.")

            elif choice == '5':  # Analytics
                connection = database_connection.connect_to_database()
                if connection:
                    try:
                        cursor = connection.cursor()
                        while True:
                            print("\n--- Analytics Menu ---")
                            print("1. Room Occupancy Pie Chart")
                            print("2. Sales Over Time Analysis")
                            print("3. Return to Admin Menu")
                            analytics_choice = input("Enter your choice: ").strip()

                            if analytics_choice == '1':
                                try:
                                    import matplotlib.pyplot as plt
                                    
                                    # Room occupancy pie chart
                                    cursor.execute("SELECT status, COUNT(*) FROM rooms GROUP BY status")
                                    data = cursor.fetchall()
                                    
                                    if data:
                                        labels = ['Occupied' if status == 0 else 'Vacant' for status,i in data]
                                        sizes = [count for i, count in data]
                                        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
                                        plt.title('Room Occupancy Distribution')
                                        plt.show()
                                    else:
                                        print("No room data available.")
                                        
                                except ImportError:
                                    print("Matplotlib not installed. Install using: pip install matplotlib")

                            elif analytics_choice == '2':
                                try:
                                    import matplotlib.pyplot as plt
                                    from datetime import datetime
                                    
                                    # Sales over time analysis
                                    cursor.execute("""
                                        SELECT b.check_in, SUM(bil.amount) 
                                        FROM booking b
                                        JOIN bill bil ON b.bill_no = bil.bill_no
                                        WHERE b.bill_no IS NOT NULL
                                        GROUP BY b.check_in
                                        ORDER BY b.check_in
                                    """)
                                    sales_data = cursor.fetchall()
                                    
                                    if sales_data:
                                        dates = [datetime.strptime(str(date), '%Y-%m-%d') for date, i in sales_data]
                                        amounts = [float(amount) for i, amount in sales_data]
                                        
                                        plt.figure(figsize=(10, 5))
                                        plt.plot(dates, amounts, marker='o', linestyle='-')
                                        plt.title('Sales Over Time')
                                        plt.xlabel('Date')
                                        plt.ylabel('Total Sales (₹)')
                                        plt.grid(True)
                                        plt.xticks(rotation=45)
                                        plt.tight_layout()
                                        plt.show()
                                    else:
                                        print("No sales data available.")
                                        
                                except ImportError:
                                    print("Matplotlib not installed. Install using: pip install matplotlib")

                            elif analytics_choice == '3':
                                break  # Return to admin menu

                            else:
                                print("Invalid analytics choice. Try again.")

                    except mysql.connector.Error as e:
                        print("Database error:", e)
                    finally:
                        cursor.close()
                        connection.close()

            elif choice == '6':  # Exit Admin Menu
                print("Exiting Admin Menu.")
                break

            else:
                print("Invalid choice. Please try again.")

            cursor.close()
            connection.close()

        elif user_type == "user":
            print("\n--- User/Staff Menu ---")
            print("1. Booking Room")
            print("2. Billing and Payment (CheakOut)")
            print("3. Check Vacant Rooms")
            print("4. Exit")
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                connection = database_connection.connect_to_database()
                if connection:
                    cursor = connection.cursor()
                    try:
                        admin_User_functions.book_room()

                    except mysql.connector.Error as e:
                        print("Database error:", e)
                    finally:
                        cursor.close()
                        connection.close()

            elif choice == '2':
                admin_User_functions.generate_bill(user_type)
            elif choice == '3':
                admin_User_functions.check_vacant_rooms()
            elif choice == '4':
                print("Exiting User Menu.")
                break
            else:
                print("Invalid choice. Please try again.")


# Create database only once at the start
connection2.create_database_if_not_exists()  # Moved here from database_connection.connect_to_database()

# Now connect to the existing database
connection = database_connection.connect_to_database()
if connection:
    print("Connected to the database successfully!")  # This will print ONCE
    database_connection.create_tables()
    admin_User_functions.login()
    connection.close()
else:
    print("Unable to connect to the database. Please check your XAMPP settings.")