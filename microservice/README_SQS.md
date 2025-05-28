# SQS Integration for Browser-Use Microservice

This README provides instructions on how to set up and verify the SQS integration for the Browser-Use microservice.

## Setup

1. Configure the environment variables in the `.env` file:

```
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-southeast-2
AWS_SQS_QUEUE_URL=https://sqs.ap-southeast-2.amazonaws.com/281584859358/BrowserUse-Test-1
AWS_S3_BUCKET=your_s3_bucket
AWS_S3_REGION=ap-southeast-2

# API Configuration
API_BASE_URL=your_api_base_url

# LLM Configuration (choose one)
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Starting the Microservice

1. Start the microservice using PM2:

```bash
./start.sh
```

2. Verify that the microservice is running:

```bash
pm2 status
```

## Testing the SQS Integration

1. Run the test script to send a test message to the SQS queue:

```bash
python test_sqs_integration.py
```

2. Monitor the microservice logs to verify that the message is being processed:

```bash
pm2 logs browser-use-api
```

3. Look for log entries related to:
   - Receiving the message from SQS
   - Processing the message
   - Running the browser automation task
   - Uploading screenshots and videos to S3
   - Sending the results to the API

## Verification Steps

1. **SQS Message Reception**:
   - Check the logs for: "Received X messages from SQS"
   - Verify that the message ID matches the one from the test script

2. **Message Processing**:
   - Check the logs for: "Processing automation message for project X, flow Y"
   - Verify that the project_id and flow_id match the ones from the test script

3. **Browser Automation**:
   - Check the logs for: "Running browser task: X"
   - Verify that the task description matches the prompt from the test script

4. **S3 Upload**:
   - Check the logs for: "Uploading X media files to S3"
   - Verify that the files are uploaded successfully

5. **API Callback**:
   - Check the logs for: "Sending session result to: X"
   - Verify that the API callback is sent with the correct payload

## Troubleshooting

If you encounter issues with the SQS integration, check the following:

1. **SQS Connectivity**:
   - Verify that the AWS credentials are correct
   - Check that the SQS queue URL is correct
   - Ensure that the IAM user has the necessary permissions

2. **S3 Upload**:
   - Verify that the S3 bucket exists and is accessible
   - Check that the IAM user has the necessary permissions

3. **API Callback**:
   - Verify that the API base URL is correct
   - Check that the API endpoint is accessible

## Additional Resources

For more detailed information, refer to:

- [SQS_INTEGRATION.md](./SQS_INTEGRATION.md) - Detailed documentation on the SQS integration
- [AWS SQS Documentation](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [AWS S3 Documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)