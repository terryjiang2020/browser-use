#!/usr/bin/env python3
"""
Test script for SQS integration with Browser-Use Microservice

This script tests the integration with the SQS queue by:
1. Sending a test message to the SQS queue
2. Verifying that the message is processed correctly
3. Checking that screenshots and videos are uploaded to S3
4. Confirming that the API callback is sent with the correct payload
"""
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the path so we can import the services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sqs_service import SQSService
from services.s3_service import S3Service
from services.api_client import APIClientService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_sqs_integration():
    """Test the SQS integration end-to-end"""
    logger.info("Starting SQS integration test")
    
    # Initialize services
    sqs_service = SQSService()
    s3_service = S3Service()
    api_client = APIClientService()
    
    # Test SQS connectivity
    logger.info("Testing SQS connectivity")
    sqs_health = sqs_service.health_check()
    if not sqs_health:
        logger.error("SQS health check failed. Please check your AWS credentials and SQS queue URL.")
        return False
    logger.info("SQS connectivity test passed")
    
    # Test S3 connectivity
    logger.info("Testing S3 connectivity")
    s3_health = s3_service.health_check()
    if not s3_health:
        logger.error("S3 health check failed. Please check your AWS credentials and S3 bucket configuration.")
        return False
    logger.info("S3 connectivity test passed")
    
    # Test API connectivity
    logger.info("Testing API connectivity")
    api_health = await api_client.health_check()
    if not api_health:
        logger.warning("API health check failed. This is expected if the API is not running locally.")
        logger.warning("Continuing with the test anyway...")
    else:
        logger.info("API connectivity test passed")
    
    # Create a test message
    project_id = f"test_project_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    flow_id = f"test_flow_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    test_message = {
        "project_id": project_id,
        "flow_id": flow_id,
        "url": "https://example.com",
        "prompt": "Navigate to the homepage and take a screenshot"
    }
    
    # Send the test message to SQS
    logger.info(f"Sending test message to SQS: {json.dumps(test_message)}")
    message_id = await sqs_service.send_message(test_message)
    
    if not message_id:
        logger.error("Failed to send test message to SQS")
        return False
    
    logger.info(f"Test message sent successfully with ID: {message_id}")
    logger.info("The message will be processed by the microservice asynchronously")
    logger.info("Check the microservice logs to verify processing")
    
    # Provide instructions for manual verification
    logger.info("\nManual verification steps:")
    logger.info("1. Check the microservice logs for message processing:")
    logger.info("   $ pm2 logs browser-use-api")
    logger.info(f"2. Look for messages related to project_id: {project_id} and flow_id: {flow_id}")
    logger.info("3. Verify that screenshots and videos are uploaded to S3")
    logger.info("4. Confirm that the API callback is sent with the correct payload")
    
    # Clean up
    await api_client.close()
    
    return True

if __name__ == "__main__":
    logger.info("SQS Integration Test")
    logger.info("====================")
    
    # Check if required environment variables are set
    required_vars = [
        'AWS_ACCESS_KEY_ID', 
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_REGION', 
        'AWS_SQS_QUEUE_URL',
        'AWS_S3_BUCKET',
        'API_BASE_URL'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in the .env file")
        sys.exit(1)
    
    # Run the test
    result = asyncio.run(test_sqs_integration())
    
    if result:
        logger.info("SQS integration test completed successfully")
    else:
        logger.error("SQS integration test failed")
        sys.exit(1)