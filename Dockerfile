# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container
COPY . /app
# Set environment variables
EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "TrainingManagementSystem.wsgi:application"]
