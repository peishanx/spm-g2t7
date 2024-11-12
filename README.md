# IS212: Solution Product Management: spm-g2t7

## Requirements
```
- Docker Desktop
- Able to read english to follow the instructions below 
```

## Project Setup
Please follow the instructions below before running the files:

* Clone the repository:
git clone https://github.com/peishanx/spm-g2t7.git
cd wfh-request-system
* Install dependencies: 
pip install -r requirements.txt
* Start the Flask server:
flask run
* Access the application: Open http://localhost:8000 in your browser to view the application

## How to Run
On the file directory of the project, do the following:
```
$ docker compose build
$ docker compose up
```

Note: 
DO NOT RUN ‘docker compose down -d’ on command prompt after seeing the 7 services. 
Run ‘docker compose down’ instead.

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