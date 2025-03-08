#!/usr/bin/env python3
# Core WebSocket routes for the Redis queue system
import json
import logging
import asyncio
import uuid
import time
from typing import Dict, Any, Optional, List, Union
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .models import (
    MessageType, parse_message, 
    SubmitJobMessage, GetJobStatusMessage, RegisterWorkerMessage, GetNextJobMessage, 
    UpdateJobProgressMessage, CompleteJobMessage, GetStatsMessage, SubscribeStatsMessage,
    SubscribeJobMessage, JobAcceptedMessage, JobStatusMessage, JobUpdateMessage, JobAssignedMessage,
    JobCompletedMessage, ErrorMessage, WorkerRegisteredMessage, WorkerHeartbeatMessage, ClaimJobMessage,
    SubscribeJobNotificationsMessage, JobClaimedMessage, JobAvailableMessage
)
from .connections import ConnectionManager
from .redis_service import RedisService, STANDARD_QUEUE, PRIORITY_QUEUE

logger = logging.getLogger(__name__)

# Initialize services
redis_service = RedisService()
connection_manager = ConnectionManager()

# Message handler maps
client_message_handlers = {}
worker_message_handlers = {}

# Task to periodically broadcast system stats to subscribed clients
async def broadcast_stats_task():
    """Periodically fetch stats from Redis and broadcast to subscribed clients"""
    print("\n\n====== STARTING STATS BROADCAST TASK ======\n")
    logger.info("Starting periodic stats broadcast task")
    last_stats = None  # Track previous stats to detect changes
    broadcast_counter = 0
    
    while True:
        try:
            broadcast_counter += 1
            if broadcast_counter % 10 == 0:  # Every 10 cycles (10 seconds with sleep of 1)
                print(f"\n\n====== STATS BROADCAST CYCLE #{broadcast_counter} ======")
                print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Skip if no clients are subscribed
            subscribers_count = len(connection_manager.stats_subscriptions)
            if subscribers_count == 0:
                if broadcast_counter % 10 == 0:  # Only log every 10 cycles
                    logger.debug("No clients subscribed to stats updates, skipping broadcast")
                await asyncio.sleep(3)  # Check less frequently if no subscribers
                continue
                
            # Get stats from Redis
            stats = redis_service.get_stats()
            
            # Verify if we got valid stats
            if not stats:
                logger.error("Received empty stats from Redis")
                await asyncio.sleep(1)
                continue
                
            # Sanitize stats data (convert string values to integers)
            try:
                sanitized_stats = {
                    'type': MessageType.STATS_RESPONSE,
                    'queues': {
                        'priority': int(stats['queues']['priority']),
                        'standard': int(stats['queues']['standard']),
                        'total': int(stats['queues']['total'])
                    },
                    'jobs': {
                        'total': int(stats['jobs']['total']),
                        'status': {
                            k: int(v) for k, v in stats['jobs']['status'].items()
                        }
                    },
                    'workers': {
                        'total': int(stats['workers']['total']),
                        'status': {
                            k: int(v) for k, v in stats['workers']['status'].items()
                        }
                    }
                }
                
                # Check if stats have changed since last broadcast
                is_changed = last_stats != sanitized_stats
                
                # Only broadcast if stats changed or every 5 seconds regardless
                if is_changed or not last_stats or time.time() % 5 < 1:
                    response = sanitized_stats
                    await connection_manager.broadcast_stats(response)
                    
                    # Store current stats for future comparison
                    last_stats = sanitized_stats
                
            except Exception as e:
                logger.error(f"Error processing stats data: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in stats broadcast task: {str(e)}")
        
        # Wait before sending the next update
        await asyncio.sleep(1)
        
# Task to periodically clean up stale job claims
async def cleanup_stale_claims_task():
    """Periodically check for and reset stale job claims"""
    logger.info("Starting periodic stale claim cleanup task")
    
    while True:
        try:
            # Check for stale claims every 15 seconds
            stale_count = redis_service.cleanup_stale_claims()
            if stale_count > 0:
                logger.info(f"Cleaned up {stale_count} stale job claims")
                
        except Exception as e:
            logger.error(f"Error in stale claim cleanup task: {str(e)}")
        
        # Wait before next cleanup
        await asyncio.sleep(15)

