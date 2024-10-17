import subprocess

# Start the employee service
subprocess.Popen(["python", "employee/employee.py"])

# Start the request service
subprocess.Popen(["python", "request/request.py"])
