# FROM python:3-slim
# WORKDIR /usr/src/app
# COPY requirements.txt ./
# RUN python -m pip install --no-cache-dir -r requirements.txt
# COPY ./request.py .
# CMD [ "python", "./request.py" ]
FROM python:3-slim

# Set the working directory
WORKDIR /usr/src/app
# Install curl
RUN apt-get update && apt-get install -y curl && apt-get clean
# Copy only requirements.txt first for caching purposes
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./request.py .

# Optionally expose the port
EXPOSE 5200

# Run the application
CMD ["python", "./request.py"]