# Task to periodically mark stale workers as out_of_service
async def mark_stale_workers_task():
    """Periodically check for and mark workers without recent heartbeats as out_of_service"""
    logger.info("Starting periodic stale worker detection task")
    
    while True:
        try:
            # Check for stale workers every 30 seconds
            stale_count = redis_service.mark_stale_workers_out_of_service(max_heartbeat_age=120)  # 2 minutes
            if stale_count > 0:
                logger.info(f"Marked {stale_count} workers as out_of_service due to missing heartbeats")
                
        except Exception as e:
            logger.error(f"Error in stale worker detection task: {str(e)}")
        
        # Wait before next check
        await asyncio.sleep(30)

def init_routes(app: FastAPI, redis_service: Optional[RedisService] = None, connection_manager: Optional[ConnectionManager] = None) -> None:
    """Initialize WebSocket routes with optional service dependencies
    
    Args:
        app: The FastAPI application
        redis_service: Optional Redis service instance (if not provided, uses global instance)
        connection_manager: Optional connection manager instance (if not provided, uses global instance)
    """
    # Use provided services or fall back to global instances
    # We need to handle the global variable shadowing issue
    global_redis_service = globals().get("redis_service")
    global_connection_manager = globals().get("connection_manager")
    
    # If parameters are provided, use them; otherwise fall back to global instances
    redis_service_env = redis_service or global_redis_service
    connection_manager_env = connection_manager or global_connection_manager
    
    # Update the global references for use within route handlers
    globals()["redis_service"] = redis_service_env
    globals()["connection_manager"] = connection_manager_env
    
    logger.info(f"Initializing WebSocket routes with Redis service: {redis_service_env}, Connection Manager: {connection_manager_env}")
    
    # Start background tasks
    app.add_event_handler("startup", broadcast_stats_task)
    app.add_event_handler("startup", cleanup_stale_claims_task)
    app.add_event_handler("startup", mark_stale_workers_task)
    app.add_event_handler("startup", start_redis_listener)
    
    # Log when the application is fully started
    @app.on_event("startup")
    async def on_startup():
        print("\n\n===================================================================")
        print("=== 🚀 WebSocket server fully initialized and ready for connections! ====")
        print("===================================================================\n\n")
        logger.info("WebSocket server fully initialized and ready to accept connections")

    @app.websocket("/ws/client/{client_id}")
    async def client_websocket(websocket: WebSocket, client_id: str):
        """WebSocket endpoint for clients"""
        # Print more visible connection logs
        print(f"\n\n==== CLIENT CONNECTION ATTEMPT: {client_id} ====\n")
        logger.info(f"New client WebSocket connection attempt: {client_id}")
        
        # Accept the connection
        try:
            await websocket.accept()
            connection_manager.client_connections[client_id] = websocket
            logger.info(f"Client WebSocket connected successfully: {client_id}")
            
            # Send an immediate welcome message
            welcome_message = {"type": "connection_established", "message": f"Welcome {client_id}! Connected to Redis Hub"}
            await websocket.send_text(json.dumps(welcome_message))
            
            print(f"\n==== CLIENT CONNECTED: {client_id} ====\n")
        except Exception as e:
            logger.error(f"Error accepting client connection {client_id}: {str(e)}")
            return
        
        try:
            while True:
                # Receive message from client
                message_text = await websocket.receive_text()
                
                # RAW MESSAGE DEBUGGING - Super visible
                print("\n\n**************************************************")
                print("*** RAW WEBSOCKET MESSAGE RECEIVED FROM CLIENT ***")
                print(f"*** CLIENT ID: {client_id} ***")
                print(f"*** RAW TEXT: {message_text} ***")
                print("**************************************************\n\n")
                
                # Parse message
                try:
                    message_data = json.loads(message_text)
                    logger.debug(f"Received message from client {client_id}: {message_data}")
                    message = parse_message(message_data)
                    
                    if not message:
                        logger.error(f"Invalid message received from client {client_id}")
                        error_message = ErrorMessage(error="Invalid message format")
                        await connection_manager.send_to_client(client_id, error_message)
                        continue
                        
                    # Process message based on type
                    if message.type == MessageType.SUBMIT_JOB:
                        await handle_submit_job(client_id, message)
                    elif message.type == MessageType.GET_JOB_STATUS:
                        await handle_get_job_status(client_id, message)
                    elif message.type == MessageType.SUBSCRIBE_JOB:
                        handle_subscribe_job(client_id, message)
                    elif message.type == MessageType.SUBSCRIBE_STATS:
                        handle_subscribe_stats(client_id, message)
                    elif message.type == MessageType.GET_STATS:
                        await handle_get_stats(client_id)
                    else:
                        logger.warning(f"Unhandled message type from client: {message.type}")
                        error_message = ErrorMessage(error=f"Unsupported message type: {message.type}")
                        await connection_manager.send_to_client(client_id, error_message)
                        
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received from client {client_id}")
                    error_message = ErrorMessage(error="Invalid JSON format")
                    await connection_manager.send_to_client(client_id, error_message)
                    
                except Exception as e:
                    logger.error(f"Error processing client message: {str(e)}")
                    error_message = ErrorMessage(error="Server error processing message")
                    await connection_manager.send_to_client(client_id, error_message)
                
        except WebSocketDisconnect:
            connection_manager.disconnect_client(client_id)
        
        except Exception as e:
            logger.error(f"Unexpected error in client WebSocket: {str(e)}")
            connection_manager.disconnect_client(client_id)
    
    @app.websocket("/ws/worker/{worker_id}")
    async def worker_websocket(websocket: WebSocket, worker_id: str):
        """WebSocket endpoint for workers"""
        # Print more visible connection logs
        print(f"\n\n==== WORKER CONNECTION ATTEMPT: {worker_id} ====\n")
        logger.info(f"New worker WebSocket connection attempt: {worker_id}")
        
        # Accept the connection
        try:
            logger.debug(f"[WORKER-CONN] Accepting WebSocket connection for worker {worker_id}")
            await websocket.accept()
            connection_manager.worker_connections[worker_id] = websocket
            connection_manager.worker_status[worker_id] = "idle"  # Set initial status to idle
            logger.info(f"[WORKER-CONN] Worker WebSocket connected successfully: {worker_id}")
            
            # Send an immediate welcome message
            welcome_message = {"type": "connection_established", "message": f"Welcome Worker {worker_id}! Connected to Redis Hub"}
            logger.debug(f"[WORKER-CONN] Sending welcome message to worker {worker_id}")
            await websocket.send_text(json.dumps(welcome_message))
            
            print(f"\n==== WORKER CONNECTED: {worker_id} ====\n")
        except Exception as e:
            logger.error(f"Error accepting worker connection {worker_id}: {str(e)}")
            return
        
        try:
            while True:
                # Receive message from worker
                message_text = await websocket.receive_text()
                
                # Log raw message for debugging
                print(f"\n\n🔍🔍🔍 RAW WORKER MESSAGE RECEIVED: {message_text}")
                print(f"🔍 Worker ID: {worker_id}")
                print(f"🔍 Message length: {len(message_text)} bytes")
                logger.info(f"[WORKER-MSG-RAW] Received raw message from worker {worker_id}: {message_text}")
                
                # Parse message
                try:
                    message_data = json.loads(message_text)
                    print(f"🔍 Parsed JSON: {json.dumps(message_data)}")
                    logger.info(f"[WORKER-MSG-PARSED] Parsed message data: {message_data}")
                    message = parse_message(message_data)
                    
                    if not message:
                        logger.error(f"Invalid message received from worker {worker_id}")
                        error_message = ErrorMessage(error="Invalid message format")
                        await connection_manager.send_to_worker(worker_id, error_message)
                        continue
                        
                    # Process message based on type
                    if message.type == MessageType.REGISTER_WORKER:
                        await handle_register_worker(worker_id, message)
                    elif message.type == MessageType.GET_NEXT_JOB:
                        await handle_get_next_job(worker_id, message)
                    elif message.type == MessageType.UPDATE_JOB_PROGRESS:
                        await handle_update_job_progress(worker_id, message)
                    elif message.type == MessageType.COMPLETE_JOB:
                        await handle_complete_job(worker_id, message)
                    # New message handlers for push-based notification system
                    elif message.type == MessageType.WORKER_HEARTBEAT:
                        await handle_worker_heartbeat(worker_id, message)
                    elif message.type == MessageType.CLAIM_JOB:
                        await handle_claim_job(worker_id, message)
                    elif message.type == MessageType.SUBSCRIBE_JOB_NOTIFICATIONS:
                        # Log the subscription attempt
                        logger.info(f"\n\n🔍🔍🔍 SUBSCRIPTION ATTEMPT FROM WORKER: {worker_id}")
                        logger.info(f"🔍 Message: {message}")
                        logger.info(f"🔍 Message type: {message.type}, Message dict: {message.dict()}")
                        
                        # Handle the subscription - use the worker_id from the connection, not from the message
                        # This is because the worker_id is already known from the WebSocket connection
                        handle_subscribe_job_notifications(worker_id, message)
                    else:
                        logger.warning(f"Unhandled message type from worker: {message.type}")
                        error_message = ErrorMessage(error=f"Unsupported message type: {message.type}")
                        await connection_manager.send_to_worker(worker_id, error_message)
                        
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received from worker {worker_id}")
                    error_message = ErrorMessage(error="Invalid JSON format")
                    await connection_manager.send_to_worker(worker_id, error_message)
                    
                except Exception as e:
                    logger.error(f"Error processing worker message: {str(e)}")
                    error_message = ErrorMessage(error="Server error processing message")
                    await connection_manager.send_to_worker(worker_id, error_message)
                
        except WebSocketDisconnect:
            connection_manager.disconnect_worker(worker_id)
            # Mark worker as disconnected in Redis
            redis_service.update_worker_status(worker_id, "disconnected")
        
        except Exception as e:
            logger.error(f"Unexpected error in worker WebSocket: {str(e)}")
            connection_manager.disconnect_worker(worker_id)
            # Mark worker as disconnected in Redis
            redis_service.update_worker_status(worker_id, "disconnected")

    # Client message handlers
    async def handle_submit_job(client_id: str, message: SubmitJobMessage):
        """Handle job submission from a client"""
        # Generate job ID if not provided
        job_id = f"job-{uuid.uuid4()}"
        
        print(f"\n\n🔵🔵🔵 JOB SUBMISSION 🔵🔵🔵")
        print(f"🔵 Client: {client_id}")
        print(f"🔵 Job ID: {job_id}")
        print(f"🔵 Job Type: {message.job_type}")
        print(f"🔵 Priority: {message.priority}")
        
        # Add job to Redis
        job_data = redis_service.add_job(
            job_id=job_id,
            job_type=message.job_type,
            priority=message.priority,
            params=message.payload,
            client_id=client_id
        )
        
        logger.info(f"[JOB-SUBMIT] New job {job_id} submitted by client {client_id} with priority {message.priority}")
        
        # Create job available notification for workers
        notification = JobAvailableMessage(
            job_id=job_id,
            job_type=message.job_type,
            priority=message.priority,
            params_summary=message.payload
        )
        
        # Send notification to idle workers and get count
        worker_count = await connection_manager.notify_idle_workers(notification)
        logger.info(f"[JOB-SUBMIT] Notified {worker_count} idle workers about job {job_id}")
        
        # Send confirmation response with worker count
        response = JobAcceptedMessage(
            job_id=job_id,
            position=job_data.get("position", -1),
            notified_workers=worker_count  # Include the count of notified workers
        )
        
        success = await connection_manager.send_to_client(client_id, response)
        print(f"🔵 Job acceptance sent to client: {success}")
        logger.info(f"[JOB-SUBMIT] Job acceptance message for {job_id} sent to client {client_id}: {success}")
        
        # Automatically subscribe client to job updates
        connection_manager.subscribe_to_job(job_id, client_id)
        print(f"🔵 Client {client_id} subscribed to job {job_id}")
        print(f"🔵🔵🔵 END JOB SUBMISSION 🔵🔵🔵\n\n")
    
    async def handle_get_job_status(client_id: str, message: GetJobStatusMessage):
        """Handle job status request from a client"""
        job_id = message.job_id
        
        # Get job status from Redis
        job_data = redis_service.get_job_status(job_id)
        
        if not job_data:
            error_message = ErrorMessage(error=f"Job {job_id} not found")
            await connection_manager.send_to_client(client_id, error_message)
            return
        
        # Create response
        response = JobStatusMessage(
            job_id=job_id,
            status=job_data.get("status", "unknown"),
            progress=int(job_data.get("progress", 0)) if "progress" in job_data else None,
            worker_id=job_data.get("worker"),
            started_at=float(job_data.get("started_at")) if "started_at" in job_data else None,
            completed_at=float(job_data.get("completed_at")) if "completed_at" in job_data else None,
            result=job_data.get("result"),
            message=job_data.get("message")
        )
        await connection_manager.send_to_client(client_id, response)
        
        # Subscribe client to future updates for this job
        connection_manager.subscribe_to_job(job_id, client_id)
    
    def handle_subscribe_job(client_id: str, message: SubscribeJobMessage):
        """Handle job subscription request from a client"""
        job_id = message.job_id
        connection_manager.subscribe_to_job(job_id, client_id)
    
    def handle_subscribe_stats(client_id: str, message: SubscribeStatsMessage):
        """Handle stats subscription request from a client"""
        if message.enabled:
            connection_manager.subscribe_to_stats(client_id)
        else:
            connection_manager.unsubscribe_from_stats(client_id)
    
    async def handle_get_stats(client_id: str):
        """Handle stats request from a client"""
        stats = redis_service.get_stats()
        await connection_manager.send_to_client(client_id, stats)
    
    # Worker message handlers
    async def handle_register_worker(worker_id: str, message: RegisterWorkerMessage):
        """Handle worker registration"""
        logger.info(f"[WORKER-REG] Processing registration for worker {worker_id}")
        
        # Get worker info from message
        worker_info = {
            "machine_id": message.machine_id,
            "gpu_id": message.gpu_id
        }
        
        # Register worker in Redis
        logger.debug(f"[WORKER-REG] Registering worker {worker_id} with info: {worker_info}")
        registration_success = redis_service.register_worker(worker_id, worker_info)
        logger.info(f"[WORKER-REG] Worker {worker_id} registration {'successful' if registration_success else 'failed'}")
        
        # Send confirmation
        response = WorkerRegisteredMessage(worker_id=worker_id)
        logger.debug(f"[WORKER-REG] Sending registration confirmation to worker {worker_id}")
        await connection_manager.send_to_worker(worker_id, response)
    
    async def handle_get_next_job(worker_id: str, message: GetNextJobMessage):
        """Handle worker request for next job"""
        # Update worker status to idle
        redis_service.update_worker_status(worker_id, "idle")
        
        # Update worker heartbeat
        redis_service.update_worker_heartbeat(worker_id)
        
        # Get next job from Redis
        job_data = redis_service.get_next_job(worker_id)
        
        if not job_data:
            # No job available, send empty response
            await connection_manager.send_to_worker(worker_id, {"type": "no_job"})
            return
        
        # Update worker status to active
        redis_service.update_worker_status(worker_id, "active")
        
        # Create response
        response = JobAssignedMessage(
            job_id=job_data["id"],
            job_type=job_data["type"],
            priority=int(job_data.get("priority", 0)),
            params=job_data["params"]
        )
        await connection_manager.send_to_worker(worker_id, response)
        
        # Notify client about job assignment if subscribed
        job_id = job_data["id"]
        update = JobUpdateMessage(
            job_id=job_id,
            status="processing",
            worker_id=worker_id
        )
        await connection_manager.send_job_update(job_id, update)
    
    async def handle_update_job_progress(worker_id: str, message: UpdateJobProgressMessage):
        """Handle worker job progress update"""
        job_id = message.job_id
        progress = message.progress
        status_message = message.message
        
        print(f"\n\n🟣🟣🟣 JOB PROGRESS UPDATE 🟣🟣🟣")
        print(f"🟣 Worker: {worker_id}")
        print(f"🟣 Job ID: {job_id}")
        print(f"🟣 Progress: {progress}%")
        print(f"🟣 Message: {status_message}")
        
        logger.info(f"[JOB-PROGRESS] Worker {worker_id} reported progress for job {job_id}: {progress}%")
        
        # Update worker heartbeat
        redis_service.update_worker_heartbeat(worker_id)
        
        # Update job progress in Redis
        redis_service.update_job_progress(job_id, progress, worker_id, status_message)
        
        # Create update message for client
        update = JobUpdateMessage(
            job_id=job_id,
            status="processing",
            progress=progress,
            message=status_message
        )
        
        # Send update to subscribed client
        client_notified = await connection_manager.send_job_update(job_id, update)
        print(f"🟣 Client notified about progress update: {client_notified}")
        logger.info(f"[JOB-PROGRESS] Client notified about job {job_id} progress update from worker {worker_id}: {client_notified}")
        print(f"🟣🟣🟣 END JOB PROGRESS UPDATE 🟣🟣🟣\n\n")
    
    async def handle_complete_job(worker_id: str, message: CompleteJobMessage):
        """Handle worker job completion notification"""
        job_id = message.job_id
        result = message.result
        
        print(f"\n\n🟢🟢🟢 JOB COMPLETION 🟢🟢🟢")
        print(f"🟢 Worker: {worker_id}")
        print(f"🟢 Job ID: {job_id}")
        print(f"🟢 Result: {result[:100]}..." if isinstance(result, str) and len(result) > 100 else f"🟢 Result: {result}")
        
        logger.info(f"[JOB-COMPLETE] Worker {worker_id} completed job {job_id}")
        
        # Update worker heartbeat
        redis_service.update_worker_heartbeat(worker_id)
        
        # Mark job as completed in Redis
        redis_service.complete_job(job_id, worker_id, result)
        
        # Update worker status back to idle
        redis_service.update_worker_status(worker_id, "idle")
        print(f"🟢 Worker {worker_id} status updated back to 'idle'")
        
        # Create completion message for client
        completion = JobCompletedMessage(
            job_id=job_id,
            result=result
        )
        
        # Send completion to subscribed client
        client_notified = await connection_manager.send_job_update(job_id, completion)
        print(f"🟢 Client notified about job completion: {client_notified}")
        logger.info(f"[JOB-COMPLETE] Client notified about job {job_id} completion from worker {worker_id}: {client_notified}")
        print(f"🟢🟢🟢 END JOB COMPLETION 🟢🟢🟢\n\n")
        
    # Worker handlers for push-based notification system
    async def handle_worker_heartbeat(worker_id: str, message: WorkerHeartbeatMessage):
        """Handle worker heartbeat and status update"""
        logger.debug(f"[WORKER-HB] Received heartbeat from worker {worker_id}, status: {message.status}")
        
        # Check if worker exists in Redis
        worker_exists = redis_service.worker_exists(worker_id)
        if not worker_exists:
            logger.warning(f"[WORKER-HB] Worker {worker_id} not registered in Redis but sent heartbeat")
            # Try to re-register the worker with minimal info
            worker_info = {
                "machine_id": "unknown",  # We don't have this info from heartbeat
                "gpu_id": "unknown"      # We don't have this info from heartbeat
            }
            redis_service.register_worker(worker_id, worker_info)
            logger.info(f"[WORKER-HB] Auto-registered missing worker {worker_id}")
        
        # Update worker heartbeat and status in Redis
        updated = redis_service.update_worker_heartbeat(worker_id, message.status)
        
        if not updated:
            logger.warning(f"[WORKER-HB] Failed to update heartbeat for worker {worker_id}")
            return
            
        # Update worker status in connection manager
        connection_manager.update_worker_status(worker_id, message.status)
        
        logger.debug(f"[WORKER-HB] Updated heartbeat for worker {worker_id}, status: {message.status}")
    
    async def handle_claim_job(worker_id: str, message: ClaimJobMessage):
        """Handle job claim request from a worker"""
        job_id = message.job_id
        claim_timeout = message.claim_timeout
        
        # Try to claim the job
        job_data = redis_service.claim_job(job_id, worker_id, claim_timeout)
        
        # Prepare response
        if job_data:
            # Update worker status to busy
            connection_manager.update_worker_status(worker_id, "busy")
            redis_service.update_worker_status(worker_id, "busy")
            
            # Send successful claim response
            response = JobClaimedMessage(
                job_id=job_id,
                worker_id=worker_id,
                success=True,
                job_data=job_data
            )
        else:
            # Send failed claim response
            response = JobClaimedMessage(
                job_id=job_id,
                worker_id=worker_id,
                success=False,
                message="Job not available or already claimed"
            )
        
        await connection_manager.send_to_worker(worker_id, response)
        
        # If claim was successful, publish job update
        if job_data:
            redis_service.publish_job_update(job_id, "claimed", worker_id=worker_id)
            
            # Notify client about job status change
            if job_id in connection_manager.job_subscriptions:
                client_id = connection_manager.job_subscriptions[job_id]
                update = JobUpdateMessage(
                    job_id=job_id,
                    status="claimed",
                    worker_id=worker_id
                )
                await connection_manager.send_to_client(client_id, update)
    
    def handle_subscribe_job_notifications(worker_id: str, message: SubscribeJobNotificationsMessage):
        """Handle worker subscription to job notifications"""
        if message.enabled:
            connection_manager.subscribe_worker_to_job_notifications(worker_id)
            logger.info(f"Worker {worker_id} subscribed to job notifications")
        else:
            connection_manager.unsubscribe_worker_from_job_notifications(worker_id)
            logger.info(f"Worker {worker_id} unsubscribed from job notifications")

