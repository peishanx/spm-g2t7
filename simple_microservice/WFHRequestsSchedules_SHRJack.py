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
        # Get the current date if not passed
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
            'wfh_status': "In Office (Full Day)",  # Default WFH status
            'in_office_status': "In Office (Full Day)",  # Default In Office status
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

        # Update employee data based on WFH requests
        for req in requests:
            emp_id = req.sid
            if req.wfh_type == "Full Day":
                employee_data[emp_id]['wfh_status'] = "WFH (Full Day)"
                employee_data[emp_id]['in_office_status'] = "N/A"
            elif req.wfh_type == "PM":
                employee_data[emp_id]['wfh_status'] = "WFH (PM)"
                employee_data[emp_id]['in_office_status'] = "In Office (AM)";  # Assuming AM in office
            elif req.wfh_type == "AM":
                employee_data[emp_id]['wfh_status'] = "WFH (AM)"
                employee_data[emp_id]['in_office_status'] = "In Office (PM)";  # Assuming PM in office

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


@app.route('/leaves/check/<int:staff_id>', methods=['GET'])
def check_employee_leave(staff_id):
    try:
        leave_date = request.args.get('date')  # Get the date from query parameters

        sql_query = text("""
            SELECT Leave_Date FROM employee_leave 
            WHERE Staff_ID = :staff_id 
            AND Leave_Date = :leave_date
        """)

        # Get the engine for the 'leaves' database and execute the query
        engine = db.get_engine('leaves')
        with engine.connect() as connection:
            result = connection.execute(sql_query, {'staff_id': staff_id, 'leave_date': leave_date})

            # Check if there are results
            leave_dates = [row.Leave_Date.isoformat() for row in result]

        return jsonify({'code': 200, 'leaveDates': leave_dates})

    except Exception as e:
        print(f"Error checking leave status for Staff ID {staff_id}: {e}")
        return jsonify({'code': 500, 'message': 'Internal server error'}), 500


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
