FROM python:3-slim
WORKDIR /usr/src/app

COPY simple_microservice/employee/requirements.txt ./ 
RUN python -m pip install --no-cache-dir -r requirements.txt 

# Correctly copy the setup script and CSV file
COPY database/employee_setup.py ./ 
COPY database/employeenew.csv ./ 

# Copy the employee script
COPY simple_microservice/employee/employee.py . 

CMD ["sh", "-c", "python employee_setup.py && python employee.py"]
