from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timedelta, timezone
import os
import sys
import math
import pytz
from werkzeug.utils import secure_filename
import requests

#Request db
app = Flask(__name__)
CORS(app, resources={r"/request/*": {"origins": "http://localhost:8000"}})

app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root:@localhost:3306/request"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 299}
app.config['UPLOAD_FOLDER'] = 'uploads'  # Define where to store uploaded attachment files for form submission


db = SQLAlchemy(app)

CORS(app)

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
    updated_by = db.Column(db.String(100), nullable=True)
    last_updated = db.Column(db.TIMESTAMP(timezone=True), default=db.func.current_timestamp(), nullable=False)
    additional_reason = db.Column(db.String(255), nullable=True) 
    approval_count = db.Column(db.Integer, default=0)

    def __init__(self, sid, request_date, wfh_type, reason=None, approval_count=0, status="Pending", attachment=None, updated_by=None,additional_reason=None):
        self.sid = sid
        self.request_date = request_date
        self.wfh_type = wfh_type
        self.reason = reason
        self.approval_count = approval_count
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
            "approval_count": self.approval_count,
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
    rid = db.Column(db.Integer, db.ForeignKey('request.rid', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected', 'Withdrawn'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('employee.employee.Staff_ID', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    additional_reason = db.Column(db.String(255), nullable=True)
    status_changedAt = db.Column(db.TIMESTAMP(timezone=True), default=db.func.current_timestamp(), nullable=False)

    def __init__(self, rid, status, updated_by, additional_reason=None):
        self.rid = rid
        self.status = status
        self.updated_by = updated_by
        self.additional_reason = additional_reason

    def json(self):
        return {
            "log_id": self.log_id,
            "rid": self.rid,
            "status": self.status,
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
        requests = db.session.query(Request).filter_by(sid=sid).all()

        if not requests:
            return jsonify({
                "code": 404,
                "message": f"No requests found for employee with sid {sid}."
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

@app.route("/request/employee/check", methods=["GET"])
def get_requests_for_employees(employee_list):
    return_list = []

    if not employee_list or not isinstance(employee_list, list):
        return {
            "code": 400,
            "message": "Invalid input. Expected a list of employee entries."
        }

    try:
        for employee in employee_list:
            staff_id = employee.get("Staff_ID")

            if staff_id is None:
                return {
                    "code": 400,
                    "message": f"Employee entry is missing 'Staff_ID'. Received: {employee}"
                }

            matching_requests = Request.query.filter_by(sid=staff_id).all()

            if matching_requests:
                for request_entry in matching_requests:
                    return_list.append(request_entry.json())
            else:
                return {
                    "code": 404,
                    "message": f"No matching requests found for Staff_ID: {staff_id}"
                }

        return {
            "code": 200,
            "data": return_list
        }

    except Exception as e:
        return {
            "code": 500,
            "message": f"An error occurred while processing the request. Error: {str(e)}"
        }

@app.route("/request", methods = ["POST"])
def create_request():
    # Process the form data
    sid = request.form.get('sid')
    wfh_type = request.form.get('type')
    reason = request.form.get('reason')

    # Log values for debugging
    app.logger.info(f"SID: {sid}, wfh_type: {wfh_type}, Reason: {reason}")

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
        return jsonify({"code": 201, "message": f"Employee {sid} submitted request successfully."}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {str(e)}")  # Log the error for debugging

        return jsonify({"code": 500, "message": "An error occurred while creating the request. " + str(e)}), 500    



@app.route("/request/<int:rid>/employee/<int:sid>/approve", methods=["PUT"])
def approve_request(rid, sid):
    try:
        request_entry = Request.query.filter_by(status = "Pending", rid=rid, sid=sid).one()

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

@app.route("/request/<int:rid>/employee/<int:sid>/reject", methods=["PUT"])
def reject_request(rid, sid):
    try:
        request_entry = Request.query.filter_by(status = "Pending", rid=rid, sid=sid).one()

        if not request_entry:
            return jsonify({
                "code": 404,
                "message": f"Request with ID {rid} for employee {sid} not found."
            }), 404

        if request_entry.status != "Pending":
            return jsonify({
                "code": 400,
                "message": f"Request {rid} for employee {sid} cannot be rejected as its status is '{request_entry.status}'."
            }), 400

        additional_reason = request.form.get('additional_reason')
        # Update the request status
        request_entry.status = "Rejected"
        request_entry.updated_by = sid
        request_entry.additional_reason = additional_reason  # Store additional reason for rejection
        db.session.commit()

        # Log the status change
        new_log = RequestLogs(rid=rid, status="Rejected", updated_by=sid, additional_reason=additional_reason)
        db.session.add(new_log)
        db.session.commit() 

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

@app.route("/request/<int:rid>/employee/<int:sid>/withdraw", methods = ["PUT"])
def withdraw_request(rid, sid):
    try:
        request_entry = Request.query.filter_by(rid=rid, sid=sid).filter(Request.status.in_(["Pending", "Approved"])).one()

        if not request_entry:
            return jsonify({
                "code": 404,
                "message": f"Request with ID {rid} for employee {sid} not found."
            }), 404

        if request_entry.status not in ["Pending", "Approved"]:
            return jsonify({
                "code": 400,
                "message": f"Request {rid} for employee {sid} cannot be withdrawn as its status is '{request_entry.status}'."
            }), 400

        request_entry.status = "Withdrawn"
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": f"Request {rid} for employee {sid} has been successfully withdrawn."
        }), 200

    except Exception as e:
        # Roll back any changes if an error occurs
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": "An error occurred while withdrawing the request. " + str(e)
        }), 500

@app.route("/request/auto-reject", methods=["PUT"])
def auto_reject_old_pending_requests():
    try:
        now = datetime.now(tz=timezone.utc)

        pending_requests = Request.query.filter_by(status="Pending").all()

        for req in pending_requests:
            time_difference = now - req.createdAt

            if time_difference > timedelta(hours=24):
                req.status = "Rejected"
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": "All pending requests older than 24 hours have been rejected."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": "An error occurred while rejecting the old pending requests. " + str(e)
        }), 500

# Endpoint to get team requests
@app.route("/request/team/<int:manager_id>", methods=["GET"])
def get_team_requests(manager_id):
    try:
        # Step 1: Get employees who report to this manager
        employee_service_url = f"http://localhost:5100/employee/reporting_manager/{manager_id}"
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

        # Step 4: Include the position in the returned WFH request data
        data = []
        for request in team_requests:
            req_json = request.json()
            # Add the employee's position to each request
            req_json["position"] = employee_positions.get(request.sid, "Unknown")
            req_json["department"] = employee_dept.get(request.sid, "Unknown")
            req_json["fname"] = employee_fname.get(request.sid, "Unknown")
            req_json["lname"] = employee_lname.get(request.sid, "Unknown")

            data.append(req_json)

        return jsonify({"code": 200, "data": data}), 200

    except Exception as e:
        return jsonify({"code": 500, "message": f"An error occurred: {str(e)}"}), 500




if __name__ == "__main__":
       # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(port=5200, debug=True)