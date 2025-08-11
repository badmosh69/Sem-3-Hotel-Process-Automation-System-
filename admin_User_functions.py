import mysql.connector
import database_connection
from datetime import datetime



# Check Vacant Rooms
def check_vacant_rooms():
    # this is all i know ok ?s
    
    """Display all vacant rooms."""
    connection = database_connection.connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT room_no, type, price FROM rooms WHERE status = TRUE")
            rooms = cursor.fetchall()
            if rooms:
                print("Vacant Rooms:")
                for room in rooms:
                    print(f"Room No: {room[0]}, Type: {room[1]}, Price: {room[2]}")
            else:
                print("No vacant rooms available.")
        except mysql.connector.Error as e:
            print("Error retrieving vacant rooms:", e)
        finally:
            cursor.close()
            connection.close()

# Generate Bill
from decimal import Decimal
import mysql.connector 
from decimal import Decimal

def generate_bill(user_type):
    """Generate bill for a customer using contact number."""
    connection = database_connection.connect_to_database()
    if not connection:
        print("Database connection error.")
        return

    cursor = connection.cursor()
    try:
        # Get contact number instead of customer ID
        contact = input("Enter customer's contact number (10 digits): ").strip()
        if not validate_contact(contact):
            print("Invalid contact number!")
            return

        # Fetch all billable bookings for this contact (include cust_id in SELECT)
        cursor.execute("""
            SELECT b.book_id, b.room_no, r.price, b.check_in, b.check_out, c.cust_id
            FROM booking b
            JOIN rooms r ON b.room_no = r.room_no
            JOIN customer c ON b.cust_id = c.cust_id
            WHERE c.contact = %s AND b.bill_no IS NULL
        """, (contact,))
        
        bookings = cursor.fetchall()

        if not bookings:
            print("No pending bills found for this contact number.")
            return

        # Display all billable bookings
        print("\nPending bookings for contact", contact)
        print("Booking ID | Room No | Check-in     | Check-out    | Price/day")
        print("----------------------------------------------------------------------")
        for idx, booking in enumerate(bookings, 1):
            print(f"{booking[0]:9} | {booking[1]:7} | {booking[3]} | {booking[4]} | ₹{booking[2]}")

        # Let user select which booking to bill
        while True:
            try:
                choice = int(input("\nEnter index number of booking to generate bill: "))
                if 1 <= choice <= len(bookings):
                    selected_booking = bookings[choice-1]
                    break
                print("Invalid index number!")
            except ValueError:
                print("Please enter a valid number!")

        # Extract values correctly (added cust_id as 5th element)
        book_id, room_no, base_amount, check_in, check_out, cust_id = selected_booking#{book_id=selected_booking[0]}

        # Calculate days
        no_days = (check_out - check_in).days
        print(f"\nNumber of days stayed: {no_days}")

        # Apply discount if admin
        discount = 0.0
        if user_type == "admin":
            while True:
                discount = float(input("Enter discount percentage (0 for none): "))
                if discount<0 or discount>100:
                    print("Enter again as discount can't be more than 100 or less than 0 ")
                    continue
                else:
                    break

        # Calculate final amount
        discounted_amount = (base_amount - (base_amount * Decimal(discount) / 100)) * no_days

        # Insert bill with correct cust_id
        cursor.execute("""
            INSERT INTO bill (room_no, cust_id, amount)
            VALUES (%s, %s, %s)
        """, (room_no, cust_id, discounted_amount))
        connection.commit()

        # Get generated bill number
        cursor.execute("SELECT LAST_INSERT_ID()")
        bill_no = cursor.fetchone()[0]

        # Update room status and booking
        cursor.execute("UPDATE rooms SET status = TRUE WHERE room_no = %s", (room_no,))
        cursor.execute("UPDATE booking SET bill_no = %s WHERE book_id = %s", (bill_no, book_id))
        connection.commit()

        print(f"\nBill generated successfully!")
        print(f"Bill Number: {bill_no}")
        print(f"Total Amount: ₹{discounted_amount:.2f}")
        print(f"Room {room_no} marked as available")

    except mysql.connector.Error as e:
        print("Database error:", e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
# Login Function
def login():
    """Main login function."""
    import sys
    import main

    while True:
        print("\nWelcome to the system. Please select your role:")
        print("1. Admin")
        print("2. User/Staff")
        print("3. Exit")
        user_choice = input("Select (1/2/3): ")

        if user_choice == "3":
            print("Exiting the system. Goodbye!")
            sys.exit(0) 
            

        user_type = "admin" if user_choice == "1" else "user" if user_choice == "2" else None

        if not user_type:
            print("Invalid option. Please select a valid choice.")
            continue

        username = input(f"Enter your {user_type} ID: ")
        password = input(f"Enter your {user_type} password: ")

        if database_connection.verify_credentials(username, password, user_type):
            print("Login successful!")
            main.menu(user_type)  
        else:
            print("Invalid credentials. Please try again.")

def book_room():
    import main
    
    """Book a room for a customer using extracted details."""
    connection = database_connection.connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Step 1: Image handling with single error check
            while True:
                image_path = input("Please enter the image path or address: ").strip()
                
                try:
                    # Attempt image processing
                    main.extract_text_from_image(image_path)
                    break  # Exit loop if successful
                
                except Exception as e:
                    print(f"\nError processing image: {str(e)}")
                    retry = input("Try again with different image? (y/n): ").lower()
                    if retry != 'y':
                        print("Booking cancelled.")
                        return

            # Step 2: Proceed only if image processed successfully
            customer_data = main.extract_customer_details_from_text_file()
            if not customer_data:
                print("Failed to extract customer details from text file.")
                return

            name = customer_data.get("name")
            dob = customer_data.get("dob")
            gender = customer_data.get("gender")
            address = customer_data.get("address")
            aadhaar = customer_data.get("aadhaar")

            # Validate Aadhaar
            if not (aadhaar.isdigit() and len(aadhaar) == 12):
                print("Invalid Aadhaar number in document. Must be 12 digits.")
                return

            # Contact number validation with retry
            contact = None
            while True:
                contact = input("Enter customer's contact number (10 digits): ").strip()
                if contact.isdigit() and len(contact) == 10:
                    break
                print("Invalid contact number! Must be 10 digits.")
                retry = input("Try again? (y/n): ").lower()
                if retry != 'y':
                    print("Booking cancelled.")
                    return

            # Age validation
            try:
                birth_date = datetime.strptime(dob, "%d/%m/%Y")
                age = (datetime.now() - birth_date).days // 365
                if age < 18:
                    print("Customer must be at least 18 years old.")
                    return
            except ValueError:
                print("Invalid date format in extracted data (required: DD/MM/YYYY).")
                return

            # Check if customer exists via Aadhaar
            cursor.execute("SELECT cust_id FROM customer WHERE aadhaar = %s", (aadhaar,))
            existing_customer = cursor.fetchone()

            if not existing_customer:
                try:
                    # Insert new customer
                    cursor.execute(
                        "INSERT INTO customer (name, age, gender, contact, address, aadhaar) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (name, age, gender, contact, address, aadhaar)
                    )
                    connection.commit()
                    print("New customer registered successfully!")
                    
                    # Get new cust_id
                    cursor.execute("SELECT cust_id FROM customer WHERE aadhaar = %s", (aadhaar,))
                    existing_customer = cursor.fetchone()
                except mysql.connector.Error as e:
                    print("Error saving customer:", e)
                    connection.rollback()
                    return
            elif existing_customer:
                print("Customer already exists in database proceed with booking ")
                
            cust_id = existing_customer[0]
            
            # Get available rooms
            cursor.execute("SELECT room_no, type, price FROM rooms WHERE status = TRUE")
            available_rooms = cursor.fetchall()

            if not available_rooms:
                print("No rooms available for booking.")
                return

            # Display rooms
            print("\nAvailable Rooms:")
            print("Room No | Type            | Price")
            print("----------------------------------")
            for room in available_rooms:
                print(f"{room[0]:<8} | {room[1]:<15} | ₹{room[2]:<8}")

            # Room selection
            while True:
                try:
                    room_no = int(input("\nEnter Room Number: "))
                    if any(room[0] == room_no for room in available_rooms):
                        break
                    print("Invalid room! Choose from available list.")
                except ValueError:
                    print("Invalid input! Enter numbers only.")

            # Date validation
            while True:
                check_in = input("Enter Check-in Date (YYYY-MM-DD): ").strip()
                check_out = input("Enter Check-out Date (YYYY-MM-DD): ").strip()
                
                # Validate date format
                try:
                    check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
                    check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
                except ValueError:
                    print("Invalid date format! Use YYYY-MM-DD.")
                    continue
                
                # Validate check-out after check-in
                if check_out_date <= check_in_date:
                    print("Error: Check-out must be after check-in.")
                    continue
                
                break  # Proceed if valid

                

            # Update room status and create booking
            cursor.execute("UPDATE rooms SET status = FALSE WHERE room_no = %s", (room_no,))
            cursor.execute(
                "INSERT INTO booking (cust_id, room_no, check_in, check_out) "
                "VALUES (%s, %s, %s, %s)",
                (cust_id, room_no, check_in, check_out)
            )
            connection.commit()
            
            print("\nBooking Successful!")
            print(f"Customer ID: {cust_id}")
            print(f"Room {room_no} booked from {check_in} to {check_out}")

        except mysql.connector.Error as e:
            print("Database error:", e)
            connection.rollback()
        except Exception as e:
            print("Unexpected error:", e)
        finally:
            cursor.close()
            connection.close()

def validate_name(name):
    """Validate that the name does not contain numbers."""
    if not name.strip():
        print("Error: Name cannot be empty.")
        return False
    if any(char.isdigit() for char in name):
        print("Error: Name should not contain numbers.")
        return False
    return True

def validate_designation(designation):
    """Validate that the designation does not contain numbers."""
    if not designation.strip():
        print("Error: Designation cannot be empty.")
        return False
    if any(char.isdigit() for char in designation):
        print("Error: Designation should not contain numbers.")
        return False
    return True
def validate_age(age):
    try:
        age = int(age)
        if age < 18 or age > 65:
            print("Error: Age must be between 18 and 65.")
            return False
    except ValueError:
        print("Error: Age must be a number.")
        return False
    return True

def validate_gender(gender):
    if gender.lower() not in ['male', 'female', 'other']:
        print("Error: Gender must be Male, Female, or Other.")
        return False
    return True

def validate_contact(contact):
    if not contact.isdigit() or len(contact) != 10:
        print("Error: Contact number must be exactly 10 digits.")
        return False
    return True

def validate_address(address):
    if not address.strip():
        print("Error: Address cannot be empty.")
        return False
    return True

def validate_shift(shift):
    if shift.lower() not in ['morning', 'evening']:
        print("Error: Shift must be Morning or Evening.")
        return False
    return True

def ask_retry_or_cancel():
    """Ask the user if they want to retry or cancel the operation."""
    while True:
        choice = input("Do you want to try again? (yes/no): ").strip().lower()
        if choice == 'yes':
            return True
        elif choice == 'no':
            return False
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")            