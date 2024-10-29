-- Drop the database if it exists to start fresh
DROP DATABASE IF EXISTS employee_leaves;

-- Create the database
CREATE DATABASE employee_leaves;

-- Use the newly created database
USE employee_leaves;

-- Creating the employee_leave table
CREATE TABLE employee_leave (
    Staff_ID INT NOT NULL,                       -- Primary Key for staff
    Staff_FName VARCHAR(50) NOT NULL,           -- First Name
    Staff_LName VARCHAR(50) NOT NULL,           -- Last Name
    Leave_Date DATE NOT NULL,                    -- Leave Date
    Dept VARCHAR(50) NOT NULL,                   -- Department the staff belongs to
    Position VARCHAR(50) NOT NULL,               -- Position in the organization
    Role INT NOT NULL CHECK (Role IN (1, 2, 3)), -- Role: Manager(1), Staff(2), HR(3)
    PRIMARY KEY (Staff_ID, Leave_Date),         -- Composite Primary Key on Staff_ID and Leave_Date
    CONSTRAINT fk_staff FOREIGN KEY (Staff_ID) 
        REFERENCES employee.employee(Staff_ID) ON DELETE CASCADE ON UPDATE CASCADE
);