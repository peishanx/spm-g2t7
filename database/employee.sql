create database employee;
use employee;
CREATE TABLE employee (
	sid int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    staff_fname varchar(50) not null,
    staff_lname varchar(50) not null,
    dept varchar(50) not null,
    position varchar(50) not null,
    country varchar(50) not null,
	email varchar(250) unique not null,
    reporting_manager int not null,
    role int not null,
    constraint primary key (sid),
    constraint foreign key (reporting_manager)
);


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
('Olivia', 'Davis', 'IT', 'IT Manager', 'Singapore', 'oliviadavis@example.com', 13, 1);

INSERT INTO employee (staff_fname, staff_lname, dept, position, country, email, reporting_manager, role)
VALUES
('Alex', 'Miller', 'Sales', 'Sales Director', 'USA', 'alexmiller@example.com', 0, 1),  -- Alex is the head of Sales (reporting_manager = 0 as no higher manager)
('Laura', 'Johnson', 'Consult', 'Consulting Director', 'Canada', 'laurajohnson@example.com', 0, 1),  -- Laura is the head of Consulting
('Brian', 'Evans', 'System solutioning', 'System Solutions Director', 'UK', 'brianevans@example.com', 0, 1),  -- Brian is head of System Solutions
('Chloe', 'Martinez', 'HR and Admin', 'HR Director', 'Singapore', 'chloemartinez@example.com', 0, 1),  -- Chloe is head of HR and Admin
('Daniel', 'Harris', 'Finance', 'Finance Director', 'Australia', 'danielharris@example.com', 0, 1),  -- Daniel is head of Finance
('Nina', 'Turner', 'IT', 'IT Director', 'Singapore', 'ninaturner@example.com', 0, 1);  -- Nina is head of IT

