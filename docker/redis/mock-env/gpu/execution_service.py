#!/usr/bin/env python3
# Execution Service for simulating job processing
import json
import asyncio
import logging
import os
import uuid
import time
import random
from typing import Dict, Any, List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("execution-service")

# Get machine ID and port
MACHINE_ID = os.environ.get("MACHINE_ID", "unknown")
PORT = int(os.environ.get("EXECUTION_SERVICE_PORT", "9001"))

# Create FastAPI application
app = FastAPI(title=f"EmProps Execution Service - {MACHINE_ID}", version="1.0.0")

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store of active executor connections and active jobs
active_executors: Dict[str, WebSocket] = {}
active_jobs: Dict[str, Dict[str, Any]] = {}

async def simulate_job_execution(job_id: str, job_data: Dict[str, Any], executor_ws: WebSocket):
    """Simulate job execution with progress updates"""
    logger.info(f"Started execution of job {job_id}")
    
    job_type = job_data.get("type", "unknown")
    params = job_data.get("params", {})
    
    # Add job to active jobs
    active_jobs[job_id] = {
        "job_id": job_id,
        "start_time": time.time(),
        "status": "processing",
        "progress": 0,
        "worker_id": job_data.get("worker_id")
    }
    
    try:
        # Determine job duration based on job type
        if job_type == "image_generation":
            max_steps = random.randint(20, 50)
        elif job_type == "text_generation":
            max_steps = random.randint(10, 30)
        else:
            max_steps = random.randint(5, 15)
        
        # Send progress updates
        for step in range(max_steps + 1):
            progress = step / max_steps * 100
            
            # Update active jobs
            active_jobs[job_id]["progress"] = progress
            
            # Send progress update
            await executor_ws.send_json({
                "type": "job_progress",
                "job_id": job_id,
                "progress": progress,
                "timestamp": time.time()
            })
            
            # Simulate work
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # Randomly fail some jobs
            if random.random() < 0.05 and step > max_steps // 2:
                logger.warning(f"Simulating random failure for job {job_id}")
                raise Exception("Random execution failure (simulated)")
        
        # Job completed
        result = generate_job_result(job_type, params)
        
        # Update active jobs
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["end_time"] = time.time()
        active_jobs[job_id]["result"] = result
        
        # Send completion message
        await executor_ws.send_json({
            "type": "job_completed",
            "job_id": job_id,
            "result": result,
            "timestamp": time.time()
        })
        
        logger.info(f"Completed execution of job {job_id}")
        
        # Remove job from active jobs after a delay
        await asyncio.sleep(5)
        if job_id in active_jobs:
            del active_jobs[job_id]
            
    except Exception as e:
        logger.error(f"Error executing job {job_id}: {str(e)}")
        
        # Update active jobs
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["end_time"] = time.time()
        active_jobs[job_id]["error"] = str(e)
        
        # Send failure message
        await executor_ws.send_json({
            "type": "job_failed",
            "job_id": job_id,
            "error": str(e),
            "timestamp": time.time()
        })
        
        # Remove job from active jobs after a delay
        await asyncio.sleep(5)
        if job_id in active_jobs:
            del active_jobs[job_id]

def generate_job_result(job_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate simulated job results based on job type"""
    if job_type == "image_generation":
        return {
            "image_url": f"https://example.com/images/{uuid.uuid4()}.png",
            "width": params.get("width", 512),
            "height": params.get("height", 512),
            "seed": random.randint(0, 1000000),
            "generation_time": random.uniform(5, 15)
        }
    elif job_type == "text_generation":
        return {
            "text": f"Generated text for prompt: {params.get('prompt', 'No prompt')}",
            "tokens": random.randint(50, 200),
            "generation_time": random.uniform(1, 5)
        }
    else:
        return {
            "message": "Job completed",
            "processing_time": random.uniform(0.5, 3)
        }

@app.websocket("/ws/executor")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for worker executors"""
    await websocket.accept()
    
    # Generate a unique executor ID
    executor_id = f"executor-{uuid.uuid4()}"
    active_executors[executor_id] = websocket
    
    logger.info(f"Executor {executor_id} connected")
    
    try:
        while True:
            # Receive messages from workers
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "execute_job":
                    job_id = message.get("job_id")
                    job_data = message.get("job_data", {})
                    worker_id = message.get("worker_id")
                    
                    logger.info(f"Received job execution request from worker {worker_id} for job {job_id}")
                    
                    # Start job execution task
                    asyncio.create_task(simulate_job_execution(job_id, job_data, websocket))
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON message: {data}")
                
    except WebSocketDisconnect:
        logger.info(f"Executor {executor_id} disconnected")
        if executor_id in active_executors:
            del active_executors[executor_id]
            
    except Exception as e:
        logger.error(f"Error in executor websocket: {str(e)}")
        if executor_id in active_executors:
            del active_executors[executor_id]

@app.get("/jobs")
async def list_active_jobs():
    """List all active jobs"""
    return {"jobs": list(active_jobs.values())}

@app.get("/stats")
async def get_stats():
    """Get execution service stats"""
    return {
        "machine_id": MACHINE_ID,
        "active_executors": len(active_executors),
        "active_jobs": len(active_jobs),
        "active_job_ids": list(active_jobs.keys()),
        "uptime": time.time() - START_TIME
    }

# Store startup time
START_TIME = time.time()

if __name__ == "__main__":
    logger.info(f"Starting Execution Service for {MACHINE_ID} on port {PORT}")
    uvicorn.run("execution_service:app", host="0.0.0.0", port=PORT, log_level="info")
