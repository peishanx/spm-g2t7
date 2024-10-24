-- Drop the database if it exists to start fresh
DROP DATABASE IF EXISTS request;

CREATE DATABASE IF NOT EXISTS request;

USE request;

CREATE TABLE IF NOT EXISTS request (
    rid INT AUTO_INCREMENT NOT NULL,
    sid INT NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    request_date DATE NOT NULL,
    wfh_type VARCHAR(50) NOT NULL, 
    reason TEXT NOT NULL,
    attachment VARCHAR(255),
    status ENUM('Pending', 'Approved', 'Rejected', 'Withdrawn') DEFAULT 'Pending',
    updated_by int,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    additional_reason TEXT,
    PRIMARY KEY (rid),
    CONSTRAINT fk_employee_sid FOREIGN KEY (sid) REFERENCES employee.employee (Staff_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_updated_by FOREIGN KEY (updated_by) REFERENCES employee.employee (Staff_ID) ON DELETE SET NULL ON UPDATE CASCADE

);