# Redis Pub/Sub listener for job updates and notifications
async def start_redis_listener():
    """Start listening for Redis pub/sub messages"""
    print("\n\n==========================================")
    print("=== 🔄 STARTING REDIS PUB/SUB LISTENER ====")
    print("==========================================\n\n")
    logger.info("Starting Redis pub/sub listener")
    
    # Connect to Redis async client
    try:
        await redis_service.connect_async()
        logger.info("Successfully connected to Redis async client")
    except Exception as e:
        logger.error(f"Failed to connect to Redis async client: {str(e)}")
        print("\n\n====================================================")
        print("=== ⚠️ REDIS CONNECTION FAILED ===")
        print(f"=== ERROR: {str(e)} ===")
        print("====================================================\n\n")
        return
        
    # Define job update message handler
    async def handle_job_update(message):
        try:
            # Log the raw message
            print("\n\n===================================================")
            print("=== PUB/SUB JOB UPDATE MESSAGE RECEIVED ===")
            print(f"=== CHANNEL: {message.get('channel')} ===")
            print(f"=== DATA: {message.get('data')} ===")
            print("===================================================\n\n")
            
            # Parse message data
            data = json.loads(message["data"])
            job_id = data.get("job_id")
            
            if job_id:
                # Check for subscribed client
                await connection_manager.send_job_update(job_id, data)
                logger.info(f"Successfully forwarded job update for job {job_id}")
        except Exception as e:
            logger.error(f"Error handling Redis job update message: {str(e)}")
    
    # Define job notification message handler
    async def handle_job_notification(message):
        try:
            # Log the raw message
            print("\n\n==========================================================")
            print("=== PUB/SUB JOB NOTIFICATION MESSAGE RECEIVED ===")
            print(f"=== CHANNEL: {message.get('channel')} ===")
            print(f"=== DATA: {message.get('data')} ===")
            print("==========================================================\n\n")
            
            # Parse message data
            data = json.loads(message["data"])
            message_type = data.get("type")
            logger.debug(f"Processing notification message of type: {message_type}")
            
            if message_type == "job_available":
                job_id = data.get("job_id")
                job_type = data.get("job_type")
                
                if job_id and job_type:
                    # Log job details
                    logger.info(f"New job available: ID={job_id}, Type={job_type}")
                    
                    # Create job available notification message
                    notification = JobAvailableMessage(
                        job_id=job_id,
                        job_type=job_type,
                        params_summary=data.get("params")
                    )
                    
                    # Send notification to idle workers
                    worker_count = await connection_manager.notify_idle_workers(notification)
                    logger.info(f"Notified {worker_count} idle workers about job {job_id}")
            
        except Exception as e:
            logger.error(f"Error handling Redis job notification message: {str(e)}")
            print("\n\n===================================================")
            print("=== ⚠️ ERROR PROCESSING JOB NOTIFICATION ===")
            print(f"=== ERROR: {str(e)} ===")
            print("===================================================\n\n")
    
    # Subscribe to channels
    try:
        logger.info("Subscribing to Redis channels: job_updates, job_notifications")
        await redis_service.subscribe_to_channel("job_updates", handle_job_update)
        await redis_service.subscribe_to_channel("job_notifications", handle_job_notification)
        logger.info("Successfully subscribed to all Redis channels")
        print("\n\n==================================================")
        print("=== 🔔 REDIS PUB/SUB SUBSCRIPTIONS ACTIVE ===")
        print("==================================================\n\n")
    except Exception as e:
        logger.error(f"Failed to subscribe to Redis channels: {str(e)}")
        print("\n\n====================================================")
        print("=== ⚠️ REDIS PUB/SUB SUBSCRIPTION FAILED ===")
        print(f"=== ERROR: {str(e)} ===")
        print("====================================================\n\n")

