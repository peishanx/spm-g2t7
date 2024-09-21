create database request;
use request;

CREATE TABLE request (
    rid INT NOT NULL AUTO_INCREMENT,
    sid INT NOT NULL,
    status VARCHAR(50) default "Pending",
    checkout_session_id VARCHAR(70),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT PRIMARY KEY (rid, sid),
    CONSTRAINT FOREIGN KEY (sid) REFERENCES employee.employee (sid),
);

