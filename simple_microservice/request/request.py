from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timedelta, timezone, time
import os
import sys
from werkzeug.utils import secure_filename
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(environ.get("RABBIT_URL"), heartbeat=0, blocked_connection_timeout=300))
channel = connection.channel()


#Request db
app = Flask(__name__)
# CORS(app, resources={r"/request/*": {"origins": "http://spm-frontend:8000"}})

# Primary database URI for the request microservice
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("request_dbURL") or "mysql+mysqlconnector://root:example@database:3306/request"
# app.config["SQLALCHEMY_BINDS"] = {
#     'employee_db': environ.get("employee_dbURL")
# }

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 299}
app.config['UPLOAD_FOLDER'] = 'uploads'  # Define where to store uploaded attachment files for form submission


db = SQLAlchemy(app)

CORS(app)

# Correct the EMPLOYEE_URL to include the /employee endpoint
EMPLOYEE_URL = os.environ.get("EMPLOYEE_URL") or "http://localhost:5100/employee"

#Request table
class Request(db.Model):
    __tablename__ = "request"

    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sid = db.Column(db.Integer, nullable=False)
    createdAt = db.Column(db.TIMESTAMP(timezone=True), default=db.func.current_timestamp(), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    wfh_type = db.Column(db.String(50))
    reason = db.Column(db.String(255), nullable=True) 
    attachment = db.Column(db.String(255), nullable=True)  # Add attachment field
    status = db.Column(db.String(50), default="Pending")
    updated_by = db.Column(db.Integer, nullable=True)  # Consider changing this to a foreign key if applicable
    last_updated = db.Column(db.TIMESTAMP(timezone=True), default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)  # Updated to auto-update
    additional_reason = db.Column(db.String(255), nullable=True) 

    def __init__(self, sid, request_date, wfh_type, reason=None, status="Pending", attachment=None, updated_by=None,additional_reason=None):
        self.sid = sid
        self.request_date = request_date
        self.wfh_type = wfh_type
        self.reason = reason
        self.updated_by = updated_by
        self.status = status
        self.attachment = attachment
        self.additional_reason = additional_reason

    def json(self):
        return {
            "rid": self.rid,
            "sid": self.sid,
            "wfh_type": self.wfh_type,
            "reason": self.reason,
            "updated_by": self.updated_by,
            "request_date": self.request_date.isoformat(),
            "status": self.status,
            "createdAt": self.createdAt,
            "attachment":self.attachment,
            "additionalreason":self.additional_reason,
            "lastupdated":self.last_updated
        }
    
#RequestLogs:
class RequestLogs(db.Model):
    __tablename__ = "requestlogs"

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rid = db.Column(db.Integer, nullable=False)
    previous_status = db.Column(db.String(50), default="Pending")
    updated_by = db.Column(db.Integer, nullable=True)
    new_additional_reason = db.Column(db.String(255), nullable=True)
    status_changedAt = db.Column(db.TIMESTAMP(timezone=True), default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=True)  # Updated to auto-update

    def __init__(self, rid, previous_status, updated_by, new_additional_reason=None):
        self.rid = rid
        self.previous_status = previous_status
        self.updated_by = updated_by
        self.additional_reason = new_additional_reason

    def json(self):
        return {
            "log_id": self.log_id,
            "rid": self.rid,
            "status": self.previous_status,
            "updated_by": self.updated_by,
            "additional_reason": self.additional_reason,
            "status_changedAt": self.status_changedAt
        }

#Request table functions
@app.route("/request/employee/rid/<int:rid>", methods=["GET"])
def get_requests_by_rid(rid):
    try:
        requests = db.session.query(Request).filter_by(rid=rid).all()
        print(f"Fetching request with rid: {rid}")  # Debug log

        if not requests:
            return jsonify({
                "code": 404,
                "message": f"No requests with this rid found {rid}."
            }), 404

        request_list = [r.json() for r in requests]

        return jsonify({
            "code": 200,
            "data": request_list
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "An error occurred while retrieving the requests. " + str(e)
        }), 500

@app.route("/request/employee/<int:sid>", methods=["GET"])
def get_requests_by_sid(sid):
    try:
        selfrequests = db.session.query(Request).filter_by(sid=sid).all()
        if not selfrequests:
            return jsonify({
                "code": 404,
                "message": f"No requests found for employee with sid {sid}."
            }), 404

        employee_service_url = f"{EMPLOYEE_URL}/{sid}"  # Construct the correct URL
        response = requests.get(employee_service_url)
        if response.status_code != 200:
            return jsonify({"code": 500, "message": "Error fetching employee data."}), 500
        
        employee_data = response.json()
        if employee_data["code"] != 200:
            return jsonify({"code": 404, "message": "No employee found."}), 404
        
        # Extract approval count for the employee
        employees = employee_data["data"]
        employee_approvalcount = employees.get("approval_count", 0)  # Ensure it's valid
        employee_lname = employees.get("Staff_LName")
        employee_fname = employees.get("Staff_FName")
        requestslist = []
        for request in selfrequests:
            req_json = request.json()
            req_json["approvalcount"] = employee_approvalcount 
            req_json["stafflname"] = employee_lname 
            req_json["stafffname"] = employee_fname 

            requestslist.append(req_json)
        
        return jsonify({"code": 200, "data": requestslist}), 200
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "An error occurred while retrieving the requests. " + str(e)
        }), 500

