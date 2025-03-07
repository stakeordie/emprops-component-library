#!/usr/bin/env python3
# API Container - Frontend HTTP API for Redis Queue
import json
import uuid
import logging
import os
import sys
import asyncio
import aiohttp
import random
import time
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Configure logging with a simpler, direct approach
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "DEBUG"),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api-service")
logger.info("STARTING API SERVER WITH BASIC LOGGING SETUP")

# Get Redis API connection details from environment variables
REDIS_API_HOST = os.environ.get("REDIS_API_HOST", "hub")
REDIS_API_PORT = os.environ.get("REDIS_API_PORT", "8001")
REDIS_API_WS_URL = f"ws://{REDIS_API_HOST}:{REDIS_API_PORT}/ws/client"
REDIS_API_HTTP_URL = f"http://{REDIS_API_HOST}:{REDIS_API_PORT}"

# Create FastAPI application
app = FastAPI(title="EmProps Queue API", version="1.0.0")

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for API interactions
class JobSubmission(BaseModel):
    job_type: str
    priority: Optional[int] = 0
    params: Dict[str, Any]

class JobStatusRequest(BaseModel):
    job_id: str

# Client connections and job updates store
client_websockets = {}
job_status_updates = {}

# WebSocket connection to Redis API
redis_ws_connection = None
client_id = f"api-{uuid.uuid4()}"

async def connect_to_redis_api(max_retries=5):
    """Connect to Redis API WebSocket with exponential backoff retry
    
    Args:
        max_retries: Maximum number of retry attempts (default: 5)
        
    Returns:
        bool: True if connection was successful, False otherwise
    """
    global redis_ws_connection
    
    # Initialize backoff parameters
    base_delay = 1.0  # Starting delay in seconds
    max_delay = 30.0  # Maximum delay in seconds
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            # If this is a retry, calculate the delay with exponential backoff and jitter
            if retry_count > 0:
                # Calculate backoff delay: min(max_delay, base_delay * 2^retry_count) + small random jitter
                delay = min(max_delay, base_delay * (2 ** (retry_count - 1))) + (0.1 * random.random())
                logger.info(f"Retry attempt {retry_count}/{max_retries}, waiting {delay:.2f} seconds before reconnecting")
                await asyncio.sleep(delay)
            
            logger.info(f"Connecting to Redis API at {REDIS_API_WS_URL}/{client_id}")
            session = aiohttp.ClientSession()
            redis_ws_connection = await session.ws_connect(f"{REDIS_API_WS_URL}/{client_id}")
            logger.info("Successfully connected to Redis API WebSocket")
            
            # Start listener task for Redis API messages
            asyncio.create_task(listen_to_redis_api())
            
            return True
            
        except Exception as e:
            retry_count += 1
            if retry_count > max_retries:
                logger.error(f"Failed to connect to Redis API after {max_retries} attempts: {str(e)}")
                return False
            
            logger.warning(f"Connection attempt {retry_count} failed: {str(e)}")
    
    return False

