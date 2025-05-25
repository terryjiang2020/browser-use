# Browser Use Microservice

This directory contains a FastAPI-based microservice wrapper for the browser-use library, designed to be deployed with PM2.

## Quick Start

1. **Setup the environment:**
   ```bash
   cd microservice
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure your API keys:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (OpenAI, Anthropic, DeepSeek, etc.)
   ```

3. **Start with PM2:**
   ```bash
   pm2 start ecosystem.config.js
   ```

## One-liner for PM2

```bash
pm2 start "venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000" --name browser-use-api --cwd /Users/jiangjiahao/Documents/GitHub/browser-use/microservice
```

## API Endpoints

### Create a Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Go to google.com and search for browser automation",
    "callback_url": "https://your-webhook-endpoint.com/webhook",
    "timeout": 300
  }'
```

### Get Task Status
```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

### Health Check
```bash
curl http://localhost:8000/health
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

## Configuration

The service supports multiple LLM providers:
- OpenAI (GPT-4, GPT-4o)
- Anthropic (Claude)
- DeepSeek
- Azure OpenAI
- Google Gemini

Configure your preferred provider in the `.env` file.

## Features

- ✅ Asynchronous task processing
- ✅ Webhook notifications
- ✅ Task status tracking
- ✅ Multiple LLM provider support
- ✅ Comprehensive logging
- ✅ Health check endpoint
- ✅ PM2 process management
- ✅ Auto-restart on failures

## Production Deployment

For production deployment on EC2:

1. Update the `ecosystem.config.js` with your EC2 paths
2. Configure proper logging paths
3. Set up Nginx as a reverse proxy (optional)
4. Configure auto-scaling if needed

## Directory Structure

```
microservice/
├── app.py                 # FastAPI main application
├── services/
│   ├── __init__.py
│   └── browser_agent.py   # Browser automation service
├── utils/
│   ├── __init__.py
│   └── logger.py          # Logging configuration
├── ecosystem.config.js    # PM2 configuration
├── setup.sh              # Setup script
├── start.sh              # Start script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```