# Function to listen for Redis pub/sub messages
async def listen_for_messages(pubsub):
    """Listen for messages on Redis pub/sub"""
    logger.info("Starting Redis pub/sub message listener loop")
    message_counter = 0
    
    while True:
        try:
            # Get message
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            
            if not message:
                await asyncio.sleep(0.01)  # Short sleep to prevent CPU spinning
                continue
                
            message_counter += 1
            
            # Log message received in a very visible way occasionally
            if message_counter % 5 == 0:  # Every 5 messages
                print("\n\n***************************************")
                print(f"*** REDIS PUB/SUB MESSAGE #{message_counter} ***")
                print(f"*** CHANNEL: {message['channel'].decode('utf-8')} ***")
                print("***************************************\n\n")
                
            # Process message based on channel
            try:
                channel = message['channel'].decode('utf-8')
                data = message['data'].decode('utf-8')
                
                logger.debug(f"Processing message from channel '{channel}': {data}")
                
                if channel == "job_updates":
                    await process_job_update(json.loads(data))
                elif channel == "worker_updates":
                    await process_worker_update(json.loads(data))
                elif channel == "job_available":
                    await process_job_available(json.loads(data))
                else:
                    logger.warning(f"Received message on unknown channel: {channel}")
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from message: {message['data']}")
            except Exception as e:
                logger.error(f"Error processing Redis message: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in Redis pub/sub listener: {str(e)}")
            print("\n\n**************************************************")
            print("*** ⚠️ ERROR IN REDIS PUB/SUB LISTENER ***")
            print(f"*** ERROR: {str(e)} ***")
            print("**************************************************\n\n")
            # Implement exponential backoff for reconnection attempts
            retry_delay = 1
            max_retry_delay = 30
            for attempt in range(1, 6):  # 5 retry attempts
                logger.warning(f"Redis pub/sub connection retry attempt {attempt}/5 in {retry_delay}s")
                await asyncio.sleep(retry_delay)
                try:
                    # Try to ping Redis to check connection
                    await redis_service.ping_async()
                    logger.info("Redis connection restored")
                    break
                except Exception:
                    logger.error(f"Redis reconnection attempt {attempt} failed")
                    retry_delay = min(retry_delay * 2, max_retry_delay)  # Exponential backoff with a cap