async def listen_to_redis_api():
    """Listen for messages from Redis API"""
    global redis_ws_connection
    
    while True:
        try:
            if not redis_ws_connection:
                logger.error("Redis API connection lost, attempting to reconnect...")
                if await connect_to_redis_api(max_retries=10):  # More retries for mid-operation reconnects
                    continue
                else:
                    logger.error("Failed to reconnect to Redis API, will retry again in 10 seconds")
                    await asyncio.sleep(10)
                    continue
                    
            # Log that we're listening for messages    
            print(f"\n[DEBUG] Waiting for message from Redis API...")
            
            # Receive message from Redis API
            msg = await redis_ws_connection.receive()
            
            if msg.type == aiohttp.WSMsgType.TEXT:
                # Print raw message first for debugging
                print(f"\n===== COMM VERIFICATION =====")
                print(f"STEP 3: REDIS API MESSAGE RECEIVED BY SERVER")
                print(f"TIME: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"RAW DATA: {msg.data[:200]}..." if len(msg.data) > 200 else f"RAW DATA: {msg.data}")
                
                data = json.loads(msg.data)
                message_type = data.get("type", "unknown")
                job_id = data.get("job_id")
                tracking_id = data.get("_tracking_id", "unknown")
                
                print(f"MESSAGE TYPE: {message_type}")
                print(f"JOB ID: {job_id if job_id else 'N/A'}")
                print(f"TRACKING ID: {tracking_id}")
                print(f"==============================\n")
                
                # Log all received messages in detail
                logger.info(f"📩 RECEIVED FROM REDIS API: type={message_type}, job_id={job_id if job_id else 'N/A'}")
                logger.debug(f"Full message content: {data}")
                
                # Handle different message types
                if message_type in ["job_status", "job_update", "job_accepted", "job_completed", "job_assigned", "worker_notification", "error"]:
                    # Store job update if it has a job_id
                    if job_id:
                        # ENHANCED: Make sure job status is always included
                        if "status" not in data and message_type == "job_completed":
                            data["status"] = "completed"
                        elif "status" not in data and message_type == "job_accepted":
                            data["status"] = "pending"
                        
                        # Store the update
                        job_status_updates[job_id] = data
                        print(f"\n=== JOB MESSAGE RECEIVED AND STORED ===\nTYPE: {message_type}\nJOB: {job_id}\nSTATUS: {data.get('status', 'N/A')}\n====================================")
                        
                        # CRITICAL FIX: Generate proper job_status message when receiving job_completed
                        # This ensures clients get appropriate status updates when jobs complete
                        if message_type == "job_completed" and data.get("status") != "completed":
                            print(f"\n!!! FIXING JOB COMPLETED MESSAGE - ADDING STATUS FIELD !!!")
                            data["status"] = "completed"
                            
                        # CRITICAL FIX: Also send a separate job_status message in addition to specialized messages
                        # This ensures all clients understand the update regardless of their implementation
                        status_message = {
                            "type": "job_status",
                            "job_id": job_id,
                            "status": data.get("status", "unknown"),
                            "timestamp": data.get("timestamp", time.time())
                        }
                        
                        # Add other useful fields if present
                        for field in ["progress", "position", "priority", "error", "result"]:
                            if field in data:
                                status_message[field] = data[field]
                        
                        # Log and store the additional status message
                        print(f"GENERATED ADDITIONAL JOB STATUS MESSAGE:\n{json.dumps(status_message, indent=2)}")
                        job_status_updates[f"{job_id}_status"] = status_message
                        
                        # Forward both the original message and the status message to clients
                        print(f"\n[BROADCAST] Forwarding original {message_type} message for job {job_id}")
                        await broadcast_message(data)
                        
                        # Special handling for job_accepted messages - Generate worker notification message
                        if message_type == "job_accepted":
                            # Create a synthetic worker notification message to inform client that workers were notified
                            worker_notification_message = {
                                "type": "worker_notification",
                                "job_id": job_id,
                                "message": f"Job {job_id} has been broadcast to available GPU workers",
                                "worker_count": data.get("notified_workers", 0),  # Use actual count from the hub
                                "timestamp": time.time()
                            }
                            print(f"\n[BROADCAST] Generating and forwarding worker notification message for job {job_id}")
                            print(f"WORKER NOTIFICATION MESSAGE:\n{json.dumps(worker_notification_message, indent=2)}")
                            await broadcast_message(worker_notification_message)
                        
                        # Special handling for job_assigned messages
                        elif message_type == "job_assigned":
                            # Enhance with worker details message
                            worker_id = data.get("worker_id", "unknown-worker")
                            assignment_message = {
                                "type": "worker_assignment",
                                "job_id": job_id,
                                "worker_id": worker_id,
                                "message": f"Job {job_id} has been assigned to worker {worker_id}",
                                "status": "processing",
                                "timestamp": time.time()
                            }
                            print(f"\n[BROADCAST] Generating and forwarding worker assignment message for job {job_id}")
                            print(f"WORKER ASSIGNMENT MESSAGE:\n{json.dumps(assignment_message, indent=2)}")
                            await broadcast_message(assignment_message)
                        
                        # Send the additional job_status message if this wasn't already a status message
                        if message_type != "job_status":
                            print(f"\n[BROADCAST] Forwarding additional job_status message for job {job_id}")
                            await broadcast_message(status_message)
                    else:
                        # Just forward the message without job_id
                        logger.info(f"📤 Forwarding {message_type} message without job_id to {len(client_websockets)} clients")
                        await broadcast_message(data)
                    
                elif message_type in ["stats_response", "worker_notification", "worker_assignment"]:
                    # Forward stats responses and worker messages to clients
                    logger.info(f"📊 Forwarding {message_type} message to {len(client_websockets)} clients")
                    await broadcast_message(data)
                    
                else:
                    # Log unhandled message types but still forward them
                    logger.warning(f"⚠️ Unhandled message type: {message_type}. Full message: {data}")
                    logger.info(f"📤 Forwarding unhandled message to {len(client_websockets)} clients")
                    await broadcast_message(data)
                
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                logger.warning("Redis API WebSocket connection closed")
                redis_ws_connection = None
                
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"Redis API WebSocket connection error: {msg.data}")
                redis_ws_connection = None
                
        except Exception as e:
            logger.error(f"Error listening to Redis API: {str(e)}")
            print(f"\n!!! EXCEPTION IN REDIS LISTENER: {str(e)} !!!")
            redis_ws_connection = None
            await asyncio.sleep(5)

