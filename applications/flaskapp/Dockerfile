FROM python:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos '' flaskuser && \
    chown -R flaskuser:flaskuser /app

USER flaskuser

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "3"]