@app.route("/request", methods = ["POST"])
def create_request():
    # Process the form data
    sid = request.form.get('sid')
    wfh_type = request.form.get('type')
    reason = request.form.get('reason')
    email = request.form.get('email')  # Get email from form data
    staff_fname = request.form.get('staff_fname')  # Get staff_fname from form data
    staff_lname = request.form.get('staff_lname')  # Get staff_lname from form data

    # Log values for debugging
    app.logger.info(f"SID: {sid}, wfh_type: {wfh_type}, Reason: {reason}, Email: {email}, Staff FName: {staff_fname},StaffLName: {staff_lname}")

    # Handle file upload
    if 'attachment' not in request.files:
        return jsonify({"code": 400, "message": "No file part in the request."}), 400

    file = request.files['attachment']
    if file.filename == '':
        return jsonify({"code": 400, "message": "No selected file."}), 400

    filename = None
    if file:
        filename = secure_filename(file.filename)  # Secure the filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save file

    request_dates = request.form.getlist('request_dates')  # Get all request dates

    # Insert request data into the database
    try:
        for request_date in request_dates:
            new_request = Request(sid=sid, request_date=request_date, wfh_type=wfh_type, reason=reason, attachment=filename)
            db.session.add(new_request)

        db.session.commit()
        exchange = 'email'
        body = {
            "employee": {
                "email": email,
                "Staff_FName": staff_fname,
                "Staff_LName": staff_lname
            },
            "request": {
                "request_id": new_request.rid,
                "request_type": new_request.wfh_type
            }
        }
        channel.exchange_declare(exchange=exchange,
                        exchange_type='topic', durable=True)
        channel.basic_publish(exchange=exchange,
                    routing_key='request',
                    body=json.dumps(body))
        
        return jsonify({"code": 201, "message": f"Employee {sid} submitted request successfully."}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {str(e)}")  # Log the error for debugging

        return jsonify({"code": 500, "message": "An error occurred while creating the request. " + str(e)}), 500    



@app.route("/request/<int:rid>/employee/<int:sid>/reporting/<int:reportingID>/approve", methods=["PUT"])
def approve_request(rid, sid, reportingID):
    try:
        # Fetch the WFH request entry
        request_entry = Request.query.filter_by(status="Pending", rid=rid, sid=sid).one()

        if not request_entry:
            return jsonify({
                "code": 404,
                "message": f"Request with ID {rid} for employee {sid} not found."
            }), 404

        if request_entry.status != "Pending":
            return jsonify({
                "code": 400,
                "message": f"Request {rid} for employee {sid} cannot be approved as its status is '{request_entry.status}'."
            }), 400

        # Log the request status change
        previous_status = request_entry.status
        new_log = RequestLogs(rid=rid, previous_status=previous_status, updated_by=reportingID)
        db.session.add(new_log)
        db.session.commit()

        # Step 1: Get the employee data
        employee_service_url = f"{EMPLOYEE_URL}/{sid}"
        response = requests.get(employee_service_url)

        if response.status_code != 200:
            return jsonify({"code": 500, "message": "Error fetching employee data."}), 500

        employee_data = response.json()
        if employee_data["code"] != 200:
            return jsonify({"code": 404, "message": "No employee found."}), 404

        employeedetails = employee_data["data"]
        approvalcount = employeedetails["approval_count"]
        approvalcountmax = 2

        # Step 2: Check and update the approval count
        if approvalcount < approvalcountmax:
            # Approve the WFH request
            request_entry.status = "Approved"
            request_entry.updated_by = reportingID
            approvalcount += 1  # Increment the employee's approval count
            db.session.commit()

            # Step 3: Update the approval count in the employee service
            update_employee_url = f"{EMPLOYEE_URL}/{sid}/update_approval_count"
            update_data = {"approval_count": approvalcount}
            update_response = requests.put(update_employee_url, json=update_data)

            if update_response.status_code != 200:
                return jsonify({"code": 500, "message": "Error updating employee approval count."}), 500
            
        if approvalcount >= approvalcountmax:
            return jsonify({"code": 404, "message": f"Employee {sid}, has exceed the number of wfh requests. Please check again. Current approved WFH requests: {approvalcount}"}), 404
        exchange = 'email'
        body = {
            "employee": {
                "email": request_entry.Email,
                "Staff_FName": request_entry.Staff_FName
            },
            "request": {
                "request_id": request_entry.rid,
                "request_type": request_entry.type
            }
        }
        channel.exchange_declare(exchange=exchange,
                        exchange_type='topic', durable=True)
        channel.basic_publish(exchange=exchange,
                    routing_key='request.approve',
                    body=json.dumps(body))
        
        return jsonify({
            "code": 200,
            "message": f"Request {rid} for employee {sid} has been approved."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": "An error occurred while approving the request. " + str(e)
        }), 500


    
@app.route("/request/<int:rid>/employee/<int:sid>/reporting/<int:reportingID>/reject", methods=["PUT"])
def reject_request(rid, sid,reportingID):
    try:
        # Fetch additional_reason from JSON body
        data = request.get_json()
        additional_reason = data.get("additional_reason")
        
        if not additional_reason:
            return jsonify({
                "code": 400,
                "message": "Additional reason is required for rejection."
            }), 400
        
        request_entry = Request.query.filter_by(status="Pending", rid=rid, sid=sid).one()

        if not request_entry:
            return jsonify({
                "code": 404,
                "message": f"Request with ID {rid} for employee {sid} not found."
            }), 404

        if request_entry.status != "Pending":
            return jsonify({
                "code": 400,
                "message": f"Request {rid} for employee {sid} cannot be approved as its status is '{request_entry.status}'."
            }), 400

        request_entry.additional_reason = additional_reason  # Store the additional reason
        request_entry.status = "Rejected"
        request_entry.updated_by = reportingID
        db.session.commit()

        # Log the request status change
        previous_status = request_entry.status
        new_log = RequestLogs(rid=rid, previous_status=previous_status, updated_by=reportingID)
        db.session.add(new_log)
        db.session.commit()

        exchange = 'email'
        body = {
            "employee": {
                "email": request_entry.Email,
                "Staff_FName": request_entry.Staff_FName
            },
            "request": {
                "request_id": request_entry.rid,
                "request_type": request_entry.type
            }
        }
        channel.exchange_declare(exchange=exchange,
                        exchange_type='topic', durable=True)
        channel.basic_publish(exchange=exchange,
                    routing_key='request.reject',
                    body=json.dumps(body))
        
        return jsonify({
            "code": 200,
            "message": f"Request {rid} for employee {sid} has been rejected."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": "An error occurred while rejecting the request. " + str(e)
        }), 500



@app.route("/request/<int:rid>/employee/<int:sid>/reporting/<int:reportingID>/withdraw", methods=["PUT"])
def withdraw_request(rid, sid,reportingID):
    try:
               # Fetch additional_reason from JSON body
        data = request.get_json()
        additional_reason = data.get("additional_reason")
        
        if not additional_reason:
            return jsonify({
                "code": 400,
                "message": "Additional reason is required for rejection."
            }), 400
        
        request_entry = Request.query.filter_by(rid=rid, sid=sid).filter(Request.status.in_(["Pending", "Approved"])).one()

        if not request_entry:
            return jsonify({
                "code": 404,
                "message": f"Request with ID {rid} for employee {sid} not found."
            }), 404

        if (request_entry.status == "Rejected") or (request_entry.status =="Withdrawn"):
            return jsonify({
                "code": 400,
                "message": f"Request {rid} for employee {sid} cannot be withdrawn as its status is '{request_entry.status}'."
            }), 400

        previous_status = request_entry.status
        # Log the status change
        new_log = RequestLogs(rid=rid, previous_status=previous_status, updated_by=sid)
        db.session.add(new_log)
        db.session.commit()        

        # Step 1: Get the employee data
        employee_service_url = f"{EMPLOYEE_URL}/{sid}"
        response = requests.get(employee_service_url)

        if response.status_code != 200:
            return jsonify({"code": 500, "message": "Error fetching employee data."}), 500

        employee_data = response.json()
        if employee_data["code"] != 200:
            print(employee_data)
            return jsonify({"code": 404, "message": "No employee found."}), 404

        employeedetails = employee_data["data"]
        approvalcount = employeedetails["approval_count"]
        approvalcountmax = 2
        approvalcountmin = 0

        if request_entry.status == "Approved":
        # Step 2: Check and update the approval count
            if (approvalcount <= approvalcountmax) and (approvalcount != approvalcountmin):
                # Approve the WFH request
                request_entry.status = "Withdrawn"
                request_entry.additional_reason = additional_reason  # Store the additional reason
                request_entry.updated_by = sid
                approvalcount -= 1  # Increment the employee's approval count
                db.session.commit()

                # Step 3: Update the approval count in the employee service
                update_employee_url = f"{EMPLOYEE_URL}/{sid}/update_approval_count"
                update_data = {"approval_count": approvalcount}
                update_response = requests.put(update_employee_url, json=update_data)

                if update_response.status_code != 200:
                    return jsonify({"code": 500, "message": f"Error updating employee {sid}'s approval count." + str(e)}), 500
                
        if request_entry.status == "Pending":
                request_entry.status = "Withdrawn"
                request_entry.updated_by = sid
                request_entry.additional_reason = additional_reason  # Store the additional reason
                db.session.commit()  

        exchange = 'email'
        body = {
            "employee": {
                "email": request_entry.Email,
                "Staff_FName": request_entry.Staff_FName
            },
            "request": {
                "request_id": request_entry.rid,
                "request_type": request_entry.type
            }
        }
        channel.exchange_declare(exchange=exchange,
                        exchange_type='topic', durable=True)
        channel.basic_publish(exchange=exchange,
                    routing_key='request.withdraw',
                    body=json.dumps(body))
        
        return jsonify({
            "code": 200,
            "message": f"Request {rid} for employee {sid} has been withdrawn."
        }), 200


    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": "An error occurred while withdrawing the request. " + str(e)
        }), 500
    

