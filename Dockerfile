# Dockerfile
# Recipe for building our ReguMind application container
# This tells Docker exactly how to set up our Python environment

# Start from official Python 3.11 image
# This is like starting with a clean computer that has Python installed
FROM python:3.11-slim

# Set working directory inside the container
# All our code will live at /app inside the container
WORKDIR /app

# Copy requirements file first
# We do this before copying code because Docker caches layers
# If requirements haven't changed, it skips reinstalling packages
COPY requirements.txt .

# Install all Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all our project code into the container
COPY . .

# Tell Docker that our app uses port 8000
EXPOSE 8000

# Default command to run when container starts
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]