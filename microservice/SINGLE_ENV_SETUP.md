# Single .env File Multi-Instance Setup

## Overview

This setup uses **one `.env` file** for all instances. PM2 handles instance-specific configurations through environment variable overrides in `ecosystem.config.js`.

## How It Works

1. **Base Configuration**: All shared settings (AWS credentials, API keys, etc.) come from the single `.env` file
2. **Instance Overrides**: PM2 overrides specific variables for each instance (PORT, INSTANCE_ID, TABLE_NAME, etc.)
3. **No Multiple Files**: No need for `.env-1`, `.env-2`, etc.

## Deployment Steps

### 1. On your EC2 instance, copy your `.env` file:

```bash
# Navigate to your project root
cd /home/ec2-user/Test-Agent-Dev-1

# Copy your .env file here (the one with all your credentials)
# Your .env file should contain all the variables from your local setup
```

### 2. Start both instances with PM2:

```bash
cd microservice
pm2 start ecosystem.config.js
```

This will start:
- **browser-use-main**: Port 8000, Instance ID 0, higher resource allocation
- **browser-use-instance1**: Port 10001, Instance ID 1, lower resource allocation

### 3. Monitor the instances:

```bash
pm2 status
pm2 logs
pm2 logs browser-use-main      # Logs for main instance
pm2 logs browser-use-instance1 # Logs for second instance
```

## Configuration Details

### Shared Variables (from .env):

- AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
- API keys (OPENAI_API_KEY, etc.)
- Database connections
- Service URLs
- All authentication tokens

### Instance-Specific Overrides (from PM2):

**Main Instance (browser-use-main):**

- PORT: 8000
- INSTANCE_ID: 0
- TABLE_NAME: test_table
- OPENSEARCH_INDEX_NAME: commit-descriptions
- MAX_CONCURRENT_JOBS: 5
- WORKER_THREADS: 4
- MAX_CONCURRENT_BROWSERS: 3

**Instance 1 (browser-use-instance1):**

- PORT: 10001
- INSTANCE_ID: 1
- TABLE_NAME: test_table_instance1
- OPENSEARCH_INDEX_NAME: commit-descriptions-instance1
- MAX_CONCURRENT_JOBS: 3
- WORKER_THREADS: 2
- MAX_CONCURRENT_BROWSERS: 2

## Benefits

✅ **Simple**: Only one environment file to manage
✅ **Secure**: All credentials in one place
✅ **Scalable**: Easy to add more instances by updating PM2 config
✅ **Maintainable**: Single source of truth for configuration
✅ **Load Balanced**: Different resource allocations per instance

## Adding More Instances

To add a third instance, just add another app object to `ecosystem.config.js`:

```javascript
{
  name: 'browser-use-instance2',
  script: 'python3',
  args: 'main.py',
  cwd: '/home/ec2-user/Test-Agent-Dev-1/microservice',
  env_file: '../.env',
  // ... same config with different overrides
  env: {
    INSTANCE_ID: '2',
    PORT: '10002',
    TABLE_NAME: 'test_table_instance2',
    // etc...
  }
}
```

## Troubleshooting

1. **Environment not loading**: Make sure `env_file: '../.env'` points to the correct path
2. **Port conflicts**: Ensure each instance has a unique PORT override
3. **Resource conflicts**: Adjust MAX_CONCURRENT_* values based on your EC2 instance size
4. **Logs location**: Check `./logs/` directory for instance-specific logs