# Helper functions for message processing
async def process_job_update(data):
    """Process a job update message"""
    job_id = data.get("job_id")
    status = data.get("status")
    worker_id = data.get("worker_id")
    
    if not job_id or not status:
        logger.error(f"Invalid job update message: {data}")
        return
        
    logger.info(f"Processing job update: job_id={job_id}, status={status}, worker_id={worker_id or 'N/A'}")
    
    # Forward update to subscribed clients
    await connection_manager.send_job_update(job_id, data)

async def process_worker_update(data):
    """Process a worker update message"""
    worker_id = data.get("worker_id")
    status = data.get("status")
    
    if not worker_id:
        logger.error(f"Invalid worker update message: {data}")
        return
        
    logger.info(f"Processing worker update: worker_id={worker_id}, status={status or 'N/A'}")
    
    # Update local worker status tracking
    if status:
        connection_manager.update_worker_status(worker_id, status)

async def process_job_available(data):
    """Process a job available message"""
    job_id = data.get("job_id")
    job_type = data.get("job_type")
    
    if not job_id or not job_type:
        logger.error(f"Invalid job available message: {data}")
        return
        
    logger.info(f"Processing job available: job_id={job_id}, job_type={job_type}")
    
    # Create notification message
    notification = JobAvailableMessage(
        job_id=job_id,
        job_type=job_type,
        params_summary=data.get("params")
    )
    
    # Notify idle workers
    worker_count = await connection_manager.notify_idle_workers(notification)
    logger.info(f"Notified {worker_count} idle workers about job {job_id}")
