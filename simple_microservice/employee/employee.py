from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS
import os
import sys
from sqlalchemy import and_

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root:@localhost:3306/employee"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 299}

db = SQLAlchemy(app)

CORS(app)

class Employee(db.Model):
    __tablename__ = "employee"

    Staff_ID = db.Column(db.Integer, primary_key = True)
    Staff_FName = db.Column(db.String(50), nullable=False)
    Staff_LName = db.Column(db.String(50), nullable=False)
    Dept = db.Column(db.String(50), nullable=False)
    Position = db.Column(db.String(50), nullable=False)
    Country = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(50), nullable=False)
    Reporting_Manager = db.Column(db.Integer)
    Role = db.Column(db.Integer, nullable=False)

    def __init__(self, Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role):
        self.Staff_ID = Staff_ID
        self.Staff_FName = Staff_FName
        self.Staff_LName = Staff_LName
        self.Dept = Dept
        self.Position = Position
        self.Country = Country
        self.Email = Email
        self.Reporting_Manager = Reporting_Manager
        self.Role = Role

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
            "Role": self.Role
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

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port = 5100, debug =True)