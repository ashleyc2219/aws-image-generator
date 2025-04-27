# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements.txt first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Copy .env file specifically
COPY ./.env .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Note: Environment variables will be passed at runtime