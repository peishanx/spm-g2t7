from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get("dbURL") or "mysql+mysqlconnector://root:@localhost:3306/request"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Request(db.Model):
    __tablename__ = "request"
    rid = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Integer, nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    wfh_type = db.Column(db.String(50))  # Ensure this matches your DB schema exactly
    status = db.Column(db.String(50), default="Pending")
    createdAt = db.Column(db.TIMESTAMP, server_default=db.func.now(), nullable=False)

    def json(self):
        # Debugging: print out all field values before returning them
        print(f"Debug - rid: {self.rid}, sid: {self.sid}, request_date: {self.request_date}, wfh_type: {self.wfh_type}, status: {self.status}, createdAt: {self.createdAt}")
        
        return {
            "rid": self.rid,
            "sid": self.sid,
            "request_date": self.request_date.isoformat(),  # Check this line is correctly referencing request_date
            "wfh_type": self.wfh_type,                      # Check this line is correctly referencing wfh_type
            "status": self.status,
            "createdAt": self.createdAt
        }

@app.route("/request/employee/<int:sid>", methods=["GET"])
def get_requests_by_sid(sid):
    try:
        # Query the database for approved requests
        requests = Request.query.filter_by(sid=sid, status='Approved').all()
        
        # Print each record to confirm fields
        data = []
        for req in requests:
            print(f"rid: {req.rid}, sid: {req.sid}, request_date: {req.request_date}, wfh_type: {req.wfh_type}, status: {req.status}, createdAt: {req.createdAt}")
            data.append(req.json())

        if not data:
            return jsonify({"code": 404, "message": "No approved requests found."}), 404
        return jsonify({"code": 200, "data": data}), 200

    except Exception as e:
        print("An error occurred:", e)
        return jsonify({"code": 500, "message": f"An error occurred: {str(e)}"}), 500

@app.before_request
def test_connection():
    try:
        db.session.execute(text('SELECT 1'))
        print("Database connection successful.")
    except Exception as e:
        print("Database connection failed:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5200, debug=True)
