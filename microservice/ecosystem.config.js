module.exports = {
  apps: [{
    name: process.env.PM2_APP_NAME || 'browser-use-microservice',
    script: 'python3',
    args: process.env.PM2_SCRIPT_ARGS || 'app.py',
    cwd: process.env.PM2_CWD || process.cwd(),
    env_file: process.env.PM2_ENV_FILE || '.env',
    instances: process.env.PM2_INSTANCES || 1,
    exec_mode: process.env.PM2_EXEC_MODE || 'fork',
    restart_delay: parseInt(process.env.PM2_RESTART_DELAY || '4000'),
    max_memory_restart: process.env.PM2_MAX_MEMORY || '1G',
    error_file: process.env.PM2_ERROR_FILE || './logs/err.log',
    out_file: process.env.PM2_OUT_FILE || './logs/out.log',
    log_file: process.env.PM2_LOG_FILE || './logs/combined.log',
    time: true,
    env: {
      NODE_ENV: process.env.NODE_ENV || 'production',
      PYTHONPATH: process.env.PM2_PYTHONPATH || process.cwd()
    }
  }]
}