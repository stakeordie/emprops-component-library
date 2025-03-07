#!/usr/bin/env python3
# Worker implementation for GPU containers
import json
import asyncio
import logging
import argparse
import os
import uuid
import time
import aiohttp
import random
from typing import Dict, Any, Optional

# VERIFICATION LOG - THIS SHOULD APPEAR IF CODE CHANGES ARE APPLIED
logging.basicConfig(level=logging.INFO)
logging.getLogger().info("VERIFICATION: WORKER CODE CHANGES HAVE BEEN APPLIED - VERSION 2")

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Get Redis API connection details from environment variables
REDIS_API_HOST = os.environ.get("REDIS_API_HOST", "hub")
REDIS_API_PORT = os.environ.get("REDIS_API_PORT", "8001")
REDIS_API_WS_URL = f"ws://{REDIS_API_HOST}:{REDIS_API_PORT}/ws/worker"

# Get Execution Service connection details
MACHINE_ID = os.environ.get("MACHINE_ID", "1")
GPU_ID = int(os.environ.get("GPU_ID", "1"))
EXECUTION_SERVICE_PORT = os.environ.get("EXECUTION_SERVICE_PORT", "9001")
EXECUTION_SERVICE_URL = f"ws://localhost:{EXECUTION_SERVICE_PORT}/ws/executor"

