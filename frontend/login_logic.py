import http.server
import json
import mysql.connector
import bcrypt  # For password hashing verification
from mysql.connector import Error
import os

db_host = os.getenv('MYSQL_HOST', 'database')
db_user = os.getenv('MYSQL_USERNAME', 'root')
db_password = os.getenv('MYSQL_PASSWORD', 'example')
db_name = 'employee'  # Use the correct database name for the user service

# Function to retrieve a user by email from the MySQL database
def get_user_by_email(email):
    try:
        # Establish a connection to the database
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=3306  # Use Docker's default MySQL port

        )
        cursor = conn.cursor(dictionary=True)  # Fetch results as dictionaries

        # Query to fetch user details based on email
        query = "SELECT * FROM employee WHERE Email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()  # Fetch one result (email should be unique)

        return user  # Returns None if no user is found

    except Error as e:
        print(f"Error retrieving user: {e}")
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Class to handle HTTP requests for the login process
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    
    # Serve HTML files and other static content
    def do_GET(self):
        if self.path == "/":
            self.path = "/login.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    # Handle POST requests
    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            print(f"Request body: {body}")  # Debugging log
            data = json.loads(body)

            email = data.get('email')
            password = data.get('password')
            print(f"Email: {email}, Password: {password}")  # Debug log
            

            # Retrieve user from the database based on email
            user = get_user_by_email(email)
            print(f"Retrieved user: {user}")  # Debugging user data

            if user and bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
                print(f"Hashed password from DB: {user['Password']}")  # This prints the hashed password from the database
                print(f"Password provided: {password}")  # This should show the plain-text password entered by Derek
                # Password matches, respond with success and user role
                response_data = {
                    'success': True,
                    'staff_id': user['Staff_ID'],
                    'firstname': user['Staff_FName'],
                    'lastname': user['Staff_LName'],
                    'dept': user['Dept'],
                    'role': user['Role'],
                    'position': user['Position'],
                    'country': user['Country'],
                    'email': user['Email'],
                    'reportingmanager': user['Reporting_Manager']
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                # Allow CORS
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
            else:
                print("Password does not match")  # Debug log
                # Authentication failed, respond with error
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': 'Invalid email or password'}).encode())
        else:
            # If the path is not /login, return a 404 not found error
            self.send_response(404)
            self.end_headers()

# Main function to run the HTTP server
if __name__ == '__main__':
    PORT = 8000  # The port to run the server on
    server_address = ('0.0.0.0', PORT)  # Change this line to allow access from all interfaces
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    print(f'Server running on http://localhost:{PORT}')
    httpd.serve_forever()
