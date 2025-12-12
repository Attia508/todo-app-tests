# Dockerfile for Todo Application
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/ templates/

# Create instance directory for SQLite database
RUN mkdir -p /app/instance

# Expose port
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]
