# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app
# Install curl
RUN apt-get update && apt-get install -y curl && apt-get clean
# Copy frontend's requirements.txt from the root context
COPY requirements.txt . 

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all frontend contents
COPY . .

# Expose the port that your frontend service runs on
EXPOSE 8000

# Command to run your frontend script
CMD ["python", "login_logic.py"]
