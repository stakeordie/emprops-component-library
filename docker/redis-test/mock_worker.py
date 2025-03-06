#!/usr/bin/env python3
# Mock worker implementation for testing the Redis queue system
# WebSocket-based version for real-time communication
import time
import random
import asyncio
import websockets
import os
import logging
import redis
import json
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MACHINE_ID = os.environ.get('MACHINE_ID', 'test-machine-1')
GPU_COUNT = int(os.environ.get('MOCK_GPU_COUNT', 2))
WS_HOST = os.environ.get('WS_HOST', 'localhost')
WS_PORT = int(os.environ.get('WS_PORT', 8000))
WS_URL = f"ws://{WS_HOST}:{WS_PORT}/ws/worker"
MIN_PROCESS_TIME = int(os.environ.get('MIN_PROCESS_TIME', 5))
MAX_PROCESS_TIME = int(os.environ.get('MAX_PROCESS_TIME', 30))
PROGRESS_INTERVAL = float(os.environ.get('PROGRESS_INTERVAL', 1.0))  # How often to send progress updates

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")  # Use 'redis' as default in Docker
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# Log Redis connection details
logger.info(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}")

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,  # Explicitly use the configured host
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )
    logger.info(f"Redis connection initialized successfully to {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logger.error(f"Failed to connect to Redis at {REDIS_HOST}:{REDIS_PORT}: {str(e)}")
    raise

async def process_job(websocket, gpu_id, job):
    """Simulate processing a job on a GPU"""
    job_id = job['job_id']
    job_type = job.get('job_type', 'unknown')
    
    logger.info(f"GPU {gpu_id} started processing job {job_id} of type {job_type}")
    
    # Simulate processing time
    process_time = random.randint(MIN_PROCESS_TIME, MAX_PROCESS_TIME)
    total_steps = process_time  # 1 step per second for simplicity
    
    logger.info(f"Job {job_id} will take {process_time} seconds on GPU {gpu_id}")
    
    # Send progress updates during processing
    for step in range(1, total_steps + 1):
        # Calculate progress percentage
        progress = int((step / total_steps) * 100)
        
        # Create progress update message
        update_msg = {
            "type": "update_job_progress",
            "job_id": job_id,
            "machine_id": MACHINE_ID,
            "gpu_id": gpu_id,
            "progress": progress,
            "message": f"Processing step {step}/{total_steps}"
        }
        
        # Send progress update
        await websocket.send(json.dumps(update_msg))
        logger.debug(f"Sent progress update for job {job_id}: {progress}%")
        
        # Wait for the next step
        await asyncio.sleep(1)
    
    # Send job completion message
    complete_msg = {
        "type": "complete_job",
        "job_id": job_id,
        "machine_id": MACHINE_ID,
        "gpu_id": gpu_id,
        "result": {
            "status": "success",
            "processing_time": process_time,
            "output": f"Simulated output for {job_type} job"
        }
    }
    
    await websocket.send(json.dumps(complete_msg))
    logger.info(f"GPU {gpu_id} completed job {job_id} in {process_time}s")
    
    return True

async def gpu_worker(gpu_id):
    """Worker coroutine for each simulated GPU"""
    worker_id = f"{MACHINE_ID}:{gpu_id}"
    logger.info(f"Starting worker for GPU {gpu_id}")
    
    # Update worker status in Redis
    start_time = time.time()
    redis_client.hset(
        f"worker:{worker_id}",
        mapping={
            "machine_id": MACHINE_ID,
            "gpu_id": gpu_id,
            "start_time": start_time,
            "status": "active"
        }
    )
    
    # Create WebSocket connection URL
    ws_worker_url = f"{WS_URL}/{MACHINE_ID}/{gpu_id}"
    
    # Connect and process jobs
    retry_delay = 1
    max_retry_delay = 30
    
    while True:
        try:
            async with websockets.connect(ws_worker_url) as websocket:
                logger.info(f"Worker {worker_id} connected to WebSocket")
                retry_delay = 1  # Reset retry delay on successful connection
                
                # Receive registration confirmation
                registration = await websocket.recv()
                logger.debug(f"Registration response: {registration}")
                
                while True:
                    # Update heartbeat in Redis
                    redis_client.hset(f"worker:{worker_id}", "last_heartbeat", time.time())
                    
                    # Request the next job
                    next_job_request = {
                        "type": "get_next_job",
                        "machine_id": MACHINE_ID,
                        "gpu_id": gpu_id
                    }
                    
                    await websocket.send(json.dumps(next_job_request))
                    
                    # Wait for response (next job or nothing)
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    
                    message_type = response_data.get("type")
                    
                    if message_type == "job_assigned":
                        # Process the assigned job
                        logger.info(f"Job assigned to GPU {gpu_id}: {response_data['job_id']}")
                        await process_job(websocket, gpu_id, response_data)
                    elif message_type == "error":
                        # Handle error
                        logger.warning(f"Error from server: {response_data.get('error')}")
                        await asyncio.sleep(2)
                    else:
                        # No job available or unknown response
                        logger.debug(f"No jobs available for GPU {gpu_id}, waiting...")
                        await asyncio.sleep(2)
        
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
            logger.warning(f"WebSocket connection closed for worker {worker_id}: {str(e)}")
            # Use exponential backoff for reconnection attempts
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_retry_delay)
        
        except Exception as e:
            logger.error(f"Error in GPU {gpu_id} worker: {str(e)}")
            await asyncio.sleep(5)

# Start a worker for each simulated GPU using asyncio
async def main():
    """Start all GPU workers"""
    logger.info(f"Starting mock worker {MACHINE_ID} with {GPU_COUNT} GPUs using WebSockets")
    
    # Create tasks for each GPU worker
    tasks = []
    for gpu_id in range(GPU_COUNT):
        task = asyncio.create_task(gpu_worker(gpu_id))
        tasks.append(task)
    
    # Wait for all tasks to complete (which they never should unless there's an error)
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Worker tasks cancelled")

if __name__ == "__main__":
    try:
        # Run the async event loop
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down mock worker")
