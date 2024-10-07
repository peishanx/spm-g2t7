CREATE DATABASE request;
USE request;

CREATE TABLE request (
    rid INT NOT NULL AUTO_INCREMENT,
    sid INT NOT NULL,
    type varchar(50) not null,
    status VARCHAR(50) DEFAULT 'Pending',
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (rid,Staff_ID),
    CONSTRAINT fk_employee_sid FOREIGN KEY (sid) REFERENCES employee (Staff_ID)
);



