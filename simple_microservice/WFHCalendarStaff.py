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
        # Get the date range: past 30 days to upcoming 30 days
        today = datetime.now().date()
        past_30_days = today - timedelta(days=30)
        future_30_days = today + timedelta(days=30)

        # Fetch all approved requests within the date range for this employee
        requests = db.session.query(Request).filter(
            Request.sid == sid,
            Request.status == "Approved",
            Request.request_date.between(past_30_days, future_30_days)
        ).all()

        # Debug: Print the retrieved requests
        print(f"Retrieved requests for SID {sid}: {[req.request_date for req in requests]}")

        events = []
        current_date = past_30_days  # Start from 30 days before today

        # Loop through past 30 days to future 30 days
        while current_date <= future_30_days:
            has_wfh = False

            for req in requests:
                if req.request_date == current_date:
                    has_wfh = True
                    print(f"Found WFH request for {current_date}: {req.wfh_type}")  # Debug

                    # Correctly handle different WFH types
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
                    break  # Exit the loop after processing the request

            # If no WFH request for this date and it's a weekday, add an "In Office" event
            if not has_wfh and current_date.weekday() < 5:
                events.append({
                    "title": "In Office (Full Day)",
                    "start": f"{current_date}T09:00:00",
                    "end": f"{current_date}T17:00:00"
                })

            current_date += timedelta(days=1)

        # Debug: Print events being returned
        print("Events being returned:", events)

        return jsonify({"code": 200, "data": events}), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "An error occurred while retrieving the WFH calendar. " + str(e)
        }), 500


if __name__ == "__main__":
    app.run(port=5201, debug=True)
