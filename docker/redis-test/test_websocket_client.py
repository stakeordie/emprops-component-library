#!/usr/bin/env python3
# Simple WebSocket client for testing the queue API
import asyncio
import websockets
import json
import logging
import os
import uuid
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WS_HOST = os.environ.get('WS_HOST', 'localhost')
WS_PORT = int(os.environ.get('WS_PORT', 8000))
CLIENT_ID = f"test-client-{uuid.uuid4()}"

async def test_client_connection():
    """Test basic client connection and message exchange"""
    ws_url = f"ws://{WS_HOST}:{WS_PORT}/ws/client/{CLIENT_ID}"
    
    logger.info(f"Connecting to {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            logger.info("Connected to WebSocket server")
            
            # Receive welcome message
            welcome = await websocket.recv()
            logger.info(f"Server welcome message: {welcome}")
            
            # Simple ping test
            ping_message = {
                "type": "ping",
                "client_id": CLIENT_ID,
                "timestamp": str(uuid.uuid4())
            }
            
            logger.info(f"Sending ping message")
            await websocket.send(json.dumps(ping_message))
            
            # Wait for pong response
            response = await websocket.recv()
            logger.info(f"Received response: {response}")
            
            # Submit a test job
            job_id = f"test-job-{uuid.uuid4()}"
            submit_job_message = {
                "type": "submit_job",
                "client_id": CLIENT_ID,
                "job_type": "test_job",
                "priority": 3,
                "job_id": job_id,
                "payload": {
                    "test_param_1": 42,
                    "test_param_2": "test-value",
                    "processing_time": 10
                }
            }
            
            logger.info(f"Submitting test job {job_id}")
            await websocket.send(json.dumps(submit_job_message))
            
            # Wait for job submission confirmation
            response = await websocket.recv()
            logger.info(f"Job submission response: {response}")
            
            # Listen for messages for 30 seconds
            logger.info("Listening for messages for 30 seconds...")
            end_time = asyncio.get_event_loop().time() + 30
            
            while asyncio.get_event_loop().time() < end_time:
                try:
                    # Set a timeout so we can break the loop if needed
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    logger.info(f"Received message: {message}")
                    
                    # Parse the message
                    message_data = json.loads(message)
                    
                    # If this is a job completion message for our job, we can break
                    if (message_data.get("type") == "job_result" and 
                        message_data.get("job_id") == job_id):
                        logger.info(f"Job {job_id} completed!")
                        break
                        
                except asyncio.TimeoutError:
                    # No message received, continue waiting
                    continue
                except Exception as e:
                    logger.error(f"Error receiving message: {str(e)}")
                    break
            
            logger.info("Test completed successfully")
    
    except Exception as e:
        logger.error(f"Error in test client: {str(e)}")
        return False
    
    return True

async def test_worker_connection(gpu_id=0):
    """Test basic worker connection and job processing"""
    machine_id = f"test-machine-{uuid.uuid4().hex[:8]}"
    ws_url = f"ws://{WS_HOST}:{WS_PORT}/ws/worker/{machine_id}/{gpu_id}"
    
    logger.info(f"Connecting as worker to {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            logger.info(f"Connected as worker {machine_id}:{gpu_id}")
            
            # Receive registration confirmation
            registration = await websocket.recv()
            logger.info(f"Registration response: {registration}")
            
            # Request a job
            next_job_request = {
                "type": "get_next_job",
                "machine_id": machine_id,
                "gpu_id": gpu_id
            }
            
            logger.info("Requesting next job")
            await websocket.send(json.dumps(next_job_request))
            
            # Wait for job assignment or no-job response
            response = await websocket.recv()
            logger.info(f"Job request response: {response}")
            
            # Process the response
            response_data = json.loads(response)
            message_type = response_data.get("type")
            
            if message_type == "job_assigned":
                # We got a job, simulate processing
                job_id = response_data.get("job_id")
                logger.info(f"Processing job {job_id}")
                
                # Simulate job processing with progress updates
                total_steps = 5
                
                for step in range(1, total_steps + 1):
                    # Calculate progress
                    progress = int((step / total_steps) * 100)
                    
                    # Send progress update
                    update_msg = {
                        "type": "update_job_progress",
                        "job_id": job_id,
                        "machine_id": machine_id,
                        "gpu_id": gpu_id,
                        "progress": progress,
                        "message": f"Processing step {step}/{total_steps}"
                    }
                    
                    await websocket.send(json.dumps(update_msg))
                    logger.info(f"Sent progress update: {progress}%")
                    
                    # Wait between steps
                    await asyncio.sleep(1)
                
                # Complete the job
                complete_msg = {
                    "type": "complete_job",
                    "job_id": job_id,
                    "machine_id": machine_id,
                    "gpu_id": gpu_id,
                    "result": {
                        "status": "success",
                        "processing_time": total_steps,
                        "output": "Test job completed successfully"
                    }
                }
                
                await websocket.send(json.dumps(complete_msg))
                logger.info(f"Job {job_id} completed")
                
                # Wait for confirmation
                confirmation = await websocket.recv()
                logger.info(f"Completion confirmation: {confirmation}")
            
            logger.info("Worker test completed successfully")
    
    except Exception as e:
        logger.error(f"Error in worker test: {str(e)}")
        return False
    
    return True

async def main():
    """Run the tests"""
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        # Run as worker test
        gpu_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        success = await test_worker_connection(gpu_id)
    else:
        # Run as client test
        success = await test_client_connection()
    
    if success:
        logger.info("All tests completed successfully")
    else:
        logger.error("Tests failed")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
