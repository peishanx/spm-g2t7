from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timedelta

app = Flask(__name__)

# Allow requests from localhost:8000
CORS(app, resources={r"/request/*": {"origins": "http://localhost:8000"}})
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root:@localhost:3306/request"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Request(db.Model):
    __tablename__ = "request"

    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sid = db.Column(db.Integer, nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    wfh_type = db.Column(db.String(50))
    status = db.Column(db.String(50), default="Pending")
    createdAt = db.Column(db.TIMESTAMP(timezone=True), default=db.func.current_timestamp(), nullable=False)

@app.route("/request/employee/<int:sid>", methods=["GET"])
def get_wfh_calendar(sid):
    try:
        # Get all approved requests for the specific employee
        requests = db.session.query(Request).filter_by(sid=sid, status="Approved").all()
        
        # Extract all unique request dates
        request_dates = {req.request_date for req in requests}
        
        # Create a list for events
        events = []

        # Define the number of days you want to show. For example, let's show the next 30 days.
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=30)
        
        # Loop through each day in the defined date range
        current_date = start_date
        while current_date <= end_date:
            # Check if there's a WFH request for that date
            if current_date in request_dates:
                # Add the WFH events based on the type
                for req in requests:
                    if req.request_date == current_date:
                        if req.wfh_type == "AM":
                            events.append({
                                "title": "WFH (AM)",
                                "start": f"{current_date}T09:00:00",
                                "end": f"{current_date}T12:00:00"
                            })
                            events.append({
                                "title": "In Office (PM)",
                                "start": f"{current_date}T13:00:00",
                                "end": f"{current_date}T17:00:00"
                            })
                        elif req.wfh_type == "PM":
                            events.append({
                                "title": "WFH (PM)",
                                "start": f"{current_date}T13:00:00",
                                "end": f"{current_date}T17:00:00"
                            })
                            events.append({
                                "title": "In Office (AM)",
                                "start": f"{current_date}T09:00:00",
                                "end": f"{current_date}T12:00:00"
                            })
                        elif req.wfh_type == "Full Day":
                            events.append({
                                "title": "WFH (Full Day)",
                                "start": f"{current_date}T09:00:00",
                                "end": f"{current_date}T17:00:00"
                            })
            else:
                # If no WFH requests, add In Office Full Day event
                events.append({
                    "title": "In Office (Full Day)",
                    "start": f"{current_date}T09:00:00",
                    "end": f"{current_date}T17:00:00"
                })

            # Move to the next day
            current_date += timedelta(days=1)

        return jsonify({"code": 200, "data": events}), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "An error occurred while retrieving the WFH calendar. " + str(e)
        }), 500

if __name__ == "__main__":
    app.run(port=5201, debug=True)
