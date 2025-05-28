# Browser Use Microservice

This directory contains a FastAPI-based microservice wrapper for the browser-use library with AWS SQS and S3 integration, designed to be deployed with PM2.

## Features

- ✅ **AWS SQS Integration** - Processes browser automation requests from SQS queues
- ✅ **Website Scanning** - Comprehensive website analysis and data extraction via SQS
- ✅ **AWS S3 Integration** - Uploads screenshots and videos to S3 with automatic URL generation
- ✅ **API Callbacks** - Sends results back to your main application API
- ✅ **Agent History Tracking** - Captures detailed browser automation steps
- ✅ **Media File Management** - Automatic screenshot and video capture
- ✅ **Multiple LLM Support** - OpenAI, Anthropic, DeepSeek, and more
- ✅ **PM2 Process Management** - Production-ready deployment
- ✅ **Comprehensive Logging** - Detailed logs for debugging and monitoring
- ✅ **Health Monitoring** - Health checks for all AWS services

## Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐
│ Your App    │───▶│ AWS SQS     │───▶│ Microservice    │
│             │    │ (Messages)  │    │ (Processing)    │
└─────────────┘    └─────────────┘    └─────────────────┘
                                              │
                                              ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐
│ Your App    │◀───│ API POST    │◀───│ Results +       │
│ (Results)   │    │ /project/:id│    │ S3 URLs         │
└─────────────┘    └─────────────┘    └─────────────────┘
                                              ▲
                                              │
                                       ┌─────────────┐
                                       │ AWS S3      │
                                       │ (Media)     │
                                       └─────────────┘
```

## Quick Start

### 1. Setup the Environment

```bash
cd microservice
chmod +x setup.sh
./setup.sh
```

### 2. Configure Environment Variables

```bash
cp env.example .env
# Edit .env with your configuration:
# - LLM API keys (OpenAI, Anthropic, or DeepSeek)
# - AWS credentials and region
# - SQS queue URL
# - S3 bucket name
# - Your API base URL
```

### 3. Start with PM2

```bash
chmod +x start.sh
./start.sh
```

Or manually:
```bash
pm2 start ecosystem.config.js
```

## Configuration

### Required Environment Variables

```bash
# LLM Provider (choose one)
OPENAI_API_KEY=sk-your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here
# OR  
DEEPSEEK_API_KEY=your_key_here

# AWS Configuration (REQUIRED)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/queue-name
AWS_S3_BUCKET=your-bucket-name

# API Configuration (REQUIRED)
API_BASE_URL=https://api.yourdomain.com/v1
```

### SQS Message Format

#### Browser Automation Messages
Send messages to your SQS queue with this format:

```json
{
  "project_id": "proj_123",
  "flow_id": "flow_456",
  "url": "https://example.com",
  "prompt": "Navigate to the homepage and take a screenshot"
}
```

#### Website Scanning Messages
For website scanning and analysis, use this format:

```json
{
  "type": "scan",
  "project_id": "scan_proj_123",
  "flow_id": "scan_flow_456",
  "url": "https://example.com",
  "scan_type": "full",
  "custom_selectors": [".product-title", ".price"],
  "extract_goals": ["Extract product information", "Get pricing details"],
  "timeout": 300
}
```

**Scan Types Available:**
- `full` - Comprehensive scan (content, structure, accessibility, security, performance)
- `content` - Content extraction and analysis
- `structure` - DOM structure and technology detection
- `accessibility` - Accessibility compliance checking
- `security` - Security assessment
- `performance` - Performance analysis

For detailed scanning documentation, see [SCANNING.md](./SCANNING.md)

### API Callback

The microservice will POST results to:
```
{API_BASE_URL}/project/{project_id}/flow/{flow_id}/session/create
```

With payload:
```json
{
  "agent_history": [
    {
      "timestamp": "2025-05-27T10:30:00Z",
      "type": "action",
      "content": "Navigated to https://example.com"
    }
  ],
  "media_urls": [
    "https://your-bucket.s3.us-east-1.amazonaws.com/browser-automation/media/proj_123/flow_456/screenshot_20250527_103000.png"
  ],
  "status": "completed",
  "timestamp": "2025-05-27T10:30:00Z",
  "metadata": {
    "result_summary": "Task completed successfully",
    "media_file_count": 1,
    "successful_uploads": 1,
    "starting_url": "https://example.com",
    "task_prompt": "Navigate to the homepage and take a screenshot"
  }
}
```

## API Endpoints

### Legacy REST API (still available)

#### Create a Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Go to google.com and search for browser automation",
    "callback_url": "https://your-webhook-endpoint.com/webhook",
    "timeout": 300
  }'
```

