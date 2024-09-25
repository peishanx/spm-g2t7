-- Drop the database if it exists to start fresh
DROP DATABASE IF EXISTS employee;

-- Create the database
CREATE DATABASE employee;

-- Use the newly created database
USE employee;

-- Creating the employee table
CREATE TABLE employee (
    Staff_ID int NOT NULL,  -- Primary Key for staff
    Staff_FName varchar(50) NOT NULL,      -- First Name
    Staff_LName varchar(50) NOT NULL,      -- Last Name
    Dept varchar(50) NOT NULL,             -- Department the staff belongs to
    Position varchar(50) NOT NULL,         -- Position in the organization
    Country varchar(50) NOT NULL,          -- Country located
    Email varchar(50) NOT NULL UNIQUE,     -- Unique Email Address
    Reporting_Manager int,                 -- Foreign Key for Reporting Manager
    Role int NOT NULL CHECK (Role IN (1, 2, 3)),  -- Role: HR(1), Staff(2), Manager(3)
    PRIMARY KEY (Staff_ID),                -- Primary Key on Staff_ID
    CONSTRAINT fk_reporting_manager FOREIGN KEY (Reporting_Manager) 
        REFERENCES employee(Staff_ID) ON DELETE SET NULL ON UPDATE CASCADE
);


