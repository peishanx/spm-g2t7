CREATE DATABASE IF NOT EXISTS request;
USE request;

CREATE TABLE IF NOT EXISTS request (
    rid INT AUTO_INCREMENT NOT NULL,
    sid INT NOT NULL,
    request_date DATE NOT NULL,
    wfh_type VARCHAR(50) NOT NULL, 
    reason TEXT NOT NULL,
    attachment VARCHAR(255),
    approved_wfh INT DEFAULT 0,  -- counting approvals
    approved_by VARCHAR(100),
    status ENUM('Pending', 'Approved', 'Rejected', 'Withdrawn') DEFAULT 'Pending',
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (rid),
    CONSTRAINT fk_employee_sid FOREIGN KEY (sid) REFERENCES employee.employee (Staff_ID) ON DELETE CASCADE ON UPDATE CASCADE
);
