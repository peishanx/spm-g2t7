import pandas as pd
import mysql.connector
from mysql.connector import Error

# Read the CSV file
df = pd.read_csv('/Applications/MAMP/htdocs/IS212/spm-g2t7/database/employeenew.csv')  # Replace with the actual CSV file path

# Establish a database connection
conn = mysql.connector.connect(
    host="localhost",     # Update as per your host
    user="root",          # Update with your MySQL username
    password="root",      # Update with your MySQL password
    database="employee"   # Ensure the database is created
)

cursor = conn.cursor()

# First, insert the employees who don't have a Reporting_Manager that exists yet
remaining_rows = df.copy()  # Copy of the dataframe to track remaining rows

while not remaining_rows.empty:  # Keep iterating until all rows are inserted
    initial_count = len(remaining_rows)

    for index, row in remaining_rows.iterrows():
        try:
            # Check if Reporting_Manager already exists in the database or not
            cursor.execute("SELECT COUNT(*) FROM employee WHERE Staff_ID = %s", (row['Reporting_Manager'],))
            (manager_exists,) = cursor.fetchone()

            if manager_exists or row['Staff_ID'] == row['Reporting_Manager']:  # Insert if manager exists or it's a top-level manager
                sql = """
                INSERT INTO employee (Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    row['Staff_ID'], row['Staff_FName'], row['Staff_LName'], row['Dept'],
                    row['Position'], row['Country'], row['Email'], row['Reporting_Manager'], row['Role']
                )
                cursor.execute(sql, values)

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

