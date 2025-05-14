#!/bin/bash

# Set project directory
PROJECT_DIR="/home/ubuntu/acadex"

# Activate the virtual environment (adjust path if needed)
source $PROJECT_DIR/.venv/bin/activate

# Start Gunicorn with Uvicorn worker for async support
gunicorn --workers 3 --worker-class uvicorn.workers.UvicornWorker acadex.asgi:application --bind 0.0.0.0:8000 --daemon

# Deactivate virtual environment when done
deactivate
