# Use an official Python runtime as a parent image
FROM python:3.9-slim
# Install WeasyPrint dependencies
RUN apt-get update && apt-get install -y \
    libpango1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    libffi-dev \
    libssl-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && apt-get clean
# Set the working directory in the container
WORKDIR /app
# Collect static files
RUN python manage.py collectstatic --noinput

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container
COPY . /app
# Set environment variables
EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "TrainingManagementSystem.wsgi:application"]
