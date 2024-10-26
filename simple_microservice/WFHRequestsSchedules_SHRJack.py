from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from sqlalchemy import text
from flask import request
from datetime import date
from datetime import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure the main database for requests
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root:@localhost:3306/request"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure the binds for additional databases for employees and leaves
app.config["SQLALCHEMY_BINDS"] = {
    'employee': environ.get("employee_dbURL") or "mysql+mysqlconnector://root:@localhost:3306/employee",
    'leaves': environ.get("leaves_dbURL") or "mysql+mysqlconnector://root:@localhost:3306/employee_leaves"
}

# Set up SQLAlchemy for the application with a single instance
db = SQLAlchemy(app)

@app.route('/request/approved/<string:department_name>', methods=['GET'])
def get_all_requests(department_name):
    try:
        current_date = request.args.get('date', date.today().isoformat())

        # Fetch all employees in the department
        employee_query = text(""" 
            SELECT e.Staff_ID AS sid, 
                   e.Staff_FName AS employee_first_name, 
                   e.Staff_LName AS employee_last_name, 
                   e.Dept AS department, 
                   e.Position AS position 
            FROM employee.employee AS e 
            WHERE e.Dept = :dept
        """)
        
        employees = db.session.execute(employee_query, {'dept': department_name}).fetchall()

        # Prepare a dictionary to hold employee data
        employee_data = {emp.sid: {
            'employee_first_name': emp.employee_first_name,
            'employee_last_name': emp.employee_last_name,
            'department': emp.department,
            'position': emp.position,
            'wfh_status': "N/A",  # Default WFH status set to N/A
            'in_office_status': "N/A",  # Default In Office status set to N/A
            'leave_status': 'N/A'  # Placeholder for leave status
        } for emp in employees}

        # Fetch approved WFH requests for the specified date
        wfh_query = text(""" 
            SELECT r.*, 
                   e.Staff_FName AS employee_first_name, 
                   e.Staff_LName AS employee_last_name 
            FROM request AS r 
            JOIN employee.employee AS e ON r.sid = e.Staff_ID 
            WHERE r.status = 'Approved' AND e.Dept = :dept 
            AND r.request_date = :current_date
        """)
        
        result = db.session.execute(wfh_query, {'dept': department_name, 'current_date': current_date})
        requests = result.fetchall()

        # Fetch leave status for the specified date
        leave_query = text("""
            SELECT Staff_ID, Leave_Date
            FROM employee_leave 
            WHERE Leave_Date = :current_date
        """)
        
        leave_results = db.session.execute(leave_query, {'current_date': current_date}).fetchall()
        leave_ids = {row.Staff_ID for row in leave_results}  # Store staff IDs who are on leave

        # Update employee data based on WFH requests and leave status
        for req in requests:
            emp_id = req.sid
            if emp_id in leave_ids:
                employee_data[emp_id]['wfh_status'] = "N/A"  # If on leave, WFH status is N/A
                employee_data[emp_id]['in_office_status'] = "N/A"  # If on leave, in-office status is N/A
                employee_data[emp_id]['leave_status'] = "On Leave"  # Update leave status to "On Leave"
            else:
                # Set the correct WFH status if not on leave
                if req.wfh_type == "Full Day":
                    employee_data[emp_id]['wfh_status'] = "WFH (Full Day)"
                    employee_data[emp_id]['in_office_status'] = "N/A"
                elif req.wfh_type == "PM":
                    employee_data[emp_id]['wfh_status'] = "WFH (PM)"
                    employee_data[emp_id]['in_office_status'] = "In Office (AM)"  # Assuming AM in office
                elif req.wfh_type == "AM":
                    employee_data[emp_id]['wfh_status'] = "WFH (AM)"
                    employee_data[emp_id]['in_office_status'] = "In Office (PM)"  # Assuming PM in office

        # Convert employee data dictionary to list
        final_data = [
            {
                'sid': emp_id,
                'employee_first_name': data['employee_first_name'],
                'employee_last_name': data['employee_last_name'],
                'department': data['department'],
                'position': data['position'],
                'wfh_status': data['wfh_status'],
                'in_office_status': data['in_office_status'],
                'leave_status': data['leave_status'],
            } for emp_id, data in employee_data.items()
        ]

        return jsonify({'code': 200, 'data': final_data})

    except Exception as e:
        print(f"Error fetching requests for department '{department_name}': {e}")
        return jsonify({'code': 500, 'message': 'Internal server error'}), 500

@app.route('/ceo/director_schedules', methods=['GET'])
def get_director_schedules_for_ceo():
    try:
        requested_date = request.args.get('date', date.today().isoformat())
        
        schedule_query = text("""
            SELECT e.Staff_ID AS sid, e.Staff_FName, e.Staff_LName, e.Dept, e.Position,
                   r.request_date, r.wfh_type, el.Leave_Date
            FROM employee.employee AS e
            LEFT JOIN request AS r ON e.Staff_ID = r.sid AND r.request_date = :requested_date
            LEFT JOIN employee_leaves.employee_leave AS el ON e.Staff_ID = el.Staff_ID AND el.Leave_Date = :requested_date
            WHERE e.Position LIKE 'Director%'
        """)
        
        result = db.session.execute(schedule_query, {'requested_date': requested_date}).fetchall()

        schedule_data = []
        for row in result:
            leave_status = "On Leave" if row.Leave_Date else "N/A"
            wfh_status = {
                "AM": "WFH (AM)", 
                "PM": "WFH (PM)", 
                "Full Day": "WFH (Full Day)"
            }.get(row.wfh_type, "N/A")
            in_office_status = "In Office (Full Day)" if not row.wfh_type else (
                "In Office (PM)" if row.wfh_type == "AM" else "In Office (AM)" if row.wfh_type == "PM" else "N/A"
            )

            schedule_data.append({
                "sid": row.sid,
                "employee_first_name": row.Staff_FName,
                "employee_last_name": row.Staff_LName,
                "department": row.Dept,
                "position": row.Position,
                "request_date": row.request_date.isoformat() if row.request_date else "N/A",
                "wfh_status": wfh_status,
                "in_office_status": in_office_status,
                "leave_status": leave_status
            })

        return jsonify({"code": 200, "data": schedule_data})

    except Exception as e:
        print(f"Error fetching director schedules for CEO: {e}")
        return jsonify({"code": 500, "message": "Internal server error"}), 500