#### Get Task Status
```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

#### Test SQS Integration
```bash
curl -X POST http://localhost:8000/api/v1/sqs/test \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test_project",
    "flow_id": "test_flow",
    "url": "https://google.com",
    "prompt": "Search for browser automation"
  }'
```

### Health and Status Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Service Status
```bash
curl http://localhost:8000/api/v1/status
```

## AWS Setup

### 1. Create SQS Queue

```bash
aws sqs create-queue \
  --queue-name browser-automation-queue \
  --region us-east-1
```

### 2. Create S3 Bucket

```bash
aws s3 mb s3://your-browser-automation-bucket --region us-east-1
```

### 3. Configure IAM Permissions

Your AWS credentials need the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:SendMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:us-east-1:123456789012:browser-automation-queue"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::your-browser-automation-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::your-browser-automation-bucket"
    }
  ]
}
```

## PM2 Commands

```bash
# Start
pm2 start browser-use-api

# Stop
pm2 stop browser-use-api

# Restart
pm2 restart browser-use-api

# Logs
pm2 logs browser-use-api

# Status
pm2 status

# Save PM2 configuration
pm2 save

# Startup script (runs PM2 on boot)
pm2 startup
```

## Production Deployment

For production deployment on EC2:

1. Update the `ecosystem.config.js` with your EC2 paths
2. Configure proper logging paths
3. Set up Nginx as a reverse proxy (optional)
4. Configure auto-scaling if needed
5. Set up CloudWatch monitoring for logs
6. Configure SQS Dead Letter Queue for failed messages

## Directory Structure

```
microservice/
├── app.py                          # FastAPI main application
├── services/
│   ├── __init__.py
│   ├── browser_agent.py            # Browser automation service
│   ├── sqs_service.py              # AWS SQS integration
│   ├── s3_service.py               # AWS S3 integration
│   ├── api_client.py               # API callback client
│   └── message_processor.py        # Main message processing logic
├── utils/
│   ├── __init__.py
│   └── logger.py                   # Logging configuration
├── ecosystem.config.js             # PM2 configuration
├── setup.sh                       # Setup script
├── start.sh                       # Start script
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create from env.example)
├── env.example                    # Environment variables template
└── README.md                      # This file
```

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   - Ensure AWS credentials are properly configured
   - Check IAM permissions for SQS and S3

2. **SQS Messages Not Processing**
   - Verify SQS queue URL is correct
   - Check queue permissions
   - Monitor CloudWatch logs

3. **S3 Upload Failures**
   - Verify S3 bucket exists and is accessible
   - Check bucket permissions
   - Ensure bucket region matches configuration

4. **API Callback Failures**
   - Verify API_BASE_URL is correct and accessible
   - Check API endpoint authentication if required
   - Monitor API server logs

### Monitoring

- Monitor PM2 logs: `pm2 logs browser-use-api`
- Check service health: `curl http://localhost:8000/health`
- Monitor SQS queue depth in AWS Console
- Check S3 bucket for uploaded files
- Monitor API callback success rates

### Performance Tuning

- Adjust `MAX_CONCURRENT_TASKS` based on server capacity
- Tune `DEFAULT_TIMEOUT` for your use cases
- Configure SQS visibility timeout appropriately
- Consider using SQS FIFO queues for ordered processing

## License

This microservice wrapper is part of the browser-use project and follows the same license terms.