@app.route("/request/<int:rid>/employee/<int:sid>/reporting/<int:reportingID>/revoke", methods=["PUT"])
def revoke_request(rid, sid,reportingID):
    try:
        # Fetch additional_reason from JSON body
        data = request.get_json()
        additional_reason = data.get("additional_reason")
        
        if not additional_reason:
            return jsonify({
                "code": 400,
                "message": "Additional reason is required for rejection."
            }), 400
        
        request_entry = Request.query.filter_by(status="Approved", rid=rid, sid=sid).one()

        if not request_entry:
            return jsonify({
                "code": 404,
                "message": f"Request with ID {rid} for employee {sid} not found."
            }), 404

        if request_entry.status !="Approved":
            return jsonify({
                "code": 400,
                "message": f"Request {rid} for employee {sid} cannot be withdrawn as its status is '{request_entry.status}'."
            }), 400

        previous_status = request_entry.status
        # Log the status change
        new_log = RequestLogs(rid=rid, previous_status=previous_status, updated_by=sid)
        db.session.add(new_log)
        db.session.commit()        

        # Step 1: Get the employee data
        employee_service_url = f"{EMPLOYEE_URL}/{sid}"
        response = requests.get(employee_service_url)

        if response.status_code != 200:
            return jsonify({"code": 500, "message": "Error fetching employee data."}), 500

        employee_data = response.json()
        if employee_data["code"] != 200:
            print(employee_data)
            return jsonify({"code": 404, "message": "No employee found."}), 404

        employeedetails = employee_data["data"]
        approvalcount = employeedetails["approval_count"]
        approvalcountmax = 2
        approvalcountmin = 0

        # Step 2: Check and update the approval count
        if (approvalcount <= approvalcountmax) and (approvalcount != approvalcountmin) and (request_entry.status == "Approved"):
            # Approve the WFH request
            request_entry.status = "Rejected"
            request_entry.updated_by = reportingID
            request_entry.additional_reason = additional_reason  # Store the additional reason

            approvalcount -= 1  # Increment the employee's approval count
            db.session.commit()

            # Step 3: Update the approval count in the employee service
            update_employee_url = f"{EMPLOYEE_URL}/{sid}/update_approval_count"
            update_data = {"approval_count": approvalcount}
            update_response = requests.put(update_employee_url, json=update_data)

            if update_response.status_code != 200:
                return jsonify({"code": 500, "message": "Error updating employee approval count. Please check total approval count."}), 500
        
        exchange = 'email'
        body = {
            "employee": {
                "email": request_entry.Email,
                "Staff_FName": request_entry.Staff_FName
            },
            "request": {
                "request_id": request_entry.rid,
                "request_type": request_entry.type
            }
        }
        channel.exchange_declare(exchange=exchange,
                        exchange_type='topic', durable=True)
        channel.basic_publish(exchange=exchange,
                    routing_key='request.reject',
                    body=json.dumps(body))
        
        return jsonify({
            "code": 200,
            "message": f"Previously approved Request {rid} for employee {sid} has been revoked. Current Request {sid}'s status is: {request_entry.status}"
        }), 200


    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": "An error occurred while withdrawing the request. " + str(e)
        }), 500