@app.route('/director/team_schedules', methods=['GET'])
def get_team_schedules_for_director():
    try:
        department = request.args.get('department')
        if not department:
            return jsonify({"code": 400, "message": "Department is required"}), 400
        
        selected_date = request.args.get('date', date.today().isoformat())
        
        schedule_query = text("""
            SELECT e.Staff_ID AS sid, e.Staff_FName, e.Staff_LName, e.Dept, e.Position,
                   r.request_date, r.wfh_type, el.Leave_Date
            FROM employee.employee AS e
            LEFT JOIN request AS r ON e.Staff_ID = r.sid AND r.request_date = :selected_date
            LEFT JOIN employee_leaves.employee_leave AS el ON e.Staff_ID = el.Staff_ID AND el.Leave_Date = :selected_date
            WHERE e.Dept = :dept AND e.Position NOT LIKE 'Director%'
        """)
        result = db.session.execute(schedule_query, {'dept': department, 'selected_date': selected_date}).fetchall()

        schedule_data = []
        for row in result:
            leave_status = "On Leave" if row.Leave_Date else "N/A"
            wfh_status = {
                "AM": "WFH (AM)", 
                "PM": "WFH (PM)", 
                "Full Day": "WFH (Full Day)"
            }.get(row.wfh_type, "N/A")
            in_office_status = 'In Office (Full Day)' if not row.wfh_type else (
                'N/A' if row.wfh_type == 'Full Day' else ('In Office (AM)' if row.wfh_type == 'PM' else 'In Office (PM)')
            )

            schedule_data.append({
                "sid": row.sid,
                "employee_first_name": row.Staff_FName,
                "employee_last_name": row.Staff_LName,
                "department": row.Dept,
                "position": row.Position,
                "request_date": row.request_date.isoformat() if row.request_date else "N/A",
                "wfh_status": wfh_status,
                "in_office_status": in_office_status,
                "leave_status": leave_status
            })

        return jsonify({"code": 200, "data": schedule_data})

    except Exception as e:
        print(f"Error fetching team schedules for Director: {e}")
        return jsonify({"code": 500, "message": "Internal server error"}), 500

@app.route('/team_schedule/<int:staff_id>', methods=['GET'])
def get_team_schedule(staff_id):
    try:
        # Get the requested date from query parameters, defaulting to today if not provided
        requested_date_str = request.args.get('date', default=datetime.now().date().isoformat())
        requested_date = datetime.strptime(requested_date_str, '%Y-%m-%d').date()

        # Fetch the employee's position
        employee_query = text("""
            SELECT Position FROM employee.employee WHERE Staff_ID = :staff_id
        """)
        employee_result = db.session.execute(employee_query, {'staff_id': staff_id}).fetchone()

        if not employee_result:
            return jsonify({"code": 404, "message": "Employee not found."}), 404

        position = employee_result.Position

        # Fetch all team members with the same position, their request dates, and leave status
        schedule_query = text("""
            SELECT e.Staff_ID AS sid,
                   e.Staff_FName AS employee_first_name,
                   e.Staff_LName AS employee_last_name,
                   e.Dept AS department,
                   e.Position AS position,
                   r.request_date AS request_date,
                   r.wfh_type AS wfh_status,
                   el.Leave_Date AS leave_date
            FROM employee.employee AS e
            LEFT JOIN request AS r ON e.Staff_ID = r.sid
            LEFT JOIN employee_leaves.employee_leave AS el ON e.Staff_ID = el.Staff_ID AND el.Leave_Date = :requested_date
            WHERE e.Position = :position
        """)

        result = db.session.execute(schedule_query, {'position': position, 'requested_date': requested_date})
        schedules = result.fetchall()

        # Convert to a list of dictionaries and calculate statuses
        schedule_data = []
        for row in schedules:
            leave_status = "On Leave" if row.leave_date else "Not on Leave"

            # Initialize WFH status and in-office status
            wfh_status = row.wfh_status if row.wfh_status else 'N/A'
            in_office_status = 'In Office (Full Day)'  # Default value

            # Logic for setting statuses based on leave
            if leave_status == "On Leave":
                wfh_status = 'N/A'
                in_office_status = 'N/A'
            else:
                # Handle WFH status and in-office status logic
                if wfh_status == 'PM':
                    in_office_status = 'In Office (AM)'
                elif wfh_status == 'AM':
                    in_office_status = 'In Office (PM)'
                elif wfh_status == 'Full Day':
                    in_office_status = 'N/A'  # No in-office if full day WFH

            schedule_data.append({
                "sid": row.sid,
                "employee_first_name": row.employee_first_name,
                "employee_last_name": row.employee_last_name,
                "department": row.department,
                "position": row.position,
                "request_date": row.request_date.isoformat() if row.request_date else "N/A",
                "wfh_status": wfh_status,
                "in_office_status": in_office_status,
                "leave_status": leave_status
            })

        return jsonify({"code": 200, "data": schedule_data})

    except Exception as e:
        print(f"Error fetching team schedule for Staff ID {staff_id}: {e}")
        return jsonify({"code": 500, "message": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(port=5000)  # Ensure the port is set to 5000
