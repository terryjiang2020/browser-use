import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Optional
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.browser_agent import BrowserAgentService
from services.message_processor import MessageProcessor
from utils.logger import setup_logger

# Global task storage (use Redis/DB in production)
tasks: Dict[str, dict] = {}

# Global message processor
message_processor: Optional[MessageProcessor] = None

class TaskRequest(BaseModel):
    task: str
    callback_url: Optional[str] = None
    timeout: Optional[int] = 300  # 5 minutes default

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class SQSTestRequest(BaseModel):
    project_id: str
    flow_id: str
    url: str
    prompt: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    global message_processor
    
    # Startup
    logger.info("Starting browser-use microservice")
    
    try:
        # Initialize message processor
        message_processor = MessageProcessor()
        
        # Start SQS message processing in background
        asyncio.create_task(message_processor.start_processing())
        logger.info("SQS message processing started")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        # Continue startup even if SQS is not available for development
        message_processor = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down browser-use microservice")
    if message_processor:
        await message_processor.stop_processing()
        await message_processor.close()

app = FastAPI(
    title="Browser Use Microservice",
    version="1.0.0",
    description="Microservice for browser automation with AWS SQS integration",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = setup_logger()

async def execute_browser_task(task_id: str, task_description: str, callback_url: Optional[str] = None, timeout: int = 300):
    """Execute browser task in background (legacy endpoint)"""
    try:
        logger.info(f"Starting task {task_id}: {task_description}")
        tasks[task_id]["status"] = "running"
        tasks[task_id]["started_at"] = datetime.now().isoformat()
        
        # Initialize browser agent
        agent_service = BrowserAgentService()
        
        try:
            # Run the updated task method
            agent_history, media_files, result_summary = await agent_service.run_task(
                task_description, timeout=timeout
            )
            
            # Update task with success
            tasks[task_id].update({
                "status": "completed",
                "result": result_summary,
                "agent_history": agent_history,
                "media_files": len(media_files),
                "completed_at": datetime.now().isoformat(),
                "error": None
            })
            
            logger.info(f"Task {task_id} completed successfully")
            
            # Send webhook notification
            if callback_url:
                await send_webhook(callback_url, task_id, "completed", 
                                 result=result_summary, agent_history=agent_history)
        
        finally:
            # Clean up agent resources
            agent_service.cleanup_temp_files()
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Task {task_id} failed: {error_msg}")
        
        tasks[task_id].update({
            "status": "failed",
            "result": None,
            "completed_at": datetime.now().isoformat(),
            "error": error_msg
        })
        
        # Send webhook notification
        if callback_url:
            await send_webhook(callback_url, task_id, "failed", error=error_msg)

async def send_webhook(callback_url: str, task_id: str, status: str, 
                      result: str = None, error: str = None, 
                      agent_history: list = None):
    """Send webhook notification"""
    try:
        payload = {
            "task_id": task_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        if result:
            payload["result"] = result
        if error:
            payload["error"] = error
        if agent_history:
            payload["agent_history"] = agent_history
            
        response = requests.post(callback_url, json=payload, timeout=30)
        logger.info(f"Webhook sent for task {task_id}, status: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send webhook for task {task_id}: {str(e)}")

@app.post("/api/v1/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Create a new browser automation task (legacy endpoint)"""
    task_id = str(uuid.uuid4())
    
    # Initialize task
    tasks[task_id] = {
        "task": request.task,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None,
        "callback_url": request.callback_url
    }
    
    # Run in background
    background_tasks.add_task(
        execute_browser_task,
        task_id,
        request.task,
        request.callback_url,
        request.timeout
    )
    
    logger.info(f"Created task {task_id}")
    return TaskResponse(
        task_id=task_id, 
        status="pending",
        message="Task created and queued for execution"
    )

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and result"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]

@app.post("/api/v1/sqs/test")
async def test_sqs_message(request: SQSTestRequest):
    """Test endpoint to send a message to SQS (for development/testing)"""
    if not message_processor:
        raise HTTPException(status_code=503, detail="SQS service not available")
    
    try:
        message_body = {
            "project_id": request.project_id,
            "flow_id": request.flow_id,
            "url": request.url,
            "prompt": request.prompt
        }
        
        message_id = await message_processor.sqs_service.send_message(message_body)
        
        if message_id:
            return {
                "status": "success",
                "message_id": message_id,
                "message": "Test message sent to SQS"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send message to SQS")
            
    except Exception as e:
        logger.error(f"Error sending test message to SQS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "fastapi": True
        }
    }
    
    # Check AWS services if available
    if message_processor:
        try:
            aws_health = await message_processor.health_check()
            health_data["services"].update(aws_health)
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            health_data["services"]["aws_error"] = str(e)
    else:
        health_data["services"]["sqs"] = False
        health_data["services"]["s3"] = False
        health_data["services"]["api_client"] = False
    
    # Determine overall health
    all_healthy = all(health_data["services"].values())
    if not all_healthy:
        health_data["status"] = "degraded"
    
    return health_data

@app.get("/api/v1/status")
async def get_service_status():
    """Get detailed service status"""
    status_data = {
        "microservice": {
            "name": "browser-use-microservice",
            "version": "1.0.0",
            "uptime": datetime.now().isoformat(),
            "active_tasks": len([t for t in tasks.values() if t["status"] == "running"]),
            "total_tasks": len(tasks)
        },
        "configuration": {
            "max_concurrent_tasks": os.getenv('MAX_CONCURRENT_TASKS', '5'),
            "default_timeout": os.getenv('DEFAULT_TIMEOUT', '300'),
            "aws_region": os.getenv('AWS_REGION', 'not_set'),
            "s3_bucket": os.getenv('AWS_S3_BUCKET', 'not_set'),
            "api_base_url": os.getenv('API_BASE_URL', 'not_set')
        }
    }
    
    # Add SQS info if available
    if message_processor:
        status_data["sqs"] = {
            "queue_url": os.getenv('AWS_SQS_QUEUE_URL', 'not_set'),
            "processing": message_processor.running
        }
    
    return status_data

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        workers=1,
        reload=False
    )
