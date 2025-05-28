#!/usr/bin/env python3
"""
Test script for the browser-use microservice AWS integration
"""

import json
import requests
import time

# Microservice endpoint
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_service_status():
    """Test the service status endpoint"""
    print("📊 Testing service status...")
    response = requests.get(f"{BASE_URL}/api/v1/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_legacy_task_creation():
    """Test the legacy task creation endpoint"""
    print("🎯 Testing legacy task creation...")
    
    task_data = {
        "task": "Go to google.com and search for 'browser automation'",
        "timeout": 60
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/tasks", json=task_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        task_id = response.json()["task_id"]
        print(f"📋 Task created with ID: {task_id}")
        
        # Check task status
        print("⏳ Checking task status...")
        time.sleep(2)
        
        status_response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}")
        print(f"Status: {status_response.status_code}")
        print(f"Response: {json.dumps(status_response.json(), indent=2)}")
    
    print()

def test_sqs_message_simulation():
    """Test the SQS message simulation endpoint"""
    print("📨 Testing SQS message simulation...")
    
    # Note: This will fail with AWS errors if credentials aren't configured
    # but will demonstrate the endpoint functionality
    
    sqs_data = {
        "project_id": "test_project_123",
        "flow_id": "test_flow_456",
        "url": "https://google.com",
        "prompt": "Navigate to Google and search for 'browser automation'"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/sqs/test", json=sqs_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
        print("Note: This is expected if AWS credentials are not configured")
    
    print()

if __name__ == "__main__":
    print("🚀 Testing Browser Use Microservice with AWS Integration")
    print("=" * 60)
    print()
    
    try:
        test_health_check()
        test_service_status()
        test_legacy_task_creation()
        test_sqs_message_simulation()
        
        print("✅ Testing completed!")
        print()
        print("Next steps:")
        print("1. Configure AWS credentials in .env file")
        print("2. Set up SQS queue and S3 bucket")
        print("3. Configure your API callback URL")
        print("4. Send real messages to your SQS queue")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to microservice")
        print("Make sure the service is running: pm2 status")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
