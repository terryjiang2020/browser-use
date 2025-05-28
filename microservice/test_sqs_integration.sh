#!/bin/bash
# Test script for SQS integration with Browser-Use Microservice

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Error: .env file not found"
  exit 1
fi

# Make the test script executable
chmod +x test_sqs_integration.py

# Run the test script
python3 test_sqs_integration.py