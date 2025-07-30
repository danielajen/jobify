#!/bin/bash
# Absolute paths
PROJECT_ROOT="/Users/aje/jobswipe-app/backend"
VENV_PATH="$PROJECT_ROOT/venv"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Set Python paths
export PYTHONPATH="$PROJECT_ROOT:$VENV_PATH/lib/python3.11/site-packages:$PYTHONPATH"

# Run Celery
"$VENV_PATH/bin/python" -m celery -A app.celery worker --loglevel=info