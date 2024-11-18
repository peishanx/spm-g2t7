# IS212: Solution Product Management: spm-g2t7

## Requirements
```
- Docker Desktop
- Able to read english to follow the instructions below 
```

## Project Setup:
Please follow the instructions below before running the files:

* Clone the repository:
git clone https://github.com/peishanx/spm-g2t7.git
cd wfh-request-system
* Install dependencies: 
pip install -r requirements.txt
* Start the Flask server:
flask run
* Access the application: Open http://localhost:8000 in your browser to view the application

## Access the application:
On the file directory of the project, do the following:
```
$ docker compose build
$ docker compose up
```

Note: 
DO NOT RUN ‘docker compose down -d’ on command prompt after seeing the 7 services. 
Run ‘docker compose down’ instead.

## Project Setup  (Local Version - Using WAMP):
Please follow the instructions below before running the files:

* Clone the repository:
git clone https://github.com/peishanx/spm-g2t7.git
cd wfh-request-system
* Install dependencies: 
pip install -r requirements.txt
* Start the Flask server:
flask run
* Access the application: Open http://localhost:8000 in your browser to view the application

## Access the application:
1. Open http://localhost:8000 in your browser to view the application
2. In the project root directory, navigate to database/unhashed_passwords.csv.
    a. This CSV file contains employee details, including: Department, Position, Country, Email, Role, Unhashed Password, Approval Count, and Reporting Manager.
3. At the Login Page, key in the employee's email and password found in the csv file.
4. After successful login, you will be brought to the requests page. 
5. Start navigating to apply for WFH request
6. Fill in the form for WFH request
7. Submit the form
8. WFH request is reflected and seen to be 'Pending'
9. Login as this Employee's manager (login details can be found from csv file)
10. Navigate to Team Requests to approve/reject this request
11. Upon approval/rejection, WFH request status is updated accordingly on Employee's end
12. Log out of both accounts

## Project Setup (Containerized Version - Dockers):
Please follow the instructions below before running the files:

* Clone the repository:
git clone https://github.com/peishanx/spm-g2t7.git
cd wfh-request-system

* On the file directory of the project, do the following to build and start the containers:
```
$ docker-compose build
$ docker-compose up
```

* In Dockers App, check if all 7 containers are built and running.

* Note: 
If any containers are not built/running, do the following:
```
$ docker-compose down –rmi all
$ docker-compose down -v
$ docker-compose build
$ docker-compose up
```
If minimal codes are updated, re-run the containers individually:
```
$ docker-compose up -d --build (foldername of the updated file)
```
Containers:
1. spm-database
    - Files in the database folder
2. spm-frontend
    - Files in the frontend folder
3. spm-employee
    - Files in the simple_microservice/employee folder
4. spm-request
    - Files in the simple_microservice/request folder
5. spm-employee_leaves
    - Files in the simple_microservice/employee folder
    - Files in the simple_microservice/request folder
6. spm-notification
    - Files in the simple_microservice/notification folder

* Eg. Updated code in WFHRequestDetails.html
    - Run:
        ```
        $ docker-compose up -d --build frontend
        ```

## Access the application:
1. Open http://localhost:8000 in your browser to view the application
2. Go to dockers app, click into spm-employee container
3. Navigate to: Files → usr → src → app → unhashed_passwords.csv.
    a. Right-click and save the unhashed_passwords.csv file for easier access.
        i. This CSV file contains employee details, including: Department, Position, Country, Email, Role, Unhashed Password, Approval Count, and Reporting Manager.
4. At the Login Page, key in the employee's email and password found in the csv file.
5. After successful login, you will be brought to the requests page. 
6. Start navigating to apply for WFH request
7. Fill in the form for WFH request
8. Submit the form
9. WFH request is reflected and seen to be 'Pending'
10. ogin as this Employee's manager (login details can be found from csv file)
11. Navigate to Team Requests to approve/reject this request
12. Upon approval/rejection, WFH request status is updated accordingly on Employee's end
13. Log out of both accounts

## Project Setup (Deployed Version - Dockers, Release Share):
Please follow the instructions below before running the files:

* Clone the repository:
git clone https://github.com/peishanx/spm-g2t7.git
cd wfh-request-system

* On the file directory of the project, do the following to build and start the containers:
```
$ docker-compose build
$ docker-compose up
```

* In Dockers App, check if all 7 containers are built and running.

* Note: 
If any containers are not built/running, do the following:
```
$ docker-compose down –rmi all
$ docker-compose down -v
$ docker-compose build
$ docker-compose up
```
If minimal codes are updated, re-run the containers individually:
```
$ docker-compose up -d --build (foldername of the updated file)
```
Containers:
1. spm-database
    - Files in the database folder
2. spm-frontend
    - Files in the frontend folder
3. spm-employee
    - Files in the simple_microservice/employee folder
4. spm-request
    - Files in the simple_microservice/request folder
