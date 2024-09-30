import pandas as pd
import mysql.connector
from mysql.connector import Error
import random
import string
import bcrypt  # Import bcrypt for password hashing

# Function to generate a random password
def generate_password(length=8):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# Function to hash the password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Read the CSV file
df = pd.read_csv(r'C:\wamp64\www\spm-g2t7\database\employeenew.csv')  # Update your own path here
print(df.columns)  # Check the columns in the DataFrame

# Create a list to store employee data with unhashed passwords for CSV output
unhashed_passwords = []

try:
    # Establish a connection without specifying the database to create it
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""  # Your MySQL root password, update if needed
    )

    cursor = conn.cursor()

    # Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS employee")
    print("Database 'employee' created or already exists.")

    # Connect to the created 'employee' database
    conn.database = "employee"

    # Create the employee table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee (
        Staff_ID INT PRIMARY KEY,
        Staff_FName VARCHAR(50),
        Staff_LName VARCHAR(50),
        Dept VARCHAR(50),
        Position VARCHAR(50),
        Country VARCHAR(50),
        Email VARCHAR(100),
        Reporting_Manager INT,
        Role VARCHAR(50),
        Password VARCHAR(255),  -- Add Password column
        FOREIGN KEY (Reporting_Manager) REFERENCES employee(Staff_ID)
    )
    """)
    print("Table 'employee' created or already exists.")

    # First, insert the employees who don't have a Reporting_Manager that exists yet
    remaining_rows = df.copy()  # Copy of the dataframe to track remaining rows

    while not remaining_rows.empty:  # Keep iterating until all rows are inserted
        initial_count = len(remaining_rows)

        for index, row in remaining_rows.iterrows():
            try:
                # Check if the Staff_ID already exists in the database
                cursor.execute("SELECT COUNT(*) FROM employee WHERE Staff_ID = %s", (row['Staff_ID'],))
                (staff_exists,) = cursor.fetchone()

                if not staff_exists:  # Only insert if the Staff_ID does not exist
                    # Check if Reporting_Manager already exists in the database or not
                    cursor.execute("SELECT COUNT(*) FROM employee WHERE Staff_ID = %s", (row['Reporting_Manager'],))
                    (manager_exists,) = cursor.fetchone()

                    if manager_exists or row['Staff_ID'] == row['Reporting_Manager']:  # Insert if manager exists or it's a top-level manager
                        sql = """
                        INSERT INTO employee (Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role, Password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        password = generate_password()  # Generate a unique password
                        hashed_password = hash_password(password)  # Hash the password before inserting it into the database
                        values = (
                            row['Staff_ID'], row['Staff_FName'], row['Staff_LName'], row['Dept'],
                            row['Position'], row['Country'], row['Email'], row['Reporting_Manager'], row['Role'],
                            hashed_password.decode('utf-8')  # Store the hashed password as a string
                        )
                        cursor.execute(sql, values)

                        # Store the unhashed password along with employee info in the unhashed_passwords list
                        unhashed_passwords.append({
                            'Staff_ID': row['Staff_ID'],
                            'Staff_FName': row['Staff_FName'],
                            'Staff_LName': row['Staff_LName'],
                            'Dept': row['Dept'],
                            'Position': row['Position'],
                            'Country': row['Country'],
                            'Email': row['Email'],
                            'Reporting_Manager': row['Reporting_Manager'],
                            'Role': row['Role'],
                            'Unhashed_Password': password  # Store the plain-text password
                        })

                        # Drop the inserted row from the remaining_rows dataframe
                        remaining_rows = remaining_rows.drop(index)

            except Error as e:
                print(f"Error inserting employee row {row['Staff_ID']}: {e}")

        # If no rows were inserted in this iteration, there's a problem with foreign key dependencies
        if len(remaining_rows) == initial_count:
            print("Circular dependency detected. Remaining rows could not be inserted due to missing Reporting_Manager references.")
            break

    # Commit the transaction after inserting all rows
    conn.commit()
    print("Data insertion completed.")

    # Save the unhashed passwords to a CSV file, including additional columns
    unhashed_passwords_df = pd.DataFrame(unhashed_passwords)
    unhashed_passwords_df.to_csv(r'C:\wamp64\www\spm-g2t7\database\unhashed_passwords.csv', index=False)
    print("Unhashed passwords saved to CSV file.")

except Error as e:
    print(f"Error: {e}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("MySQL connection is closed.")
