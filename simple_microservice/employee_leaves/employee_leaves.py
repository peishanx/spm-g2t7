from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timedelta

app = Flask(__name__)

#Employee Leaves db
app = Flask(__name__)
# CORS(app, resources={r"/request/*": {"origins": "http://spm-frontend:8000"}})

# Configure the binds for additional databases
app.config["SQLALCHEMY_BINDS"] = {
    'employee_leaves': environ.get("employee_leaves_dbURL") or "mysql+mysqlconnector://root:@localhost:3306/employee_leaves"
}

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 299}
app.config['UPLOAD_FOLDER'] = 'uploads'  # Define where to store uploaded attachment files for form submission


db = SQLAlchemy(app)

CORS(app)

# Database model for employee leaves
class EmployeeLeave(db.Model):
    __bind_key__ = 'employee_leaves'  # Specify the bind key for this model
    __tablename__ = 'employee_leave'

    Staff_ID = db.Column(db.String, primary_key=True)
    Staff_FName = db.Column(db.String)
    Staff_LName = db.Column(db.String)
    Leave_Date = db.Column(db.Date)
    Dept = db.Column(db.String)
    Position = db.Column(db.String)
    Role = db.Column(db.String)


@app.route("/leaves", methods=["GET"])
def get_leave_details():
    try:
        # Fetch all leave details from the employee_leaves database
        leave_details = db.session.query(EmployeeLeave).all()

        # Prepare the response data
        response_data = [{
            'staff_id': leave.Staff_ID,
            'staff_fname': leave.Staff_FName,
            'staff_lname': leave.Staff_LName,
            'leave_date': leave.Leave_Date.isoformat(),  # Convert to ISO format for JSON
            'dept': leave.Dept,
            'position': leave.Position,
            'role': leave.Role
        } for leave in leave_details]

        return jsonify({"code": 200, "data": response_data}), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "An error occurred while retrieving leave details. " + str(e)
        }), 500

if __name__ == "__main__":
    app.run(port=5300, debug=True)