# Helper function to calculate working days difference
def calculate_working_hours_difference(start, end):
    # Move start to the next working day if it falls on a weekend
    while start.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        start += timedelta(days=1)
        start = datetime.combine(start, time.min, tzinfo=start.tzinfo)  # Set time to start of the next working day

    working_hours = 0
    current = start

    while current < end:
        if current.weekday() < 5:  # Monday to Friday
            working_hours += 1
        current += timedelta(hours=1)

    return working_hours

@app.route("/request/auto-reject", methods=["PUT"])
def auto_reject_old_pending_requests():
    try:
        now = datetime.now(tz=timezone.utc)

        pending_requests = Request.query.filter_by(status="Pending").all()

        for req in pending_requests:
            created_at = req.createdAt

            # Calculate working hours difference, excluding weekends
            working_hours_difference = calculate_working_hours_difference(created_at, now)

            # If more than 24 working hours (1 working day) have passed, reject the request
            if working_hours_difference > 24:
                req.status = "Rejected"
                req.additional_reason = "All pending requests older than 1 working day have been rejected by the system."
        
        db.session.commit()

        exchange = 'email'
        body = {
            "employee": {
                "email": pending_requests.Email,
                "Staff_FName": pending_requests.Staff_FName
            },
            "request": {
                "request_id": pending_requests.rid,
                "request_type": pending_requests.type
            }
        }
        channel.exchange_declare(exchange=exchange,
                        exchange_type='topic', durable=True)
        channel.basic_publish(exchange=exchange,
                    routing_key='request.reject',
                    body=json.dumps(body))
        
        return jsonify({
            "code": 200,
            "message": "All pending requests older than 1 working day have been rejected by the system."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": "An error occurred while rejecting the old pending requests. " + str(e)
        }), 500

