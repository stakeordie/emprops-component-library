#!/usr/bin/env python3
# Job submitter for testing the Redis queue system
# WebSocket-based version for real-time communication
import time
import random
import asyncio
import websockets
import os
import logging
import json
import uuid
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WS_HOST = os.environ.get('WS_HOST', 'localhost')
WS_PORT = int(os.environ.get('WS_PORT', 8000))
WS_URL = f"ws://{WS_HOST}:{WS_PORT}/ws/client"
CLIENT_ID = f"test-client-{uuid.uuid4()}"
JOB_COUNT = int(os.environ.get('JOB_COUNT', 10))  # Reduced default for easier testing
SUBMISSION_INTERVAL = float(os.environ.get('SUBMISSION_INTERVAL', 0.5))
MAX_PRIORITY = int(os.environ.get('MAX_PRIORITY', 5))
RESULT_TIMEOUT = int(os.environ.get('RESULT_TIMEOUT', 600))  # 10 minutes timeout for results
JOB_TYPES = ["comfy_workflow", "a1111_txt2img", "test_job"]

# Sample job templates for testing
def create_test_job(job_id, priority=0):
    """Create a test job with the given priority"""
    job_type = random.choice(JOB_TYPES)
    
    # Create job payload based on type
    if job_type == "comfy_workflow":
        payload = {
            "workflow_id": f"workflow_{random.randint(1, 10)}",
            "parameters": {
                "prompt": "a photo of a cat",
                "negative_prompt": "blurry, bad quality",
                "steps": random.randint(20, 50),
                "cfg_scale": round(random.uniform(5.0, 9.0), 1),
                "width": random.choice([512, 768, 1024]),
                "height": random.choice([512, 768, 1024]),
                "seed": random.randint(0, 2**32 - 1)
            }
        }
    elif job_type == "a1111_txt2img":
        payload = {
            "prompt": "a beautiful landscape with mountains and rivers",
            "negative_prompt": "ugly, deformed",
            "steps": random.randint(20, 50),
            "sampler_name": random.choice(["Euler a", "DPM++ 2M Karras"]),
            "width": random.choice([512, 768, 1024]),
            "height": random.choice([512, 768, 1024]),
            "cfg_scale": round(random.uniform(5.0, 9.0), 1),
            "seed": random.randint(0, 2**32 - 1)
        }
    else:  # test_job
        payload = {
            "test_param_1": random.randint(1, 100),
            "test_param_2": str(uuid.uuid4()),
            "processing_time": random.randint(5, 30)
        }
    
    # Create the WebSocket message to submit the job
    return {
        "type": "submit_job",
        "client_id": CLIENT_ID,
        "job_type": job_type,
        "priority": priority,
        "payload": payload,
        "job_id": job_id  # Let the queue service assign IDs in production
    }

async def submit_job(websocket, job):
    """Submit a single job via WebSocket and track its progress"""
    job_id = job["job_id"]
    priority = job["priority"]
    job_type = job["job_type"]
    
    # Send the job submission message
    await websocket.send(json.dumps(job))
    logger.info(f"Submitted job {job_id} (type: {job_type}) with priority {priority}")
    
    return job_id

async def job_status_tracker(websocket, job_id, job_type):
    """Track the status of a job until completion or timeout"""
    start_time = time.time()
    last_progress = 0
    
    while time.time() - start_time < RESULT_TIMEOUT:
        try:
            # Wait for a message from the server
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(response)
            
            # Check if the message is for our job
            if message.get("job_id") == job_id:
                message_type = message.get("type")
                
                if message_type == "job_status_update":
                    status = message.get("status")
                    logger.info(f"Job {job_id} status update: {status}")
                    
                    # If the job is completed or failed, we're done tracking
                    if status in ["completed", "failed", "cancelled"]:
                        return status
                
                elif message_type == "job_progress_update":
                    progress = message.get("progress", 0)
                    
                    # Only log if progress has changed significantly
                    if progress - last_progress >= 10 or progress == 100:
                        logger.info(f"Job {job_id} progress: {progress}%")
                        last_progress = progress
                
                elif message_type == "job_result":
                    logger.info(f"Job {job_id} completed successfully")
                    return "completed"
                
                elif message_type == "error":
                    logger.error(f"Error for job {job_id}: {message.get('error')}")
                    return "failed"
        
        except asyncio.TimeoutError:
            # No message received within timeout, continue waiting
            continue
        except Exception as e:
            logger.error(f"Error tracking job {job_id}: {str(e)}")
            return "error"
    
    logger.warning(f"Timeout waiting for job {job_id} result")
    return "timeout"

async def submit_jobs():
    """Submit a batch of test jobs to the queue API and track their status"""
    logger.info(f"Submitting {JOB_COUNT} test jobs via WebSocket...")
    
    successful_submissions = 0
    failed_submissions = 0
    pending_jobs = {}
    
    # Connect to the WebSocket server
    try:
        async with websockets.connect(f"{WS_URL}/{CLIENT_ID}") as websocket:
            logger.info(f"Connected to WebSocket server with client ID: {CLIENT_ID}")
            
            # Receive initial connection message
            welcome = await websocket.recv()
            logger.debug(f"Server welcome: {welcome}")
            
            # Create and submit jobs
            for i in range(JOB_COUNT):
                job_id = f"test-job-{uuid.uuid4()}"
                priority = random.randint(0, MAX_PRIORITY)
                job = create_test_job(job_id, priority)
                
                try:
                    # Submit the job
                    await submit_job(websocket, job)
                    successful_submissions += 1
                    
                    # Store job info for tracking
                    pending_jobs[job_id] = {
                        "job_type": job["job_type"],
                        "priority": priority,
                        "submit_time": datetime.now().isoformat()
                    }
                    
                except Exception as e:
                    logger.error(f"Error submitting job {job_id}: {str(e)}")
                    failed_submissions += 1
                
                # Wait between submissions
                await asyncio.sleep(SUBMISSION_INTERVAL)
            
            logger.info(f"Job submission complete: {successful_submissions} successful, {failed_submissions} failed")
            
            # Now track job status for all submitted jobs
            if successful_submissions > 0:
                logger.info(f"Tracking status for {len(pending_jobs)} submitted jobs...")
                
                # Create tasks for tracking each job's status
                tracking_tasks = []
                for job_id, job_info in pending_jobs.items():
                    task = asyncio.create_task(
                        job_status_tracker(websocket, job_id, job_info["job_type"])
                    )
                    tracking_tasks.append(task)
                
                # Wait for all tracking tasks to complete
                completed_statuses = await asyncio.gather(*tracking_tasks)
                
                # Summarize results
                status_counts = {}
                for status in completed_statuses:
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                logger.info(f"Job processing results: {status_counts}")
    
    except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        return 0, 0
    
    except Exception as e:
        logger.error(f"Unexpected error in submit_jobs: {str(e)}")
        return 0, 0
    
    return successful_submissions, failed_submissions

if __name__ == "__main__":
    try:
        # Run the async event loop
        asyncio.run(submit_jobs())
    except KeyboardInterrupt:
        logger.info("Job submission interrupted by user")
