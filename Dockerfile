# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi.py

# Set work directory
WORKDIR /app

# Install system dependencies (if needed for libraries like Pillow or Postgres)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose the port Gunicorn will listen on
EXPOSE 8080

# Start Gunicorn
# -w 4: Use 4 worker processes (adjust based on CPU cores)
# --access-logfile -: Log to stdout
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--access-logfile", "-", "wsgi:app"]