# Scheduler function
def start_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule the auto-reject function to run every hour
    scheduler.add_job(auto_reject_old_pending_requests, 'interval', hours=5)
    scheduler.start()


# Get team requests
@app.route("/request/team/<int:manager_id>", methods=["GET"])
def get_team_requests(manager_id):
    try:
        # Step 1: Get employees who report to this manager
        employee_service_url = f"{EMPLOYEE_URL}/reporting_manager/{manager_id}"
        response = requests.get(employee_service_url)
        if response.status_code != 200:
            return jsonify({"code": 500, "message": "Error fetching employees under manager."}), 500
        
        employee_data = response.json()
        if employee_data["code"] != 200:
            return jsonify({"code": 404, "message": "No employees found under this manager."}), 404
        
        # Extract staff IDs from the employee data
        employees = employee_data["data"]
        staff_ids = [emp["Staff_ID"] for emp in employees]

        # Step 2: Fetch WFH requests for these staff IDs
        team_requests = Request.query.filter(Request.sid.in_(staff_ids)).all()
        if not team_requests:
            return jsonify({"code": 404, "message": "No WFH requests found for this team."}), 404

        # Step 3: Create a dictionary of employee positions by Staff_ID
        employee_positions = {emp["Staff_ID"]: emp["Position"] for emp in employees}
        employee_dept = {emp["Staff_ID"]: emp["Dept"] for emp in employees}
        employee_lname = {emp["Staff_ID"]: emp["Staff_LName"] for emp in employees}
        employee_fname = {emp["Staff_ID"]: emp["Staff_FName"] for emp in employees}
        employee_approvalcount = {emp["Staff_ID"]: emp["approval_count"] for emp in employees}


        # Step 4: Include the position in the returned WFH request data
        data = []
        for request in team_requests:
            req_json = request.json()
            # Add the employee's position to each request
            req_json["position"] = employee_positions.get(request.sid, "Unknown")
            req_json["department"] = employee_dept.get(request.sid, "Unknown")
            req_json["fname"] = employee_fname.get(request.sid, "Unknown")
            req_json["lname"] = employee_lname.get(request.sid, "Unknown")
            req_json["approvalcount"] = employee_approvalcount.get(request.sid, "Unknown")

            # print(req_json)
            data.append(req_json)
            # print(data)

        return jsonify({"code": 200, "data": data}), 200

    except Exception as e:
        return jsonify({"code": 500, "message": f"An error occurred: {str(e)}"}), 500




if __name__ == "__main__":
    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=5200, debug=True)
