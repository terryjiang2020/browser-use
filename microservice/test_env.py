#!/usr/bin/env python3
"""
Test script to verify environment variables are being loaded correctly
for the single .env file multi-instance setup.
"""

import os
from dotenv import load_dotenv

def test_env_variables():
    """Test that environment variables are loaded correctly."""
    
    # Load environment variables from .env file  
    # Check if we're in microservice directory, if so go up one level
    current_dir = os.getcwd()
    if current_dir.endswith('microservice'):
        env_path = '../.env'
    else:
        env_path = '.env'
    
    load_dotenv(env_path)
    
    print("🔍 Environment Variables Test")
    print("=" * 50)
    print(f"Loading .env from: {os.path.abspath(env_path)}")
    print(f"File exists: {os.path.exists(env_path)}")
    print("=" * 50)
    
    # Test critical variables
    critical_vars = [
        'INSTANCE_ID',
        'PORT', 
        'AWS_REGION',
        'AWS_SQS_QUEUE_URL',  # Your actual variable name
        'OPENAI_API_KEY',
        'TABLE_NAME',
        'OPENSEARCH_INDEX_NAME'
    ]
    
    print("\n📋 Critical Variables:")
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'SAK' in var or 'SECRET' in var:
                masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                masked_value = value
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    # Test instance-specific variables
    print(f"\n🏷️ Instance Configuration:")
    print(f"Instance ID: {os.getenv('INSTANCE_ID', 'NOT SET')}")
    print(f"Port: {os.getenv('PORT', 'NOT SET')}")
    print(f"Table Name: {os.getenv('TABLE_NAME', 'NOT SET')}")
    print(f"OpenSearch Index: {os.getenv('OPENSEARCH_INDEX_NAME', 'NOT SET')}")
    
    # Test performance variables
    print(f"\n⚡ Performance Settings:")
    print(f"Max Concurrent Jobs: {os.getenv('MAX_CONCURRENT_JOBS', 'NOT SET')}")
    print(f"Worker Threads: {os.getenv('WORKER_THREADS', 'NOT SET')}")
    print(f"Max Browsers: {os.getenv('MAX_CONCURRENT_BROWSERS', 'NOT SET')}")
    
    # Test AWS configuration
    print(f"\n☁️ AWS Configuration:")
    aws_region = os.getenv('AWS_REGION', 'NOT SET')
    AWS_SQS_QUEUE_URL = os.getenv('AWS_SQS_QUEUE_URL', 'NOT SET')  # Your actual variable name
    print(f"Region: {aws_region}")
    print(f"SQS URL: {AWS_SQS_QUEUE_URL[:50]}..." if len(AWS_SQS_QUEUE_URL) > 50 else f"SQS URL: {AWS_SQS_QUEUE_URL}")
    
    print("\n" + "=" * 50)
    print("✅ Environment test completed!")

if __name__ == "__main__":
    test_env_variables()
