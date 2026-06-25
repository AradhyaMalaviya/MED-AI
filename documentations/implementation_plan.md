# Implementation Plan - Day 8: Containerization & Deployment Prep

This document details the exact, step-by-step action plan to containerize, configure, and prepare the **MediCare AI** application for production deployment using Docker, Docker Compose, and Gunicorn.

## Proposed Changes

All files created or referenced in this plan belong to the application root directory:  
[medicare/medicare](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20&%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare)

---

### Step 1: Create `.dockerignore`
#### [NEW] [.dockerignore](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20&%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/.dockerignore)

This file prevents unnecessary files (large test coverage folders, virtual environments, local environment configurations containing keys, etc.) from being copied into the Docker build context.

**File Contents:**
```text
# Virtual Environments
venv/
.venv/
env/

# Python Build & Caches
**/__pycache__/
*.py[cod]
*$py.class
.pytest_cache/

# Coverage reports
.coverage
htmlcov/

# Version Control
.git/
.gitignore

# Environment Configurations & Secrets
.env
.env.local

# IDE configurations
.vscode/
.idea/
```

---

### Step 2: Create the `Dockerfile`
#### [NEW] [Dockerfile](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20&%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/Dockerfile)

This configuration builds a lightweight production-ready image using Python 3.11 slim, sets up proper environment variables to optimize Python within Docker, exposes the application port, implements a healthcheck targeting the `/health` endpoint, and uses Gunicorn as the entry point.

**File Contents:**
```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to optimize Python execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system-level dependencies for healthcheck/network tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose port 5000 for local or cloud mapping
EXPOSE 5000

# Add a healthcheck to ensure the container is running and healthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start the Flask app using Gunicorn production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--timeout", "60", "app:app"]
```

---

### Step 3: Create `docker-compose.yml`
#### [NEW] [docker-compose.yml](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20&%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/docker-compose.yml)

Docker Compose simplifies running the containerized service locally with options for volume mounting (supporting template updates during development) and environment variable management.

**File Contents:**
```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: medicare-ai:latest
    container_name: medicare_api_server
    ports:
      - "5000:5000"
    volumes:
      # Bind mount current directory to /app for development (hot-reloading assets)
      - .:/app
      # Exclude venv directory inside container from being overridden by local files
      - /app/venv/
    env_file:
      - .env.example
    environment:
      - PORT=5000
      - HOST=0.0.0.0
      - DEBUG=false
    restart: always
```

---

### Step 4: Gunicorn Production Verification
#### [MODIFY] [requirements.txt](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20&%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/requirements.txt)
We verify that `gunicorn>=22.0.0` is indeed pinned inside [requirements.txt](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20&%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/requirements.txt). No code modifications are needed on [app.py](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20&%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/app.py) because printing statements have already been replaced with standard python logging using the `'medicare'` logger, preventing potential buffer bottlenecks inside Gunicorn workers.

---

## Verification Plan

Here is the exact action-by-action command list to build, run, and verify the containerized application.

### Command Execution Steps (Local CLI)

1. **Verify Local Gunicorn Execution**:
   Verify that Gunicorn starts the application successfully without Docker first:
   ```powershell
   cd "C:\Users\deepa\Downloads\NEW PROJECT\Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)\medicare\medicare"
   .\venv\Scripts\Activate.ps1
   gunicorn --bind 0.0.0.0:5000 app:app
   ```
   *Expected Outcome*: The terminal logs confirm that Gunicorn has spawned worker processes and is listening on `http://0.0.0.0:5000`. Stop Gunicorn with `Ctrl+C` after verification.

2. **Build and Run via Docker**:
   Build the Docker image manually and check the local build steps:
   ```powershell
   docker build -t medicare-ai .
   ```
   *Expected Outcome*: Command executes successfully, displaying output for all steps (1 through 9) in the Dockerfile.

3. **Run the Docker Container**:
   Run the newly built container in background/detached mode:
   ```powershell
   docker run -d -p 5000:5000 --name medicare_test_container medicare-ai
   ```
   *Expected Outcome*: Returns the container ID. Verify it is running via `docker ps`.

4. **Verify Health Endpoint and Logs**:
   ```powershell
   curl http://localhost:5000/health
   docker logs medicare_test_container
   ```
   *Expected Outcome*: `curl` returns `{"status":"healthy","model_loaded":true,"encoder_loaded":true}`. `docker logs` displays the Gunicorn initialization and HTTP request records.

5. **Clean up Docker Run**:
   ```powershell
   docker stop medicare_test_container
   docker rm medicare_test_container
   ```

6. **Validate via Docker Compose**:
   Initialize the system using Docker Compose:
   ```powershell
   docker-compose up -d
   ```
   *Expected Outcome*: Docker Compose starts the service. Confirm again via `curl http://localhost:5000/health`.

7. **Tear down Docker Compose**:
   ```powershell
   docker-compose down
   ```