5. spm-employee_leaves
    - Files in the simple_microservice/employee folder
    - Files in the simple_microservice/request folder
6. spm-notification
    - Files in the simple_microservice/notification folder

* Eg. Updated code in WFHRequestDetails.html
    - Run:
        ```
        $ docker-compose up -d --build frontend
        ```
## Access the application:
1. Open Docker Desktop and go to the 'Extensions' section.
2. Download the 'Release Share' extension.
3. You will see 7 containers running. Find the spm-frontend container.
4. Click on the 'Connect' button. A public URL will appear next to it (eg. https://spmg2t7.rshare.io/ )
5. Click on the public URL to access the Login Page.
6. Go to dockers app, click into spm-employee container
    a. Navigate to: Files → usr → src → app → unhashed_passwords.csv.
    b. Right-click and save the unhashed_passwords.csv file for easier access.
    c. This CSV file contains employee details, including: Department, Position, Country, Email, Role, Unhashed Password, Approval Count, and Reporting Manager.
7. At the Login Page, key in the employee's email and password found in the csv file.
8. After successful login, you will be brought to the requests page. 
9. Start navigating to apply for WFH request
10. Fill in the form for WFH request
11. Submit the form
12. WFH request is reflected and seen to be 'Pending'
13. Login as this Employee's manager (login details can be found from csv file)
14. Navigate to Team Requests to approve/reject this request
15. Upon approval/rejection, WFH request status is updated accordingly on Employee's end
16. Log out of both accounts



# Service Overview

## Backstory
With the growing adoption of remote work, organizations have faced increasing administrative challenges in managing work-from-home (WFH) requests. Manual tracking can lead to delays, miscommunications, and lost requests, disrupting the productivity and morale of employees. This project was initiated to address these pain points by providing a centralized, automated system for WFH request submissions, approval processes, and notifications. This ensures that requests are tracked accurately and processed efficiently, allowing employees to focus on their work without administrative hassles and managers to gain better oversight and control of the WFH process.

## Solution
Our application provides a streamlined, automated solution for managing work-from-home requests. Employees submit their requests with necessary details and attachments, and the system organizes these for easy tracking. Managers can review each request and decide to approve or reject it. The solution includes an integrated notification system, which ensures that employees and managers receive timely email updates at each stage, from submission to final approval. By reducing manual effort and improving communication, the system creates a seamless experience, making it easy to keep accurate records and ensuring that everyone stays informed throughout the process.

## Features
* Dynamic User Views: Depending on the kind of employee, the employee will be shown different views and allowed different kinds of actions.
* User-Friendly Request Submission: Employees can submit WFH requests with all necessary details, including request dates, reasons, and document attachments.
* Manager Approval Workflow: Managers can review submitted requests, see attached files, and approve or reject requests based on provided information.
* Automated Notifications: Email notifications are sent at key stages to keep both employees and managers informed without manual follow-up.
* Secure File Handling: Uploaded files are securely stored, ensuring data protection and privacy.
* Detailed Logging and Error Handling: The system captures logs for troubleshooting and ensures that errors are communicated to the user effectively.

## Benefits
* Efficiency: Automates the entire WFH request process, reducing the time spent on manual submissions, follow-ups, and approvals.
* Improved Communication: Real-time notifications keep employees and managers updated, minimizing the need for repeated inquiries and improving transparency.
* Enhanced Record-Keeping: All requests, reasons, and supporting documents are securely stored, allowing for easy retrieval and accurate tracking.
* Streamlined Approval Workflow: Managers have a straightforward platform to review and manage requests, allowing them to make quick, informed decisions.
* Employee Satisfaction: By simplifying the WFH request process, employees can focus more on their work and experience greater convenience and clarity.

## How to test the application
 + Login with Employee Email using the email found in from employee.sql
 + Start navigating to apply for WFH request
 + Fill in the form for WFH request
 + Submit the form
 + WFH request is reflected and seen to be 'Pending'
 + Login as this Employee's manager(can be found from employee.sql)
 + Navigate to Team Requests to approve/reject this request
 + Upon approval/rejection, WFH request status is updated accordingly on Employee's end
 Log Out of both accounts

## Technologies Used
* Backend: Python with Flask framework
* Frontend: HTML, CSS, JavaScript (for form submissions and display)
* Database: SQLite or PostgreSQL for storing WFH request data
* Notifications: Nodemailer for automated email notifications
* File Handling: Secure file upload and storage for supporting documents

## Usage
* Submitting a WFH Request: Employees fill out the form, provide relevant details and request dates, and submit their WFH request.

* Manager Review: Managers can view all submitted requests, check details, review attachments, and make an approval decision.

* Notification Handling: Notifications are sent at each step, keeping employees informed of the status of their requests.

## Future Enhancements
* Multi-Level Approval: Adding support for multi-level approvals to accommodate organizations with complex workflows.
* Integration with HR Systems: Syncing with HR systems for seamless data management.
* Dashboard: Adding a dashboard for analytics and insights into WFH request trends.