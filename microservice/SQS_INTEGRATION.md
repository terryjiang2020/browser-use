# SQS Integration for Browser-Use Microservice

This document explains how to set up and use the SQS integration for the Browser-Use microservice.

## Overview

The Browser-Use microservice can be triggered by messages from an AWS SQS queue. When a message is received, the microservice:

1. Extracts the URL and prompt from the message
2. Performs browser automation based on the URL and prompt
3. Uploads generated screenshots and videos to S3
4. Sends a request to the backend API with the URLs of the video and screenshot

## Configuration

### Environment Variables

The following environment variables must be set in the `.env` file:

```
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-southeast-2

# SQS Configuration
AWS_SQS_QUEUE_URL=https://sqs.ap-southeast-2.amazonaws.com/281584859358/BrowserUse-Test-1

# S3 Configuration
AWS_S3_BUCKET=your_s3_bucket
AWS_S3_REGION=ap-southeast-2

# API Configuration
API_BASE_URL=your_api_base_url
```

### Message Format

The SQS message must have the following format:

```json
{
  "project_id": "proj_123",
  "flow_id": "flow_456",
  "url": "https://example.com",
  "prompt": "Navigate to the homepage and take a screenshot"
}
```

Required fields:
- `project_id`: A unique identifier for the project
- `flow_id`: A unique identifier for the flow
- `url`: The URL to navigate to
- `prompt`: The browser automation task to perform

## Testing

You can test the SQS integration using the provided test script:

```bash
cd microservice
./test_sqs_integration.sh
```

This script will:
1. Check connectivity to SQS, S3, and the API
2. Send a test message to the SQS queue
3. Provide instructions for verifying that the message was processed correctly

## Monitoring

You can monitor the microservice using PM2:

```bash
# View logs
pm2 logs browser-use-api

# Check status
pm2 status
```

## Troubleshooting

### Common Issues

1. **SQS Connectivity Issues**
   - Check AWS credentials
   - Verify SQS queue URL
   - Ensure proper IAM permissions

2. **S3 Upload Failures**
   - Check S3 bucket name and region
   - Verify IAM permissions for S3

3. **API Callback Failures**
   - Check API base URL
   - Verify network connectivity to API

### Health Check

You can check the health of all services using the health endpoint:

```bash
curl http://localhost:8000/health
```

## API Callback

After processing a message, the microservice sends a callback to:

```
{API_BASE_URL}/project/{project_id}/flow/{flow_id}/session/create
```

With a payload containing:
- `agent_history`: A list of browser automation steps
- `media_urls`: URLs of uploaded screenshots and videos
- `status`: The status of the task (completed/failed)
- `metadata`: Additional information about the task

## Security Considerations

- Ensure AWS credentials have the minimum required permissions
- Use a dedicated IAM user for the microservice
- Consider using SQS server-side encryption for sensitive messages
- Implement proper error handling to prevent message loss