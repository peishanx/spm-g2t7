from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS
import os
import sys
from sqlalchemy import and_
from sqlalchemy import text

app = Flask(__name__)
# Primary database URI for the request microservice
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("employee_dbURL") or "mysql+mysqlconnector://root:example@database:3306/employee"

# Additional databases
app.config["SQLALCHEMY_BINDS"] = {
    'request_db': environ.get("request_dbURL") or "mysql+mysqlconnector://root:example@database:3306/request"
}

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 299}

db = SQLAlchemy(app)

CORS(app)

class Employee(db.Model):
    # __bind_key__ = 'employee'  # This tells SQLAlchemy to use the 'employee' database
    __tablename__ = "employee"

    Staff_ID = db.Column(db.Integer, primary_key=True)
    Staff_FName = db.Column(db.String(50), nullable=False)
    Staff_LName = db.Column(db.String(50), nullable=False)
    Dept = db.Column(db.String(50), nullable=False)
    Position = db.Column(db.String(50), nullable=False)
    Country = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(50), nullable=False)
    Reporting_Manager = db.Column(db.Integer)
    Role = db.Column(db.Integer, nullable=False)
    approval_count = db.Column(db.Integer, default=0)  # Added approval_count

    def __init__(self, Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role, approval_count=0):
        self.Staff_ID = Staff_ID
        self.Staff_FName = Staff_FName
        self.Staff_LName = Staff_LName
        self.Dept = Dept
        self.Position = Position
        self.Country = Country
        self.Email = Email
        self.Reporting_Manager = Reporting_Manager
        self.Role = Role
        self.approval_count = approval_count  # Initialize approval_count

    def json(self):
        return {
            "Staff_ID": self.Staff_ID,
            "Staff_FName": self.Staff_FName,
            "Staff_LName": self.Staff_LName,
            "Dept": self.Dept,
            "Position": self.Position,
            "Country": self.Country,
            "Email": self.Email,
            "Reporting_Manager": self.Reporting_Manager,
            "Role": self.Role,
            "approval_count": self.approval_count  # Added approval_count to JSON output
        }

@app.route("/employee/<int:Staff_ID>")
def find_by_Staff_ID(Staff_ID):
    staff_entry = db.session.scalars(db.select(Employee).filter_by(Staff_ID=Staff_ID).limit(1)).first()

    if staff_entry:
        return jsonify({"code": 200, "data": staff_entry.json()})
    return jsonify({"code": 404, "message": "Staff not found."}), 404

@app.route("/employee/filter/<string:Dept>")
def find_by_dept(Dept):
    employees = db.session.query(Employee.Staff_ID, Employee.Staff_FName, Employee.Staff_LName).filter_by(Dept=Dept).all()

    if employees:
        employee_list = [{"Staff_ID": e.Staff_ID, "Staff_FName": e.Staff_FName, "Staff_LName": e.Staff_LName} for e in employees]
        return jsonify({"code": 200, "data": employee_list})
    return jsonify({"code": 404, "message": f"No employees found in the department {Dept}."}), 404

@app.route("/employee/position/<string:Position>")
def find_by_position(Position):
    employees = db.session.query(Employee.Staff_ID, Employee.Staff_FName, Employee.Staff_LName).filter_by(Position=Position).all()

    if employees:
        employee_list = [{"Staff_ID": e.Staff_ID, "Staff_FName": e.Staff_FName, "Staff_LName": e.Staff_LName} for e in employees]
        return jsonify({"code": 200, "data": employee_list})
    return jsonify({"code": 404, "message": f"No employees found with the position {Position}."}), 404

@app.route("/employee/role/<int:Role>")
def find_by_role(Role):
    employees = db.session.query(Employee.Staff_ID, Employee.Staff_FName, Employee.Staff_LName).filter_by(Role=Role).all()

    if employees:
        employee_list = [{"Staff_ID": e.Staff_ID, "Staff_FName": e.Staff_FName, "Staff_LName": e.Staff_LName} for e in employees]
        return jsonify({"code": 200, "data": employee_list})
    return jsonify({"code": 404, "message": f"No employees found with the role {Role}."}), 404

@app.route("/employee/filter/<string:dept>/<int:role>/<string:comparison>", methods=["GET"])
def filter_by_dept_and_role(dept, role, comparison):
    try:
        if comparison == "equal":
            employees = Employee.query.filter(
                and_(
                    Employee.Dept == dept,
                    Employee.Role == role
                )
            ).all()
        elif comparison == "not_equal":
            employees = Employee.query.filter(
                and_(
                    Employee.Dept == dept,
                    Employee.Role != role
                )
            ).all()
        else:
            return jsonify({
                "code": 400,
                "message": "Invalid comparison type. Use 'equal' or 'not_equal'."
            }), 400

        if not employees:
            return jsonify({
                "code": 404,
                "message": f"No employees found for department '{dept}' with role {comparison} to '{role}'."
            }), 404

        employee_list = [employee.json() for employee in employees]

        return jsonify({
            "code": 200,
            "data": employee_list
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "An error occurred while fetching the employees. " + str(e)
        }), 500

