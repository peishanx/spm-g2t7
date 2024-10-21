from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text

app = Flask(__name__)
CORS(app)

# Set up the MySQL database connections
app.config['SQLALCHEMY_BINDS'] = {
    'employee': 'mysql://root:@localhost/employee',
    'request': 'mysql://root:@localhost/request',
    'employee_leaves': 'mysql://root:@localhost/employee_leaves'

}

db = SQLAlchemy(app)

# Employee Model
class Employee(db.Model):
    __bind_key__ = 'employee'
    __tablename__ = 'employee'

    Staff_ID = db.Column(db.Integer, primary_key=True)
    Dept = db.Column(db.String(50), nullable=False)
    Position = db.Column(db.String(50), nullable=False)

# Request Model
class Request(db.Model):
    __bind_key__ = 'request'
    __tablename__ = 'request'

    rid = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Integer, nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    wfh_type = db.Column(db.String(50))
    status = db.Column(db.String(50), default='Pending')

class EmployeeLeave(db.Model):
    __bind_key__ = 'employee_leaves'  # Specify the bind key for this model
    __tablename__ = 'employee_leave'

    Staff_ID = db.Column(db.Integer, db.ForeignKey('employee.Staff_ID'), primary_key=True)
    Leave_Date = db.Column(db.Date, nullable=False)


@app.route('/employee/wfh/counts', methods=['GET'])
def count_wfh():
    try:
        selected_date = request.args.get('date', default=None)
        if not selected_date:  # Check if date is provided
            return jsonify({'error': 'Date parameter is required'}), 400
        
        counts = {}

        # Fetch employees and their details
        with db.get_engine(app, bind='employee').connect() as conn:
            employee_query = text(""" 
                SELECT Dept, Position, COUNT(*) AS employee_count
                FROM employee.employee
                GROUP BY Dept, Position
            """)
            employee_counts = conn.execute(employee_query).fetchall()

        # Initialize counts
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
                "leaves": 0  # Leave count initialized
            }

        # Fetch approved WFH requests for the selected date
        with db.get_engine(app, bind='request').connect() as conn:
            request_query = text(""" 
                SELECT e.Dept, e.Position, r.wfh_type, COUNT(*) AS approved_request_count
                FROM request.request AS r
                JOIN employee.employee AS e ON r.sid = e.Staff_ID
                WHERE r.status = 'Approved' AND r.request_date = :selected_date
                GROUP BY e.Dept, e.Position, r.wfh_type
            """)
            approved_counts = conn.execute(request_query, {'selected_date': selected_date}).fetchall()

        # Update WFH counts
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

        # Update leave counts
        for leave_row in leave_counts:
            dept = leave_row.Dept
            position = leave_row.Position
            leave_count = leave_row.leave_count

            if dept in counts and position in counts[dept]:
                counts[dept][position]["leaves"] += leave_count

        return jsonify({'code': 200, 'data': counts})  # Adjust the response structure if necessary

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500  # Return error with status code



if __name__ == '__main__':
    app.run(port=5100)
