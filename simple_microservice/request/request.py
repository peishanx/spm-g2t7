from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS
import os
import sys
import math
import pytz

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root:example@localhost:3306/request"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 299}

db = SQLAlchemy(app)

CORS(app)

class Request(db.Model):
    __tablename__ = "request"

    rid = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    createdAt = db.Column(db.TIMESTAMP(timezone=True), default = db.func.current_timestamp(), nullable = False)

    def __init__(self, rid, sid, type, status="Pending"):
        self.rid = rid
        self.sid = sid
        self.type = type
        self.status = status
    
    def json(self):
        return {
            "rid": self.rid,
            "sid": self.sid,
            "type": self.type,
            "status": self.status,
            "createdAt": self.createdAt
        }
    
@app.route("/request", methods = ["POST"])
def create_request():
    data = request.get_json()

    # rid = data.get("rid")
    sid = data.get("sid")
    type = data.get("type")

    if sid is None or type is None:
        return jsonify(
        {
                "code": 400,
                "message": "Missing required parameter(s)."
        }
        ),400
    new_request = Request(rid=None, sid=sid, type=type)

    try:
        db.session.add(new_request)
        db.session.commit()
        return jsonify({"code":201, "message": f"Employee {sid} has submitted request({new_request.rid}) successfully."}),201
    
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the queue. " + str(e)
             }
             ), 500

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

        request_entry.status = "Approved"
        db.session.commit()

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

        request_entry.status = "Rejected"
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



if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 5200, debug = True)