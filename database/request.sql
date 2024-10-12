CREATE DATABASE IF NOT EXISTS request;
USE request;

CREATE TABLE IF NOT EXISTS request (
    rid INT AUTO_INCREMENT NOT NULL,
    sid INT NOT NULL,
    request_date DATE NOT NULL,
    wfh_type VARCHAR(50) NOT NULL,  -- Changed from 'type' to 'wfh_type'
    reason TEXT NOT NULL,
    attachment VARCHAR(255),
    approved_wfh INT DEFAULT 0,  -- Assuming this field is for counting approvals
    approved_by VARCHAR(100),
    status ENUM('Pending', 'Approved', 'Rejected', 'Withdrawn') DEFAULT 'Pending',
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (rid),
    CONSTRAINT fk_employee_sid FOREIGN KEY (sid) REFERENCES employee.employee (Staff_ID) ON DELETE CASCADE ON UPDATE CASCADE
);



-- CREATE DATABASE request;
-- USE request;

-- CREATE TABLE request (
--     rid INT NOT NULL AUTO_INCREMENT,
--     sid INT NOT NULL,
--     type VARCHAR(50) NOT NULL,
--     status VARCHAR(50) DEFAULT 'Pending',
--     createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
--     PRIMARY KEY (rid),  -- Primary Key should only be on 'rid'
--     CONSTRAINT fk_employee_sid FOREIGN KEY (sid) REFERENCES employee.employee (Staff_ID) ON DELETE CASCADE ON UPDATE CASCADE  -- Foreign key constraint on 'sid'
-- );
-- ALTER TABLE request
-- ADD COLUMN attachment VARCHAR(255);