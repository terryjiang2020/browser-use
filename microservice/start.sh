#!/bin/bash

# Start script for browser-use microservice
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Set Python path to include both microservice and browser-use directories
export PYTHONPATH="${SCRIPT_DIR}:${SCRIPT_DIR}/../"

# Start the FastAPI application
python -m uvicorn app:app --host 0.0.0.0 --port 8000
