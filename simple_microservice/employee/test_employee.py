import unittest
from unittest.mock import patch, MagicMock
from employee import Employee, db, app  # Import the Flask app

class TestEmployee(unittest.TestCase):

    # Set up the Flask test client and application context
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('employee.db.session')
    def test_get_employee_by_staff_id_valid(self, mock_session):
        # Mocking the result of a query for a valid staff ID
        mock_query = MagicMock()
        mock_query.all.return_value = [
            Employee(Staff_ID=130002, Staff_FName='Jack', Staff_LName='Sim', Dept='CEO', Position='CEO', Country='SG', Email='jack@company.com', Reporting_Manager=None, Role=1)
        ]
        mock_session.query.return_value.filter_by.return_value = mock_query

        with self.app.app_context():  # Ensure you're in the app context
            response = self.app.get('/employee/130002')
            data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['Staff_FName'], 'Jack')

    @patch('employee.db.session')
    def test_get_employee_by_staff_id_invalid(self, mock_session):
        # Mocking an empty result for an invalid staff ID
        mock_query = MagicMock()
        mock_query.all.return_value = []  # No employee found
        mock_session.query.return_value.filter_by.return_value = mock_query

        with self.app.app_context():  # Ensure you're in the app context
            response = self.app.get('/employee/999999')
            data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertIn("Staff not found.", data['message'])

    @patch('employee.db.session')
    def test_get_all_employees(self, mock_session):
        # Mocking the result of all employees
        mock_query = MagicMock()
        mock_query.all.return_value = [
            Employee(Staff_ID=140001, Staff_FName='Susan', Staff_LName='Lim', Dept='Sales', Position='Manager', Country='SG', Email='susan@company.com', Reporting_Manager=None, Role=2),
            Employee(Staff_ID=140002, Staff_FName='Rahim', Staff_LName='Khan', Dept='Sales', Position='Sales Rep', Country='SG', Email='rahim@company.com', Reporting_Manager=None, Role=3)
        ]
        mock_session.query.return_value = mock_query

        with self.app.app_context():  # Ensure you're in the app context
            response = self.app.get('/employee/getallemployees')
            data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['data']), 2)

    @patch('employee.db.session')
    def test_filter_by_department_not_found(self, mock_session):
        # Mocking an empty result for a non-existent department
        mock_query = MagicMock()
        mock_query.all.return_value = []
        mock_session.query.return_value.filter_by.return_value = mock_query

        with self.app.app_context():  # Ensure you're in the app context
            response = self.app.get('/employee/filter/NonExistentDept')
            data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertIn("No employees found in the department NonExistentDept.", data['message'])

    @patch('employee.db.session')
    def test_filter_by_dept_and_role_equal(self, mock_session):
        # Mocking employees filtered by department and role with a condition
        mock_query = MagicMock()
        mock_query.all.return_value = [
            Employee(Staff_ID=130002, Staff_FName='Jack', Staff_LName='Sim', Dept='CEO', Position='CEO', Country='SG', Email='jack@company.com', Reporting_Manager=None, Role=1)
        ]
        mock_session.query.return_value.filter.return_value = mock_query

        with self.app.app_context():  # Ensure you're in the app context
            response = self.app.get('/employee/filter/CEO/1/equal')
            data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['data']), 1)

    @patch('employee.db.session')
    def test_filter_by_dept_and_role_not_equal(self, mock_session):
        # Mocking employees filtered by department and role with a condition
        mock_query = MagicMock()
        mock_query.all.return_value = [
            Employee(Staff_ID=130002, Staff_FName='Jack', Staff_LName='Sim', Dept='CEO', Position='CEO', Country='SG', Email='jack@company.com', Reporting_Manager=None, Role=1)
        ]
        mock_session.query.return_value.filter.return_value = mock_query

        with self.app.app_context():  # Ensure you're in the app context
            response = self.app.get('/employee/filter/CEO/2/not_equal')
            data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['data']), 1)

    @patch('employee.db.session')
    def test_update_approval_count(self, mock_session):
        # Mock the database and update approval count
        mock_employee = MagicMock()
        mock_employee.Staff_ID = 130002
        mock_employee.approval_count = 0
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_employee

        mock_session.commit = MagicMock()

        with self.app.app_context():  # Ensure you're in the app context
            response = self.app.put('/employee/130002/update_approval_count', json={'approval_count': 5})
            data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Approval count updated successfully", data['message'])

    @patch('employee.db.session')
    def test_update_approval_count_employee_not_found(self, mock_session):
        mock_session.query.return_value.filter_by.return_value.first.return_value = None

        with self.app.app_context():  # Ensure you're in the app context
            response = self.app.put('/employee/999999/update_approval_count', json={'approval_count': 5})
            data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertIn("Employee not found", data['message'])

if __name__ == '__main__':
    unittest.main()
