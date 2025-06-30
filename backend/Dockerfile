# Start with an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (if any, e.g., for psycopg2 if not using binary)
# RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install pipenv (if using Pipfile, otherwise skip)
# RUN pip install pipenv

# Copy requirements files
COPY requirements/base.txt requirements/base.txt
# If you have prod requirements, copy them too
# COPY requirements/prod.txt requirements/prod.txt

# Install dependencies
# If using pipenv:
# COPY Pipfile Pipfile.lock ./
# RUN pipenv install --system --deploy --ignore-pipfile
# If using requirements.txt:
RUN pip install --no-cache-dir -r requirements/base.txt
# For production, you might use:
# RUN pip install --no-cache-dir -r requirements/prod.txt


# Copy the rest of the application code
COPY . .

# Expose port 8000 (or whatever port your app runs on)
EXPOSE 8000

# Command to run the application
# For development with Uvicorn and reload (not recommended for production image)
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# For production with Uvicorn
# The run.py script can also be used if it's configured for production
# CMD ["python", "run.py"]
# Or directly use Uvicorn with gunicorn or multiple workers:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# If using Gunicorn as a process manager for Uvicorn workers (more robust for production)
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/gunicorn_conf.py", "app.main:app"]
# You would need a gunicorn_conf.py file and gunicorn in requirements.
# Example gunicorn_conf.py:
# bind = "0.0.0.0:8000"
# workers = 4 # Adjust based on your server's CPU cores
# worker_class = "uvicorn.workers.UvicornWorker"
# loglevel = "info"
# accesslog = "-"
# errorlog = "-"
