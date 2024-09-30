import http.server
import json
import mysql.connector
import bcrypt  # For password hashing verification
from mysql.connector import Error

# Function to retrieve a user by email from the MySQL database
def get_user_by_email(email):
    try:
        # Establish a connection to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Your MySQL root password, update if needed
            database="employee"  # The database you created with the employee table
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
    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            email = data.get('email')
            password = data.get('password')

            # Retrieve user from the database based on email
            user = get_user_by_email(email)

            if user and bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
                # Password matches, respond with success and user role
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'role': user['Role']}).encode())
            else:
                # Authentication failed, respond with error
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': 'Invalid email or password'}).encode())
        else:
            # If the path is not /login, return a 404 not found error
            self.send_response(404)
            self.end_headers()

# Main function to run the HTTP server
if __name__ == '__main__':
    PORT = 8000  # The port to run the server on
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    print(f'Server running on http://localhost:{PORT}')
    httpd.serve_forever()