class Worker:
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.logger = logging.getLogger(f"worker-{worker_id}")
        self.status = "idle"
        self.ws = None
        self.executor_ws = None
        self.current_job = None
        self.heartbeat_task = None
        self.running = True
        self.last_sent_message = "None"
        self.logger.info(f"Worker {worker_id} initialized")
        
    async def connect_to_redis_api(self):
        """Connect to Redis API WebSocket with retries and exponential backoff"""
        # Retry parameters
        max_retries = 10
        base_delay = 0.5  # Start with 0.5 second delay
        max_delay = 10  # Max delay between retries in seconds
        
        session = None
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Create a new session if needed
                if session is None or session.closed:
                    session = aiohttp.ClientSession()
                
                # Log connection attempt with retry info
                if retry_count > 0:
                    self.logger.info(f"Retry #{retry_count} connecting to Redis API at {REDIS_API_WS_URL}/{self.worker_id}")
                else:
                    self.logger.info(f"Connecting to Redis API at {REDIS_API_WS_URL}/{self.worker_id}")
                
                # Try to connect to WebSocket
                self.ws = await session.ws_connect(f"{REDIS_API_WS_URL}/{self.worker_id}")
                self.logger.info("Connected to Redis API WebSocket successfully")
                
                # Send worker registration message
                await self.ws.send_json({
                    "type": "register_worker",
                    "machine_id": MACHINE_ID,
                    "gpu_id": GPU_ID
                })
                self.logger.info(f"Sent worker registration for {self.worker_id}")
                
                # Subscribe to job notifications
                subscription_message = {
                    "type": "subscribe_job_notifications",
                    "worker_id": self.worker_id,
                    "enabled": True
                }
                self.logger.info(f"🔍🔍🔍 SENDING SUBSCRIPTION MESSAGE: {json.dumps(subscription_message)}")
                await self.ws.send_json(subscription_message)
                self.logger.info("Subscribed to job notifications")
                
                # Start heartbeat task
                self.heartbeat_task = asyncio.create_task(self.send_heartbeats())
                
                return True
                
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                
                # Only log detailed error on first few attempts to avoid log spam
                if retry_count <= 3:
                    self.logger.warning(f"Connection attempt {retry_count} failed: {last_error}")
                elif retry_count == 4:
                    self.logger.warning("Further connection errors will be summarized")
                
                # Close the session if it exists and is still open
                if session and not session.closed:
                    await session.close()
                    session = None
                
                # Calculate backoff delay with jitter to avoid thundering herd
                delay = min(base_delay * (2 ** (retry_count - 1)), max_delay)
                jitter = delay * 0.2  # Add 20% jitter
                delay = delay + random.uniform(-jitter, jitter)
                
                if retry_count < max_retries:
                    self.logger.info(f"Retrying in {delay:.2f} seconds (attempt {retry_count}/{max_retries})")
                    await asyncio.sleep(delay)
                    
        # If we've exhausted all retries, log and return failure
        self.logger.error(f"Failed to connect to Redis API after {max_retries} attempts. Last error: {last_error}")
        return False
            
    async def connect_to_execution_service(self):
        """Connect to Execution Service WebSocket with retries"""
        # Retry parameters
        max_retries = 5
        base_delay = 0.5
        max_delay = 5  # Max delay between retries in seconds
        
        session = None
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Create a new session if needed
                if session is None or session.closed:
                    session = aiohttp.ClientSession()
                
                # Log connection attempt with retry info
                if retry_count > 0:
                    self.logger.info(f"Retry #{retry_count} connecting to Execution Service at {EXECUTION_SERVICE_URL}")
                else:
                    self.logger.info(f"Connecting to Execution Service at {EXECUTION_SERVICE_URL}")
                
                # Try to connect to WebSocket
                self.executor_ws = await session.ws_connect(EXECUTION_SERVICE_URL)
                self.logger.info("Connected to Execution Service WebSocket successfully")
                return True
                
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                
                # Close the session if it exists and is still open
                if session and not session.closed:
                    await session.close()
                    session = None
                
                # Calculate backoff delay with jitter
                delay = min(base_delay * (2 ** (retry_count - 1)), max_delay)
                jitter = delay * 0.2  # Add 20% jitter
                delay = delay + random.uniform(-jitter, jitter)
                
                if retry_count < max_retries:
                    self.logger.info(f"Retrying execution service connection in {delay:.2f} seconds (attempt {retry_count}/{max_retries})")
                    await asyncio.sleep(delay)
        
        # If we've exhausted all retries, log and return failure
        self.logger.error(f"Failed to connect to Execution Service after {max_retries} attempts. Last error: {last_error}")
        return False
            
    async def send_heartbeats(self):
        """Send regular heartbeats to Redis API"""
        # Add initial delay before first heartbeat to allow registration to complete
        self.logger.info("Waiting 10 seconds before sending first heartbeat...")
        await asyncio.sleep(10)  # Wait 10 seconds before sending first heartbeat
        
        while self.running:
            try:
                if self.ws and not self.ws.closed:
                    message = {
                        "type": "worker_heartbeat",
                        "worker_id": self.worker_id,
                        "status": self.status,
                        "load": 0.0
                    }
                    self.last_sent_message = json.dumps(message)
                    await self.ws.send_json(message)
                    self.logger.debug(f"Sent heartbeat with status: {self.status}")
                else:
                    self.logger.warning("Cannot send heartbeat: WebSocket closed")
            except Exception as e:
                self.logger.error(f"Error sending heartbeat: {str(e)}")
                
            # Heartbeat is a slow backup health check mechanism (30s)
            # Job status changes and completions are announced separately and immediately
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            
    async def claim_job(self, job_id: str, job_type: str):
        """Claim a job for processing"""
        try:
            self.logger.info(f"Claiming job {job_id} of type {job_type}")
            
            # Send claim message
            await self.ws.send_json({
                "type": "claim_job",
                "worker_id": self.worker_id,
                "job_id": job_id
            })
            
            self.logger.debug(f"Sent claim_job message for job {job_id}")
            
            # Wait for response
            for _ in range(10):  # 5 second timeout
                msg = await self.ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    self.logger.debug(f"Received response for claim attempt: {data}")
                    
                    if data.get("type") == "job_claimed" and data.get("job_id") == job_id:
                        if data.get("success", False):
                            self.logger.info(f"Successfully claimed job {job_id}")
                            self.current_job = job_id
                            self.status = "busy"
                            return True  # Return boolean instead of data object
                        else:
                            self.logger.warning(f"Failed to claim job {job_id}: {data.get('reason', 'unknown')}")
                            return False
                await asyncio.sleep(0.5)
                
            self.logger.warning(f"Timeout waiting for job claim response")
            return False
            
        except Exception as e:
            self.logger.error(f"Error claiming job: {str(e)}")
            return False
            
    async def process_job(self, job_data: Dict[str, Any]):
        """Process a job in the mock environment"""
        job_id = job_data.get("job_id")
        
        try:
            self.logger.info(f"Processing job {job_id} in mock environment")
            
            # Update job status to processing
            await self.update_job_status(job_id, "processing")
            
            # In the mock environment, we'll simulate job processing
            self.logger.info(f"Simulating processing for job {job_id}")
            
            # Simulate job progress updates
            for progress in [10, 25, 50, 75, 100]:
                await self.update_job_status(job_id, "processing", {"progress": progress})
                self.logger.info(f"Job {job_id} progress: {progress}%")
                await asyncio.sleep(1)  # Simulate processing time
            
            # Create mock result data
            result = {
                "status": "success",
                "output": {
                    "images": [f"mock_image_{uuid.uuid4()}.png"],
                    "parameters": job_data.get("params_summary", {})
                },
                "execution_time": 5.0
            }
            
            # Job completed successfully
            self.logger.info(f"Job {job_id} completed successfully in mock environment")
            
            # Announce job completion
            await self.announce_job_completion(job_id, result)
            
            # Reset worker state
            self.status = "idle"
            self.current_job = None
                    
        except Exception as e:
            self.logger.error(f"Error processing job {job_id}: {str(e)}")
            await self.update_job_status(job_id, "failed", {"error": str(e)})
            self.status = "idle"
            self.current_job = None
            
    async def update_job_status(self, job_id: str, status: str, metadata: Optional[Dict[str, Any]] = None):
        """Update job status in Redis API"""
        try:
            if not metadata:
                metadata = {}
                
            # Use the correct UpdateJobProgressMessage format
            message = {
                "type": "update_job_progress",  # Correct message type
                "job_id": job_id,
                "machine_id": MACHINE_ID,  # Required field
                "gpu_id": GPU_ID,  # Required field
                "status": status,
                "timestamp": time.time(),
                "progress": 0  # Default progress value
            }
            
            # Add optional fields if they exist in metadata
            if metadata:
                if "progress" in metadata:
                    message["progress"] = metadata["progress"]  # Override default if specified
                if "message" in metadata:
                    message["message"] = metadata["message"]
            
            # Track the last sent message for debugging
            self.last_sent_message = json.dumps(message)
            await self.ws.send_json(message)
            self.logger.info(f"Updated job {job_id} status to {status}")
            
        except Exception as e:
            self.logger.error(f"Failed to update job status: {str(e)}")
            
    async def announce_job_completion(self, job_id: str, result: Dict[str, Any]):
        """Announce job completion to the Redis API
        
        This is a dedicated method for job completion announcements, separate from
        regular status updates. It uses a specific message type to ensure job completions
        are properly recognized and forwarded to clients.
        """
        try:
            # First update the job status to completed (for backward compatibility)
            await self.update_job_status(job_id, "completed", result)
            
            # Send a job completion message that matches the expected CompleteJobMessage format
            message = {
                "type": "complete_job",  # Worker-to-hub message type for job completions
                "job_id": job_id,
                "machine_id": MACHINE_ID,
                "gpu_id": GPU_ID,
                "result": result,
                "timestamp": time.time()  # Add timestamp field
            }
            
            # Track the last sent message for debugging
            self.last_sent_message = json.dumps(message)
            await self.ws.send_json(message)
            self.logger.info(f"Announced completion of job {job_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to announce job completion: {str(e)}")
            
    async def send_test_message(self):
        """Send a test message to the Redis API that will be forwarded to clients"""
        # VERY OBVIOUS LOG MESSAGE TO PROVE LOGGING WORKS
        self.logger.info("🔴🔴🔴 TESTING WORKER LOGS - THIS SHOULD APPEAR IN THE LOGS 🔴🔴🔴")
        try:
            if self.ws and not self.ws.closed:
                test_job_id = f"test-{uuid.uuid4()}"
                self.logger.info(f"Sending test message with ID {test_job_id}")
                
                # Send a worker heartbeat message that matches the expected model format
                message = {
                    "type": "worker_heartbeat",
                    "worker_id": self.worker_id,
                    "status": "idle",
                    "load": 0.0
                }
                self.last_sent_message = json.dumps(message)
                await self.ws.send_json(message)
                
                self.logger.info(f"Test message sent with ID {test_job_id}")
                return True
            else:
                self.logger.warning("Cannot send test message: WebSocket closed")
                return False
        except Exception as e:
            self.logger.error(f"Error sending test message: {str(e)}")
            return False
            
    async def run(self):
        """Main worker loop with robust reconnection handling"""
        reconnect_delay = 1.0  # Start with 1 second delay for reconnections
        max_reconnect_delay = 30.0  # Maximum reconnection delay in seconds
        consecutive_failures = 0  # Count consecutive connection failures
        
        self.logger.info(f"Starting worker {self.worker_id} main loop")
        
        # Initial connection to Redis API
        while self.running and not await self.connect_to_redis_api():
            self.logger.warning(f"Initial connection failed, retrying in {reconnect_delay} seconds...")
            await asyncio.sleep(reconnect_delay)
            # Exponential backoff with cap
            reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
        
        if not self.running:
            self.logger.info("Worker stopped during initial connection")
            return
            
        self.logger.info(f"Worker {self.worker_id} successfully connected and ready")
        reconnect_delay = 1.0  # Reset delay after successful connection
        consecutive_failures = 0  # Reset failure counter
            
        # Main message processing loop
        try:
            # Send an initial test message after connection
            await asyncio.sleep(2)  # Wait a moment for connection to stabilize
            await self.send_test_message()
            
            # Set up a task to send test messages periodically
            last_test_message_time = time.time()
            test_message_interval = 30  # Send a test message every 30 seconds
            
            while self.running:
                try:
                    # Ensure we have an active connection
                    if not self.ws or self.ws.closed:
                        self.logger.warning(f"WebSocket connection lost, attempting to reconnect in {reconnect_delay:.1f} seconds...")
                        await asyncio.sleep(reconnect_delay)  # Wait before reconnection
                        
                        # Attempt to reconnect
                        if await self.connect_to_redis_api():
                            self.logger.info("Successfully reconnected to Redis API")
                            reconnect_delay = 1.0  # Reset delay after successful reconnection
                            consecutive_failures = 0  # Reset failure counter
                            # Send a test message after reconnection
                            await self.send_test_message()
                            last_test_message_time = time.time()
                        else:
                            consecutive_failures += 1
                            # Exponential backoff with cap
                            reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
                            continue  # Skip to next iteration to try again
                    
                    # Send periodic test messages
                    current_time = time.time()
                    if current_time - last_test_message_time > test_message_interval:
                        await self.send_test_message()
                        last_test_message_time = current_time
                    
                    # Wait for messages with a timeout to allow for periodic connection check
                    try:
                        msg = await asyncio.wait_for(self.ws.receive(), timeout=10.0)
                    except asyncio.TimeoutError:
                        # No message received within timeout period, check connection and continue
                        if self.ws and not self.ws.closed:
                            self.logger.debug("No messages received in 10 seconds, connection appears healthy")
                            continue
                        else:
                            self.logger.warning("Connection appears to be broken, forcing reconnection")
                            self.ws = None
                            continue
                    
                    # Process received message
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        # Log every message received for debugging
                        self.logger.info(f"⚡ RAW MESSAGE RECEIVED: {msg.data}")
                        self.logger.info(f"⚡⚡⚡ MESSAGE LENGTH: {len(msg.data)} bytes")
                        try:
                            data = json.loads(msg.data)
                            
                            # Enhanced logging for error messages
                            if data.get("type") == "error":
                                self.logger.error(f"🚨 ERROR MESSAGE DETAILS: {json.dumps(data, indent=2)}")
                                self.logger.error(f"🚨 ERROR OCCURRED AFTER SENDING: {self.last_sent_message if hasattr(self, 'last_sent_message') else 'Unknown'}")
                            
                            # Handle different message types
                            message_type = data.get("type")
                            self.logger.info(f"📩 Processing message of type: {message_type}")
                            
                            if message_type == "connection_established":
                                self.logger.info(f"Connection established: {data.get('message', 'No message provided')}")
                                
                            elif message_type == "worker_registered":
                                self.logger.info(f"Worker registered successfully with status: {data.get('status', 'unknown')}")
                                
                            elif message_type == "error":
                                error_msg = data.get('error', 'Unknown error')
                                details = data.get('details', 'No details provided')
                                self.logger.error(f"Received error from hub: {error_msg}")
                                self.logger.error(f"Error details: {details}")
                                
                            elif message_type == "job_available" or message_type == "worker_notification":
                                # Log the full job notification message at INFO level to confirm broadcasts
                                job_id = data.get("job_id", "unknown")
                                job_type = data.get("job_type", "unknown")
                                
                                if message_type == "job_available":
                                    self.logger.info(f"🔔 BROADCAST RECEIVED: Job available notification for job {job_id} of type {job_type}")
                                    self.logger.info(f"Full job_available notification details: {data}")
                                else:  # worker_notification
                                    self.logger.info(f"🔔 WORKER NOTIFICATION RECEIVED: Job notification for job {job_id}")
                                    self.logger.info(f"Full worker_notification details: {data}")
                                
                                # Only handle if we're idle
                                if self.status == "idle" and self.current_job is None:
                                    job_id = data.get("job_id")
                                    job_type = data.get("job_type")
                                    
                                    self.logger.info(f"Received job notification for job {job_id} of type {job_type}")
                                    self.logger.info(f"Worker status: {self.status}, current_job: {self.current_job}")
                                    
                                    # Claim the job
                                    self.logger.info(f"Attempting to claim job {job_id}")
                                    claim_result = await self.claim_job(job_id, job_type)
                                    self.logger.info(f"Claim result for job {job_id}: {claim_result}")
                                    
                                    if claim_result:
                                        # Process the job immediately using the notification data
                                        self.logger.info(f"Processing job {job_id} using notification data")
                                        
                                        # Create a job data structure from the notification
                                        job_data = {
                                            "job_id": job_id,
                                            "job_type": job_type,
                                            "params_summary": data.get("params_summary", {}),
                                            "priority": data.get("priority", 0)
                                        }
                                        
                                        # Use create_task to run processing in the background
                                        self.logger.info(f"Starting job processing for {job_id}")
                                        asyncio.create_task(self.process_job(job_data))
                                    else:
                                        self.logger.warning(f"Failed to claim job {job_id}")
                        except json.JSONDecodeError:
                            self.logger.error(f"Received invalid JSON: {msg.data[:100]}...")
                        except Exception as e:
                            self.logger.error(f"Error processing message: {str(e)}")
                    
                    elif msg.type in [aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSE]:
                        self.logger.warning(f"WebSocket connection issue: {msg.type}")
                        self.ws = None  # Mark connection as needing reconnection
                        
                except Exception as e:
                    self.logger.error(f"Error in message processing loop: {str(e)}")
                    # Reset connection on unexpected errors
                    if self.ws and not self.ws.closed:
                        try:
                            await self.ws.close()
                        except Exception:
                            pass  # Ignore errors during close
                    self.ws = None
                    consecutive_failures += 1
                    # Exponential backoff with cap
                    reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
                    await asyncio.sleep(1)  # Brief pause before continuing
            
        except asyncio.CancelledError:
            self.logger.info("Worker task cancelled")
        except Exception as e:
            self.logger.error(f"Unexpected error in worker loop: {str(e)}")
        finally:
            # Clean up resources when worker is stopped
            self.logger.info(f"Worker {self.worker_id} shutting down")
            self.running = False
            
            # Cancel heartbeat task
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            # Close WebSocket connections
            if self.ws and not self.ws.closed:
                try:
                    await self.ws.close()
                except Exception as e:
                    self.logger.error(f"Error closing Redis API connection: {str(e)}")
                    
            if self.executor_ws and not self.executor_ws.closed:
                try:
                    await self.executor_ws.close()
                except Exception as e:
                    self.logger.error(f"Error closing Execution Service connection: {str(e)}")
                
async def main():
    parser = argparse.ArgumentParser(description="EmProps Worker")
    parser.add_argument("--worker-id", type=str, help="Worker ID")
    args = parser.parse_args()
    
    worker_id = args.worker_id or f"worker-{uuid.uuid4()}"
    worker = Worker(worker_id)
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        print("Worker stopping...")
    finally:
        print("Worker stopped")

if __name__ == "__main__":
    asyncio.run(main())