async def broadcast_job_update(job_id: str, update: Dict[str, Any]):
    """Broadcast job update to connected clients"""
    for client_ws in list(client_websockets.values()):
        try:
            await client_ws.send_text(json.dumps(update))
        except Exception as e:
            logger.error(f"Error sending update to client: {str(e)}")

async def broadcast_message(message: Dict[str, Any]):
    """Broadcast any message to all connected clients"""
    message_type = message.get("type", "unknown")
    job_id = message.get("job_id", "N/A")
    
    # ENHANCED LOGGING: Direct console prints for maximum visibility
    print(f"\n===== BROADCASTING MESSAGE: {message_type} =====")
    print(f"JOB ID: {job_id}")
    print(f"MESSAGE CONTENT: {json.dumps(message, indent=2)}")
    print(f"CLIENT COUNT: {len(client_websockets)}")
    print(f"CLIENT IDs: {list(client_websockets.keys())}")
    
    # Get list of connected clients
    client_list = list(client_websockets.values())
    if not client_list:
        print(f"CRITICAL: No clients connected to forward {message_type} message to!")
        logger.warning(f"⚠️ No clients connected to forward {message_type} message to!")
        return
        
    success_count = 0
    error_count = 0
    
    for client_id, client_ws in list(client_websockets.items()):  # Use list() to allow modification during iteration
        try:
            # Check if websocket is connected before sending
            if hasattr(client_ws, 'client_state') and client_ws.client_state.name != "CONNECTED":
                print(f"SKIPPING client {client_id}: WebSocket not in CONNECTED state (current state: {client_ws.client_state.name})")
                # Clean up bad connection
                del client_websockets[client_id]
                error_count += 1
                continue
                
            print(f"SENDING to client {client_id}...")
            message_json = json.dumps(message)
            await client_ws.send_text(message_json)
            success_count += 1
            print(f"SUCCESS: Sent {message_type} message to client {client_id}")
            logger.debug(f"✅ Successfully sent {message_type} message to client {client_id}")
        except Exception as e:
            error_count += 1
            print(f"ERROR sending to client {client_id}: {str(e)}")
            logger.error(f"❌ Error sending {message_type} message to client {client_id}: {str(e)}")
            # Remove failed client connection
            if client_id in client_websockets:
                del client_websockets[client_id]
                print(f"REMOVED failed client {client_id} from active connections")
    
    # Summary log after broadcasting to all clients
    print(f"===== BROADCAST COMPLETE: {success_count} successes, {error_count} failures =====\n")
    logger.info(f"📢 Broadcast {message_type} message for job {job_id}: {success_count} successes, {error_count} failures")

