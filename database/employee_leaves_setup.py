import pandas as pd
from sqlalchemy import create_engine

# Load the CSV file
csv_file_path = 'employees_with_leave_dates.csv'  # Update this with the correct path
employees_df = pd.read_csv(csv_file_path)

# Create a database connection
# For MySQL
engine = create_engine('mysql+mysqlconnector://root:@localhost/employee_leaves')


# Insert data into the employee_leave table
employees_df.to_sql('employee_leave', con=engine, if_exists='append', index=False)

print("Data inserted successfully!")
