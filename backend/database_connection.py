import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """Establishes a connection to the database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                print(f"Connected to MySQL Server version {db_info}")
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            self.connection = None

    def close(self):
        """Closes the connection to the database."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")
