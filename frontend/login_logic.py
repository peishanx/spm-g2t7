import http.server
import json
import mysql.connector
import bcrypt
from mysql.connector import Error
import os

db_host = os.getenv('MYSQL_HOST', 'database')
db_user = os.getenv('MYSQL_USERNAME', 'root')
db_password = os.getenv('MYSQL_PASSWORD', 'example')
db_name = 'employee'

def get_user_by_email(email):
    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=3306
        )
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM employee WHERE Email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"Error retrieving user: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.path = "/login.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            email = data.get('email')
            password = data.get('password')

            user = get_user_by_email(email)

            if user and bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
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

                response_json = json.dumps(response_data).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', str(len(response_json)))
                self.end_headers()
                self.wfile.write(response_json)
            else:
                error_response = json.dumps({'success': False, 'message': 'Invalid email or password'}).encode('utf-8')
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', str(len(error_response)))
                self.end_headers()
                self.wfile.write(error_response)
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    PORT = 8000
    server_address = ('0.0.0.0', PORT)
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    print(f'Server running on http://localhost:{PORT}')
    httpd.serve_forever()
