-- Drop the database if it exists to start fresh
DROP DATABASE IF EXISTS request;

CREATE DATABASE request;

USE request;

CREATE TABLE request (
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

-- Create the requestlogs table
CREATE TABLE requestlogs (
    log_id INT AUTO_INCREMENT NOT NULL,
    rid INT NOT NULL,  -- Foreign key to the request ID
    previous_status ENUM('Pending', 'Approved', 'Rejected', 'Withdrawn') NOT NULL,  -- Old status before the change
    updated_by INT NULL,  -- Who updated the status (NULL if the previous status was Pending)
    new_additional_reason TEXT NULL,  -- New additional reason for the status change
    status_changedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,  -- Timestamp of the update
    PRIMARY KEY (log_id),
    CONSTRAINT fk_request_id FOREIGN KEY (rid) REFERENCES request (rid) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_updated_by_logs FOREIGN KEY (updated_by) REFERENCES employee.employee (Staff_ID) ON DELETE SET NULL ON UPDATE CASCADE
);
