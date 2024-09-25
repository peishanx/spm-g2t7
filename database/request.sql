CREATE DATABASE request;
USE request;

CREATE TABLE request (
    rid INT NOT NULL AUTO_INCREMENT,
    sid INT NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    type varchar(50) not null,
    checkout_session_id VARCHAR(70),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (rid),
    CONSTRAINT fk_employee_sid FOREIGN KEY (sid) REFERENCES employee (sid)
);



