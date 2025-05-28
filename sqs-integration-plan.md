# SQS Integration Plan for Browser-Use Microservice

## Overview

This document outlines the plan to modify the Browser-Use microservice to subscribe to a specific SQS queue and implement the required functionality.

## Requirements

1. Subscribe to SQS queue: `https://sqs.ap-southeast-2.amazonaws.com/281584859358/BrowserUse-Test-1`
2. Extract URL and prompt from SQS messages
3. Perform browser automation tasks based on the URL and prompt
4. Upload generated screenshots and videos to S3
5. Send a request to the backend API at `POST /project/session/create` with the URLs of the video and screenshot

## Current Architecture

The microservice already has most of the required functionality:

- **SQS Integration**: The `SQSService` class handles polling messages from an SQS queue
- **Message Processing**: The `MessageProcessor` class processes messages and orchestrates the workflow
- **Browser Automation**: The `BrowserAgentService` handles browser automation tasks
- **S3 Upload**: The `S3Service` uploads screenshots and videos to S3
- **API Callback**: The `APIClientService` sends results back to an API endpoint

## Implementation Steps

### 1. Update Environment Configuration

Update the `.env` file with the new SQS queue URL and region:

```
# AWS Configuration
AWS_REGION=ap-southeast-2
AWS_SQS_QUEUE_URL=https://sqs.ap-southeast-2.amazonaws.com/281584859358/BrowserUse-Test-1
```

### 2. Verify Message Processing Logic

The current message processor already handles:
- Extracting URL and prompt from messages
- Running browser automation tasks
- Uploading media to S3
- Sending results to the API

The expected message format is:
```json
{
  "project_id": "proj_123",
  "flow_id": "flow_456",
  "url": "https://example.com",
  "prompt": "Navigate to the homepage and take a screenshot"
}
```

### 3. Test SQS Connectivity

Use the existing health check endpoint to verify connectivity to the new SQS queue:
```
GET /health
```

### 4. Send a Test Message

Use the existing test endpoint to send a message to the SQS queue:
```
POST /api/v1/sqs/test
```
With payload:
```json
{
  "project_id": "test_project",
  "flow_id": "test_flow",
  "url": "https://example.com",
  "prompt": "Navigate to the homepage and take a screenshot"
}
```

### 5. Monitor Processing

Monitor the logs to ensure the message is processed correctly:
```
pm2 logs browser-use-api
```

### 6. Verify S3 Upload

Check the S3 bucket to confirm that screenshots and videos are uploaded correctly.

### 7. Verify API Callback

Confirm that the API callback is sent with the correct payload to the specified endpoint.

## Testing Strategy

1. **Unit Testing**: Test individual components (SQS service, S3 service, API client)
2. **Integration Testing**: Test the end-to-end flow from SQS message to API callback
3. **Error Handling**: Test error scenarios (SQS connectivity issues, S3 upload failures, API callback failures)

## Potential Challenges and Solutions

1. **SQS Message Format**: If the message format from the new SQS queue differs from the expected format, we may need to update the message parsing logic in `sqs_service.py`.

2. **AWS Region Configuration**: Ensure that all AWS services (SQS, S3) are configured to use the same region (ap-southeast-2).

3. **Error Handling**: Implement robust error handling for SQS polling, browser automation, S3 uploads, and API callbacks.

## Implementation Files

The following files need to be modified:

1. `microservice/.env` - Update AWS region and SQS queue URL
2. Potentially `microservice/services/sqs_service.py` - If message format adjustments are needed
3. Potentially `microservice/services/message_processor.py` - If processing logic adjustments are needed

## Verification Steps

After implementation, verify the following:

1. The microservice successfully connects to the SQS queue
2. Messages are properly processed
3. Browser automation tasks are executed correctly
4. Screenshots and videos are uploaded to S3
5. API callbacks are sent with the correct payload

## Rollback Plan

If issues arise:

1. Revert the `.env` file to use the original SQS queue URL and region
2. Restart the microservice
3. Verify connectivity to the original SQS queue