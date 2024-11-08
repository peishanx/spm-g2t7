import unittest
import json
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from io import BytesIO
import sys
import os
from werkzeug.datastructures import FileStorage

# Add path to access employee_leaves.py if required
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'employee_leaves')))

from simple_microservice.request.request2 import app as request_app, db as request_db, Request  # Use aliases for request app and db

class RequestTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ["TESTING"] = "1"  # Set the TESTING environment variable
        request_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        request_app.config['TESTING'] = True
        cls.client = request_app.test_client()

        with request_app.app_context():
            request_db.create_all()

    def setUp(self):
        self.app_context = request_app.app_context()
        self.app_context.push()
        self.connection = request_db.engine.connect()
        self.trans = self.connection.begin()

        # Add a sample request with a "Pending" status and non-null 'reason'
        self.sample_request = Request(
            sid=1,
            request_date=datetime.now().date(),
            wfh_type="Full Day",
            reason="Test Reason",
            status="Pending"
        )
        request_db.session.add(self.sample_request)
        request_db.session.commit()
        self.sample_rid = self.sample_request.rid
        print(f"[DEBUG] Created sample request with rid={self.sample_rid} and status='Pending'")

    def tearDown(self):
        self.trans.rollback()
        self.connection.close()
        self.app_context.pop()

    def log_response(self, response):
        print(f"Response Status Code: {response.status_code}")
        try:
            print("Response JSON:", response.get_json())
        except Exception as e:
            print("Error parsing response JSON:", e)

    def test_get_requests_by_rid(self):
        # Happy Path
        response = self.client.get(f'/request/employee/rid/{self.sample_rid}')
        self.log_response(response)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertIn("data", data)

        # Sad Path
        response = self.client.get('/request/employee/rid/99999')
        self.log_response(response)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        if data is not None:
            self.assertIn("message", data)

    @patch('request.requests.get')
    def test_get_requests_by_sid(self, mock_get):
        # Mock response for employee service
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "code": 200,
            "data": {"Staff_LName": "Doe", "Staff_FName": "John", "approval_count": 1, "Email": "john.doe@example.com"}
        }

        # Happy Path
        response = self.client.get(f'/request/employee/{self.sample_request.sid}')
        self.log_response(response)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertIn("data", data)

        # Sad Path
        response = self.client.get('/request/employee/99999')
        self.log_response(response)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        if data is not None:
            self.assertIn("message", data)

    @patch.object(FileStorage, 'save', lambda *args, **kwargs: None)
    def test_create_request(self):
        file_data = FileStorage(
            stream=BytesIO(b"sample data"),
            filename='sample.txt',
            content_type='text/plain'
        )

        data = {
            'sid': '2',
            'type': 'Full Day',
            'reason': 'Need to work from home',
            'email': 'test@example.com',
            'staff_fname': 'John',
            'staff_lname': 'Doe',
            'request_dates': [str(datetime.now().date())],
            'attachment': file_data
        }

        response = self.client.post('/request', data=data, content_type='multipart/form-data')
        self.log_response(response)
        self.assertEqual(response.status_code, 201)
    
    
    @patch('request.requests.get')
    @patch('request.requests.put')
    def test_approve_request(self, mock_put, mock_get):
        # Mock responses for employee data and approval count
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "code": 200,
            "data": {
                "approval_count": 3,  # Set to max to simulate limit check
                "Email": "john.doe@example.com",
                "Staff_FName": "John"
            }
        }

        # Attempt to approve should return an error because count has reached the limit
        response = self.client.put(f'/request/{self.sample_rid}/employee/1/reporting/2/approve')
        self.log_response(response)
        self.assertEqual(response.status_code, 404)  # Expecting a 404 error for count limit
        self.assertIn("message", response.get_json())

    @patch('request.requests.get')
    @patch('request.requests.put')
    def test_withdraw_request(self, mock_put, mock_get):
        # Mock employee data
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "code": 200,
            "data": {"approval_count": 1, "Email": "john.doe@example.com", "Staff_FName": "John"}
        }
        mock_put.return_value.status_code = 200

        response = self.client.put(f'/request/{self.sample_rid}/employee/1/reporting/2/withdraw', json={"additional_reason": "Not needed"})
        self.log_response(response)
        self.assertEqual(response.status_code, 200)

    @patch('request.requests.get')
    @patch('request.requests.put')
    def test_reject_request(self, mock_put, mock_get):
        # Mock employee data response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "code": 200,
            "data": {"approval_count": 1, "Email": "john.doe@example.com", "Staff_FName": "John"}
        }
        mock_put.return_value.status_code = 200

        # Reject request with valid reason
        response = self.client.put(
            f'/request/{self.sample_rid}/employee/1/reporting/2/reject',
            json={"additional_reason": "Not needed"}
        )
        self.log_response(response)
        self.assertEqual(response.status_code, 200)
    

if __name__ == "__main__":
    unittest.main()
