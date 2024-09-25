-- Creating the database and setting it as the active database
CREATE DATABASE employee;
USE employee;

-- Creating the employee table
CREATE TABLE employee (
    sid int NOT NULL AUTO_INCREMENT,
    staff_fname varchar(50) NOT NULL,
    staff_lname varchar(50) NOT NULL,
    dept varchar(50) NOT NULL,
    position varchar(50) NOT NULL,
    country varchar(50) NOT NULL,
    email varchar(250) UNIQUE NOT NULL,
    reporting_manager int,  -- Changed to allow NULL for top positions
    role int NOT NULL,
    PRIMARY KEY (sid),
    CONSTRAINT fk_reporting_manager FOREIGN KEY (reporting_manager) REFERENCES employee(sid)
);

-- Inserting values into the employee table
-- For heads of departments, reporting_manager is set to NULL
INSERT INTO employee (staff_fname, staff_lname, dept, position, country, email, reporting_manager, role)
VALUES
('John', 'Doe', 'Sales', 'Sales Executive', 'USA', 'johndoe@example.com', 1, 2),
('Jane', 'Smith', 'Sales', 'Sales Manager', 'Canada', 'janesmith@example.com', 3, 1),
('Paul', 'Brown', 'Consult', 'Consultant', 'UK', 'paulbrown@example.com', 5, 2),
('Emily', 'White', 'Consult', 'Senior Consultant', 'Australia', 'emilywhite@example.com', 6, 1),
('Michael', 'Green', 'System solutioning', 'Systems Engineer', 'Singapore', 'michaelgreen@example.com', 7, 2),
('Sara', 'Blue', 'System solutioning', 'Solutions Architect', 'India', 'sarablue@example.com', 8, 1),
('Robert', 'Taylor', 'HR and Admin', 'HR Executive', 'New Zealand', 'roberttaylor@example.com', 4, 3),
('Sophia', 'Lee', 'HR and Admin', 'HR Manager', 'USA', 'sophialee@example.com', 9, 1),
('Mark', 'Adams', 'Finance', 'Finance Analyst', 'UK', 'markadams@example.com', 10, 2),
('Isabella', 'Clark', 'Finance', 'Finance Manager', 'Canada', 'isabellaclark@example.com', 11, 1),
('James', 'Wilson', 'IT', 'IT Support', 'Australia', 'jameswilson@example.com', 12, 2),
('Olivia', 'Davis', 'IT', 'IT Manager', 'Singapore', 'oliviadavis@example.com', 13, 1),
('Alex', 'Miller', 'Sales', 'Sales Director', 'USA', 'alexmiller@example.com', NULL, 1),
('Laura', 'Johnson', 'Consult', 'Consulting Director', 'Canada', 'laurajohnson@example.com', NULL, 1),
('Brian', 'Evans', 'System solutioning', 'System Solutions Director', 'UK', 'brianevans@example.com', NULL, 1),
('Chloe', 'Martinez', 'HR and Admin', 'HR Director', 'Singapore', 'chloemartinez@example.com', NULL, 1),
('Daniel', 'Harris', 'Finance', 'Finance Director', 'Australia', 'danielharris@example.com', NULL, 1),
('Nina', 'Turner', 'IT', 'IT Director', 'Singapore', 'ninaturner@example.com', NULL, 1);