@app.route("/employee/reporting_manager/<int:manager_id>", methods=["GET"])
def get_employees_by_manager(manager_id):
    employees = Employee.query.filter_by(Reporting_Manager=manager_id).all()
    if not employees:
        return jsonify({"code": 404, "message": "No employees found for this manager."}), 404

    return jsonify({"code": 200, "data": [employee.json() for employee in employees]}), 200

@app.route("/employee/<int:sid>/update_approval_count", methods=["PUT"])
def update_approval_count(sid):
    try:
        data = request.get_json()
        approval_count = data.get("approval_count")

        employee = Employee.query.filter_by(Staff_ID=sid).first()
        if not employee:
            return jsonify({"code": 404, "message": "Employee not found"}), 404

        employee.approval_count = approval_count
        db.session.commit()

        return jsonify({"code": 200, "message": "Approval count updated successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": "Error updating approval count"}), 500
    
# get employee wfh counts 

@app.route('/employee/wfh/counts', methods=['GET'])
def count_wfh():
    try:
        selected_date = request.args.get('date', default=None)
        counts = {}

        # Get all departments and positions regardless of WFH requests
        with db.get_engine(app, bind='employee').connect() as conn:
            employee_query = text(""" 
                SELECT Dept, Position, COUNT(*) AS employee_count
                FROM employee.employee
                GROUP BY Dept, Position
            """)
            employee_counts = conn.execute(employee_query).fetchall()

        # Initialize counts with 0 WFH for each department and position
        for emp_row in employee_counts:
            dept = emp_row.Dept
            position = emp_row.Position
            if dept not in counts:
                counts[dept] = {}
            counts[dept][position] = {
                "employee_count": emp_row.employee_count,
                "am": 0,
                "pm": 0,
                "full_day": 0,
                "total": 0,
                "leaves": 0  # Add a new field for leaves
            }

        # Fetch WFH requests for the selected date
        with db.get_engine(app, bind='request').connect() as conn:
            request_query = text(""" 
                SELECT e.Dept, e.Position, r.wfh_type, COUNT(*) AS approved_request_count
                FROM request.request AS r
                JOIN employee.employee AS e ON r.sid = e.Staff_ID
                WHERE r.status = 'Approved'
                AND r.request_date = :selected_date
                GROUP BY e.Dept, e.Position, r.wfh_type
            """)
            approved_counts = conn.execute(request_query, {'selected_date': selected_date}).fetchall()

        # Update WFH counts for departments and positions that have approved WFH requests
        for req_row in approved_counts:
            dept = req_row.Dept
            position = req_row.Position
            wfh_type = req_row.wfh_type
            approved_count = req_row.approved_request_count

            if dept in counts and position in counts[dept]:
                if wfh_type.lower() == 'am':
                    counts[dept][position]["am"] += approved_count
                elif wfh_type.lower() == 'pm':
                    counts[dept][position]["pm"] += approved_count
                elif wfh_type.lower() == 'full_day':
                    counts[dept][position]["full_day"] += approved_count

                counts[dept][position]["total"] += approved_count

        # Fetch leave counts for the selected date
        with db.get_engine(app, bind='employee_leaves').connect() as conn:
            leave_query = text(""" 
                SELECT e.Dept, e.Position, COUNT(*) AS leave_count
                FROM employee_leaves.employee_leave AS el
                JOIN employee.employee AS e ON el.Staff_ID = e.Staff_ID
                WHERE el.Leave_Date = :selected_date
                GROUP BY e.Dept, e.Position
            """)
            leave_counts = conn.execute(leave_query, {'selected_date': selected_date}).fetchall()

        # Update leave counts for departments and positions that have leave requests
        for leave_row in leave_counts:
            dept = leave_row.Dept
            position = leave_row.Position
            leave_count = leave_row.leave_count

            if dept in counts and position in counts[dept]:
                counts[dept][position]["leaves"] += leave_count  # Add leave counts

        return jsonify(counts)

    except Exception as e:
        print(f"Error: {e}")
        return {'error': str(e)}


if __name__ == "__main__": 
    app.run(host="0.0.0.0", port = 5100, debug =True)