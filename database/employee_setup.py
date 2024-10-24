import pandas as pd
import mysql.connector
from mysql.connector import Error
import random
import string
import bcrypt
import os

# Function to generate a random password
def generate_password(length=8):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

# Function to hash the password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Read the CSV file with a configurable path
csv_path = os.getenv('CSV_PATH', r'employeenew.csv')
df = pd.read_csv(csv_path)
print(df.columns)

# Create a list to store employee data with unhashed passwords for CSV output
unhashed_passwords = []

try:
    # Establish a connection without specifying the database to create it
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '')  # Use environment variables for better security
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
    Staff_ID INT NOT NULL,
    Staff_FName VARCHAR(50) NOT NULL,
    Staff_LName VARCHAR(50) NOT NULL,
    Dept VARCHAR(50) NOT NULL,
    Position VARCHAR(50) NOT NULL,
    Country VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Reporting_Manager INT,
    Role VARCHAR(50),
    Password VARCHAR(255),
    approval_count INT DEFAULT 0,
    PRIMARY KEY (Staff_ID),
    FOREIGN KEY (Reporting_Manager) REFERENCES employee(Staff_ID)
    ON DELETE SET NULL ON UPDATE CASCADE
    )ENGINE=InnoDB;
    """)
    print("Table 'employee' created or already exists.")

    # Insert top-level managers first (employees with no Reporting_Manager)
    top_level_managers = df[df['Reporting_Manager'].isna() | (df['Staff_ID'] == df['Reporting_Manager'])]
    for index, row in top_level_managers.iterrows():
        password = generate_password()
        hashed_password = hash_password(password)
        values = (
            row['Staff_ID'], row['Staff_FName'], row['Staff_LName'], row['Dept'],
            row['Position'], row['Country'], row['Email'], None, row['Role'], 
            hashed_password.decode('utf-8'),row['approval_count']
        )
        cursor.execute("""
        INSERT INTO employee (Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role, Password,approval_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, values)

        unhashed_passwords.append({
            'Staff_ID': row['Staff_ID'],
            'Staff_FName': row['Staff_FName'],
            'Staff_LName': row['Staff_LName'],
            'Dept': row['Dept'],
            'Position': row['Position'],
            'Country': row['Country'],
            'Email': row['Email'],
            'Role': row['Role'],
            'Unhashed_Password': password,
            'approval_count':row['approval_count']
        })

    # Insert remaining employees with Reporting_Manager
    remaining_rows = df[~df.index.isin(top_level_managers.index)]

    while not remaining_rows.empty:
        initial_count = len(remaining_rows)

        for index, row in remaining_rows.iterrows():
            try:
                # Check if Reporting_Manager exists in the database
                cursor.execute("SELECT COUNT(*) FROM employee WHERE Staff_ID = %s", (row['Reporting_Manager'],))
                (manager_exists,) = cursor.fetchone()

                if manager_exists or row['Staff_ID'] == row['Reporting_Manager']:  # Insert if manager exists or it's a top-level manager
                    password = generate_password()
                    hashed_password = hash_password(password)
                    values = (
                        row['Staff_ID'], row['Staff_FName'], row['Staff_LName'], row['Dept'],
                        row['Position'], row['Country'], row['Email'], row['Reporting_Manager'], row['Role'],
                        hashed_password.decode('utf-8'),row['approval_count']
                    )
                    cursor.execute("""
                    INSERT INTO employee (Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role, Password,approval_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, values)

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
                        'Unhashed_Password': password,
                        'approval_count':row['approval_count']
                    })

                    # Drop the inserted row from the remaining_rows dataframe
                    remaining_rows = remaining_rows.drop(index)

            except Error as e:
                print(f"Error inserting employee row {row['Staff_ID']}: {e}")

        if len(remaining_rows) == initial_count:
            print("Circular dependency detected. Remaining rows could not be inserted due to missing Reporting_Manager references.")
            break

    # Commit the transaction after inserting all rows
    conn.commit()
    print("Data insertion completed.")

    # Save the unhashed passwords to a CSV file, including additional columns, with improved security
    unhashed_passwords_path = os.getenv('UNHASHED_PASSWORDS_PATH', r'unhashed_passwords.csv')
    unhashed_passwords_df = pd.DataFrame(unhashed_passwords)
    unhashed_passwords_df.to_csv(unhashed_passwords_path, index=False)
    print("Unhashed passwords saved to CSV file.")

except Error as e:
    print(f"Error: {e}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("MySQL connection is closed.")