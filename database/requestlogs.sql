DROP DATABASE IF EXISTS request;

USE request;

CREATE TABLE IF NOT EXISTS requestlogs (
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