# API Routes
@app.post("/jobs")
async def create_job(job: JobSubmission):
    """Submit a new job to the queue"""
    try:
        # Generate job ID
        job_id = f"job-{uuid.uuid4()}"
        
        # Prepare message for Redis API
        message = {
            "type": "submit_job",
            "job_type": job.job_type,
            "priority": job.priority,
            "payload": job.params
        }
        
        # Send message to Redis API
        if not redis_ws_connection:
            if not await connect_to_redis_api():
                raise HTTPException(status_code=503, detail="Cannot connect to Redis API")
                
        await redis_ws_connection.send_json(message)
        
        # Wait for job acceptance confirmation
        for _ in range(10):  # 5-second timeout
            if job_id in job_status_updates:
                return job_status_updates[job_id]
            await asyncio.sleep(0.5)
            
        return {"job_id": job_id, "status": "pending", "message": "Job submitted, no confirmation yet"}
        
    except Exception as e:
        logger.error(f"Error submitting job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting job: {str(e)}")

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a specific job"""
    try:
        # Check if we have a recent status update cached
        if job_id in job_status_updates:
            return job_status_updates[job_id]
            
        # Request status from Redis API
        if not redis_ws_connection:
            if not await connect_to_redis_api():
                raise HTTPException(status_code=503, detail="Cannot connect to Redis API")
                
        message = {
            "type": "get_job_status",
            "job_id": job_id
        }
        
        await redis_ws_connection.send_json(message)
        
        # Wait for status response
        for _ in range(10):  # 5-second timeout
            if job_id in job_status_updates:
                return job_status_updates[job_id]
            await asyncio.sleep(0.5)
            
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found or status unavailable")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting job status: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get queue system stats"""
    try:
        # Request stats from Redis API
        if not redis_ws_connection:
            if not await connect_to_redis_api():
                raise HTTPException(status_code=503, detail="Cannot connect to Redis API")
                
        message = {
            "type": "get_stats"
        }
        
        await redis_ws_connection.send_json(message)
        
        # Wait for stats response
        for _ in range(10):  # 5-second timeout
            msg = await redis_ws_connection.receive()
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                if data.get("type") == "stats_response":
                    return data
            await asyncio.sleep(0.5)
            
        raise HTTPException(status_code=504, detail="Timeout waiting for stats")
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.websocket("/ws/client/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for clients to receive real-time updates"""
    # Direct stdout prints for debugging to ensure visibility
    print(f"\n\n===== COMM VERIFICATION =====")
    print(f"STEP 1: CLIENT-TO-SERVER CONNECTION ESTABLISHED")
    print(f"CLIENT ID: {client_id}")
    print(f"CONNECTION TIME: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"==============================\n\n")
    
    # Accept the connection and register the client
    await websocket.accept()
    client_websockets[client_id] = websocket
    print(f"\n[DEBUG] Client {client_id} registered in client_websockets dictionary")
    print(f"[DEBUG] Total connected clients: {len(client_websockets)}")
    
    try:
        # Subscribe to stats updates
        if redis_ws_connection:
            logger.info(f"🔄 Subscribing to stats updates for client {client_id}")
            await redis_ws_connection.send_json({
                "type": "subscribe_stats",
                "enabled": True
            })
        
        # Log client connection
        logger.info(f"🔌 Client {client_id} connected via WebSocket")
        
        # Send a welcome message to verify the client connection is working
        welcome_msg = {"type": "welcome", "message": f"Connected to API WebSocket server. Client ID: {client_id}"}
        await websocket.send_text(json.dumps(welcome_msg))
        logger.info(f"👋 Sent welcome message to client {client_id}")
        
        # CRITICAL FIX: Send cached job updates to new client
        # This ensures clients immediately receive the status of all active jobs
        if job_status_updates:
            print(f"\n===== SENDING CACHED JOB UPDATES TO NEW CLIENT {client_id} =====")
            print(f"Number of cached updates: {len(job_status_updates)}")
            
            # First, collect only the primary job status entries (not the _status suffixed ones)
            primary_updates = {}
            for job_id, update in job_status_updates.items():
                if not job_id.endswith('_status'):
                    primary_updates[job_id] = update
                    
            print(f"Number of primary job updates to send: {len(primary_updates)}")
            
            # Send each cached job update to the new client
            for job_id, update in primary_updates.items():
                try:
                    print(f"Sending cached update for job {job_id} to new client {client_id}")
                    await websocket.send_text(json.dumps(update))
                    
                    # Also send a standard job_status update which is more compatible with some clients
                    status_key = f"{job_id}_status"
                    if status_key in job_status_updates:
                        print(f"Sending additional job_status update for job {job_id} to new client")
                        await websocket.send_text(json.dumps(job_status_updates[status_key]))
                except Exception as e:
                    print(f"Error sending cached job update to new client: {str(e)}")
            
            print(f"===== FINISHED SENDING CACHED UPDATES =====\n")
        else:
            print(f"No cached job updates to send to client {client_id}")
        
        while True:
            # Keep the connection alive and process client messages
            data = await websocket.receive_text()
            
            # Print raw message for debugging
            print(f"\n===== RAW CLIENT MESSAGE FROM {client_id} =====\n{data}\n=============================")
            
            # Process client commands
            try:
                message = json.loads(data)
                message_type = message.get("type", "unknown")
                
                # Log client message in detail
                logger.info(f"📥 RECEIVED FROM CLIENT {client_id}: type={message_type}")
                logger.debug(f"Full message from client: {message}")
                
                if redis_ws_connection and redis_ws_connection.closed == False:
                    # Forward client message to Redis API
                    logger.info(f"📤 Forwarding {message_type} message from client {client_id} to Redis API")
                    
                    # Enhanced diagnostic logs for communication verification
                    print(f"\n===== COMM VERIFICATION =====")
                    print(f"STEP 2: CLIENT MESSAGE FORWARDED TO REDIS API")
                    print(f"MESSAGE TYPE: {message_type}")
                    print(f"CLIENT ID: {client_id}")
                    print(f"TIME: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Log the actual message content with tracking ID
                    tracking_id = f"msg-{int(time.time())}-{random.randint(1000,9999)}"
                    message['_tracking_id'] = tracking_id
                    print(f"TRACKING ID: {tracking_id}")
                    print(f"CONTENT: {json.dumps(message, indent=2)}")
                    print(f"==============================\n")
                    
                    # Send the message to Redis API
                    await redis_ws_connection.send_json(message)
                    print(f"CONFIRMATION: Message {tracking_id} sent to Redis API successfully")
                    
                    # Special handling for submit_job messages
                    if message_type == "submit_job":
                        job_type = message.get('job_type', 'unknown')
                        priority = message.get('priority', 0)
                        logger.info(f"📋 JOB SUBMISSION from client {client_id}: type={job_type}, priority={priority}")
                        
                        # Print comprehensive debug for job submission
                        print(f"\n==== JOB SUBMISSION DETAILS =====")
                        print(f"CLIENT:   {client_id}")
                        print(f"JOB TYPE: {job_type}")
                        print(f"PRIORITY: {priority}")
                        print(f"PAYLOAD:  {json.dumps(message.get('payload', {}), indent=2)}")
                        print(f"=================================")
                        
                        # Generate a tracking ID to help match requests with responses
                        tracking_id = f"req-{int(time.time())}-{client_id[:8]}"
                        
                        # Acknowledge receipt to the client with the tracking ID
                        ack_msg = {
                            "type": "client_message_received",
                            "message": f"Job submission forwarded to processing service",
                            "tracking_id": tracking_id,
                            "job_type": job_type,
                            "timestamp": time.time()
                        }
                        print(f"[DEBUG] Sending acknowledgment to client: {json.dumps(ack_msg, indent=2)}")
                        await websocket.send_text(json.dumps(ack_msg))
                        print(f"[DEBUG] Acknowledgment sent successfully")
                        logger.info(f"📨 Sent acknowledgment for job submission to client {client_id} with tracking_id={tracking_id}")
                else:
                    # Redis connection is not available
                    error_msg = {"type": "error", "error": "Redis API connection not available"}
                    await websocket.send_text(json.dumps(error_msg))
                    logger.error(f"❌ Cannot forward message - Redis API connection not available")
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Received invalid JSON from client {client_id}: {data}")
            except Exception as e:
                logger.error(f"❌ Error processing client message from {client_id}: {str(e)}")
                logger.exception("Detailed exception information:")
                
    except WebSocketDisconnect:
        print(f"\n!!! CLIENT {client_id} DISCONNECTED !!!")
        logger.info(f"🔌 Client {client_id} disconnected")
        if client_id in client_websockets:
            del client_websockets[client_id]
            print(f"Removed client {client_id} from active connections. {len(client_websockets)} clients remaining.")
    
    except Exception as e:
        print(f"\n!!! WEBSOCKET ERROR WITH CLIENT {client_id}: {str(e)} !!!")
        logger.error(f"❌ WebSocket error with client {client_id}: {str(e)}")
        logger.exception("Detailed exception information:")
        if client_id in client_websockets:
            del client_websockets[client_id]
            print(f"Removed client {client_id} from active connections due to error.")

# Add direct prints for startup to verify logging works
print("\n\n")
print("***************************************")
print("*** STARTING API SERVER - HELLO!! ***")
print("***************************************")
print("\n\n")

@app.on_event("startup")
async def startup_event():
    """Connect to Redis API on startup"""
    print("\n@@@ STARTUP EVENT TRIGGERED @@@\n")
    await connect_to_redis_api()
    print("\n@@@ CONNECT_TO_REDIS_API COMPLETED @@@\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Close Redis API connection on shutdown"""
    global redis_ws_connection
    if redis_ws_connection:
        await redis_ws_connection.close()

@app.get("/test", response_class=HTMLResponse)
async def get_test_page():
    """Serve the WebSocket debug UI"""
    try:
        with open("static/ws-debug.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error serving test page: {str(e)}")
        return HTMLResponse(content=f"<html><body><h1>Error loading test page: {str(e)}</h1></body></html>")

@app.get("/sequence-monitor", response_class=HTMLResponse)
async def get_sequence_monitor():
    """Serve the Job Sequence Monitor UI"""
    try:
        with open("static/sequence-monitor.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error serving sequence monitor page: {str(e)}")
        return HTMLResponse(content=f"<html><body><h1>Error loading sequence monitor page: {str(e)}</h1></body></html>")

# Most basic print statement possible at the module level
print("\n\n!!! DIRECT CONSOLE OUTPUT FROM MODULE !!!\n\n")

if __name__ == "__main__":
    # Direct print that will show at runtime
    print("\n\n!!! MAIN BLOCK EXECUTED !!!\n\n")
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
