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
from utils.logger import setup_logger

# Global task storage (use Redis/DB in production)
tasks: Dict[str, dict] = {}

class TaskRequest(BaseModel):
    task: str
    callback_url: Optional[str] = None
    timeout: Optional[int] = 300  # 5 minutes default

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting browser-use microservice")
    yield
    # Shutdown
    logger.info("Shutting down browser-use microservice")

app = FastAPI(
    title="Browser Use Microservice",
    version="1.0.0",
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
    """Execute browser task in background"""
    try:
        logger.info(f"Starting task {task_id}: {task_description}")
        tasks[task_id]["status"] = "running"
        tasks[task_id]["started_at"] = datetime.now().isoformat()
        
        # Initialize browser agent
        agent_service = BrowserAgentService()
        result = await agent_service.run_task(task_description, timeout)
        
        # Update task with success
        tasks[task_id].update({
            "status": "completed",
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "error": None
        })
        
        logger.info(f"Task {task_id} completed successfully")
        
        # Send webhook notification
        if callback_url:
            await send_webhook(callback_url, task_id, "completed", result=result)
            
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

async def send_webhook(callback_url: str, task_id: str, status: str, result: str = None, error: str = None):
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
            
        response = requests.post(callback_url, json=payload, timeout=30)
        logger.info(f"Webhook sent for task {task_id}, status: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send webhook for task {task_id}: {str(e)}")

@app.post("/api/v1/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Create a new browser automation task"""
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        workers=1,
        reload=False
    )
