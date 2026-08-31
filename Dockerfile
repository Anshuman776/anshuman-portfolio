# Use official Python runtime as base image
FROM python:3.12-slim

# Set metadata
LABEL maintainer="Anshuman Maurya <anshumanmaurya776@gmail.com>"
LABEL description="AI/ML Engineer Portfolio - Production Build"

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install system dependencies if any are needed (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code into container working directory
COPY . .

# Create templates and static directories if not present
RUN mkdir -p templates static && chmod -R 755 templates static

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port the web service runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI web app using Gunicorn + Uvicorn workers for production
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
