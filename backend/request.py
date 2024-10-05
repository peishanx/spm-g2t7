from mysql.connector import Error

class Request:
    def __init__(self, db_connection):
        # Initialize with an instance of DatabaseConnection
        self.db_connection = db_connection

    def get_wfh_request_by_rid(self, rid):
        if not self.db_connection.connection:
            print("No database connection.")
            return None

        try:
            cursor = self.db_connection.connection.cursor(dictionary=True)
            query = "SELECT * FROM request WHERE rid = %s"
            cursor.execute(query, (rid,))
            result = cursor.fetchone()

            if result:
                return result
            else:
                print(f"No request found with rid {rid}")
                return None
        except Error as e:
            print(f"Error fetching request: {e}")
            return None

    def add_wfh_request(self, sid, request_type):
        # Add a new WFH request for a specific employee (sid) and request type
        if not self.db_connection.connection:
            print("No database connection.")
            return False

        try:
            cursor = self.db_connection.connection.cursor()
            query = """
                INSERT INTO request (sid, type) 
                VALUES (%s, %s)
            """
            cursor.execute(query, (sid, request_type))
            self.db_connection.connection.commit()
            print(f"WFH request added successfully with rid {cursor.lastrowid}")
            return True
        except Error as e:
            print(f"Error adding request: {e}")
            return False

    def approve_wfh_request(self, rid):
        #Update the status of a WFH request from 'Pending' to 'Approved' by its rid
        if not self.db_connection.connection:
            print("No database connection.")
            return False

        try:
            cursor = self.db_connection.connection.cursor()
            query = """
                UPDATE request 
                SET status = 'Approved'
                WHERE rid = %s AND status = 'Pending'
            """
            cursor.execute(query, (rid,))
            self.db_connection.connection.commit()

            if cursor.rowcount > 0:
                print(f"WFH request {rid} approved successfully.")
                return True
            else:
                print(f"No pending WFH request found with rid {rid} or request already approved.")
                return False
        except Error as e:
            print(f"Error approving request: {e}")
            return False

    def reject_wfh_request(self, rid):
        #Update the status of a WFH request from 'Pending' to 'Rejected' by its rid
        if not self.db_connection.connection:
            print("No database connection.")
            return False

        try:
            cursor = self.db_connection.connection.cursor()
            query = """
                UPDATE request 
                SET status = 'Rejected'
                WHERE rid = %s AND status = 'Pending'
            """
            cursor.execute(query, (rid,))
            self.db_connection.connection.commit()

            if cursor.rowcount > 0:
                print(f"WFH request {rid} rejected successfully.")
                return True
            else:
                print(f"No pending WFH request found with rid {rid} or request already processed.")
                return False
        except Error as e:
            print(f"Error rejecting request: {e}")
            return False
