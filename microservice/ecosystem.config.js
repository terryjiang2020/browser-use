module.exports = {
  apps: [{
    name: 'browser-use-api',
    script: 'venv/bin/python',
    args: '-m uvicorn app:app --host 0.0.0.0 --port 8000',
    cwd: '/Users/jiangjiahao/Documents/GitHub/browser-use/microservice',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '/Users/jiangjiahao/Documents/GitHub/browser-use/microservice:/Users/jiangjiahao/Documents/GitHub/browser-use'
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    merge_logs: true
  }]
};
