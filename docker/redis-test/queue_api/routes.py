#!/usr/bin/env python3
# WebSocket routes for the Redis queue system
import json
import logging
import asyncio
import uuid
import traceback
import time
from typing import Dict, Any, Optional, List, Union
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .models import (
    MessageType, parse_message, 
    SubmitJobMessage, GetJobStatusMessage, RegisterWorkerMessage, GetNextJobMessage, 
    UpdateJobProgressMessage, CompleteJobMessage, GetStatsMessage, SubscribeStatsMessage,
    SubscribeJobMessage, JobAcceptedMessage, JobStatusMessage, JobUpdateMessage, JobAssignedMessage,
    JobCompletedMessage, StatsResponseMessage, ErrorMessage, WorkerRegisteredMessage,
    Job
)
from .connections import ConnectionManager
from .redis_service import RedisService

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
                    print("No stats subscribers connected, waiting...")
                    logger.info("No stats subscribers, waiting...")
                await asyncio.sleep(3)  # Check less frequently if no subscribers
                continue
                
            # Get stats from Redis
            if broadcast_counter % 5 == 0:  # Every 5 cycles
                print(f"Fetching stats for {subscribers_count} subscribed clients")
                logger.info(f"Fetching stats for {subscribers_count} subscribed clients")
                
            stats = redis_service.get_stats()
            
            # Verify if we got valid stats
            if not stats:
                logger.error("Received empty stats from Redis")
                await asyncio.sleep(1)
                continue
                
            # Debug raw stats data every 10 cycles
            if broadcast_counter % 10 == 0:
                print(f"Raw Redis stats for cycle #{broadcast_counter}:\n{json.dumps(stats, indent=2)}")
            
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
                
                # Always compare and report changes even if we don't broadcast
                if is_changed and last_stats is not None:
                    print("\n🔄 STATS HAVE CHANGED - Details:")
                    
                    # Compare job counts
                    if last_stats['jobs'] != sanitized_stats['jobs']:
                        print("JOBS CHANGED:")
                        # Total job count
                        if last_stats['jobs']['total'] != sanitized_stats['jobs']['total']:
                            print(f"  - Total jobs: {last_stats['jobs']['total']} → {sanitized_stats['jobs']['total']}")
                        
                        # Job status counts
                        if last_stats['jobs']['status'] != sanitized_stats['jobs']['status']:
                            print("  - Job status counts:")
                            all_statuses = set(list(last_stats['jobs']['status'].keys()) + 
                                             list(sanitized_stats['jobs']['status'].keys()))
                            for status in all_statuses:
                                old_count = last_stats['jobs']['status'].get(status, 0)
                                new_count = sanitized_stats['jobs']['status'].get(status, 0)
                                if old_count != new_count:
                                    print(f"    - {status}: {old_count} → {new_count}")
                    
                    # Compare worker counts
                    if last_stats['workers'] != sanitized_stats['workers']:
                        print("WORKERS CHANGED:")
                        # Total worker count
                        if last_stats['workers']['total'] != sanitized_stats['workers']['total']:
                            print(f"  - Total workers: {last_stats['workers']['total']} → {sanitized_stats['workers']['total']}")
                        
                        # Worker status counts
                        if last_stats['workers']['status'] != sanitized_stats['workers']['status']:
                            print("  - Worker status counts:")
                            all_statuses = set(list(last_stats['workers']['status'].keys()) + 
                                             list(sanitized_stats['workers']['status'].keys()))
                            for status in all_statuses:
                                old_count = last_stats['workers']['status'].get(status, 0)
                                new_count = sanitized_stats['workers']['status'].get(status, 0)
                                if old_count != new_count:
                                    print(f"    - {status}: {old_count} → {new_count}")
                    
                    # Compare queue stats
                    if last_stats['queues'] != sanitized_stats['queues']:
                        print("QUEUES CHANGED:")
                        for queue in ['priority', 'standard', 'total']:
                            if last_stats['queues'][queue] != sanitized_stats['queues'][queue]:
                                print(f"  - {queue}: {last_stats['queues'][queue]} → {sanitized_stats['queues'][queue]}")
                    
                    logger.info("Stats have changed since last broadcast")
                else:
                    if broadcast_counter % 10 == 0:  # Only log every 10 cycles
                        print("Stats unchanged since last broadcast")
                        logger.debug("Stats unchanged since last broadcast")
                
                # Create stats response
                response = StatsResponseMessage(**sanitized_stats)
                
                # Only broadcast if stats changed or every 5 seconds regardless
                if is_changed or not last_stats or broadcast_counter % 5 == 0:
                    # Broadcast to all subscribed clients
                    sent_count = await connection_manager.broadcast_stats(response)
                    if is_changed or broadcast_counter % 10 == 0:  # Log on change or every 10 cycles
                        print(f"Broadcast stats to {sent_count} clients")
                        logger.info(f"Broadcast stats to {sent_count} clients")
                    
                    # Store current stats for future comparison
                    last_stats = sanitized_stats
                    
                    if broadcast_counter % 10 == 0:  # Only log every 10 cycles
                        print("Stats broadcast complete")
                
            except KeyError as ke:
                logger.error(f"Missing key in stats data: {str(ke)}")
                logger.error(f"Stats structure: {stats}")
            except ValueError as ve:
                logger.error(f"Value conversion error in stats: {str(ve)}")
                logger.error(f"Problem stats value: {stats}")
            
        except Exception as e:
            logger.error(f"Error in stats broadcast task: {str(e)}")
            logger.error(traceback.format_exc())
        
        # Wait before sending the next update (1 second interval)
        await asyncio.sleep(1)

def init_routes(app: FastAPI) -> None:
    """Initialize WebSocket routes"""

    @app.websocket("/ws/client/{client_id}")
    async def client_websocket(websocket: WebSocket, client_id: str):
        """WebSocket endpoint for clients"""
        await connection_manager.connect_client(websocket, client_id)
        
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
                
                try:
                    message_data = json.loads(message_text)
                    logger.debug(f"Received message from client {client_id}: {message_data}")
                    # Check for GET_STATS right here
                    if message_data.get("type") == "GET_STATS":
                        print("\n\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        print("@@@ GET_STATS FOUND IN CLIENT WEBSOCKET HANDLER @@@")
                        print(f"@@@ CLIENT ID: {client_id} @@@")
                        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\n")
                    await connection_manager.handle_client_message(client_id, message_data, client_message_handlers)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from client {client_id}: {message_text}")
                    error = ErrorMessage(error="Invalid JSON message")
                    await connection_manager.send_to_client(client_id, error)
                except Exception as e:
                    logger.error(f"Error processing client message: {str(e)}")
                    error = ErrorMessage(error=f"Error processing message: {str(e)}")
                    await connection_manager.send_to_client(client_id, error)
        except WebSocketDisconnect:
            connection_manager.disconnect_client(client_id)
        except Exception as e:
            logger.error(f"Error in client websocket: {str(e)}")
            connection_manager.disconnect_client(client_id)
    
    @app.websocket("/ws/worker/{machine_id}/{gpu_id}")
    async def worker_websocket(websocket: WebSocket, machine_id: str, gpu_id: int):
        """WebSocket endpoint for workers"""
        worker_id = f"{machine_id}:{gpu_id}"
        await connection_manager.connect_worker(websocket, worker_id)
        
        # Register worker with Redis
        redis_service.register_worker(machine_id, gpu_id)
        
        # Send confirmation message
        registration_msg = WorkerRegisteredMessage(worker_id=worker_id)
        await connection_manager.send_to_worker(worker_id, registration_msg)
        
        try:
            while True:
                # Receive message from worker
                message_text = await websocket.receive_text()
                try:
                    message_data = json.loads(message_text)
                    logger.debug(f"Received message from worker {worker_id}: {message_data}")
                    await connection_manager.handle_worker_message(worker_id, message_data, worker_message_handlers)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from worker {worker_id}: {message_text}")
                    error = ErrorMessage(error="Invalid JSON message")
                    await connection_manager.send_to_worker(worker_id, error)
                except Exception as e:
                    logger.error(f"Error processing worker message: {str(e)}")
                    error = ErrorMessage(error=f"Error processing message: {str(e)}")
                    await connection_manager.send_to_worker(worker_id, error)
        except WebSocketDisconnect:
            connection_manager.disconnect_worker(worker_id)
        except Exception as e:
            logger.error(f"Error in worker websocket: {str(e)}")
            connection_manager.disconnect_worker(worker_id)

    # Define client message handlers
    async def handle_submit_job(client_id: str, message_data: Dict[str, Any]):
        """Handle job submission from client"""
        try:
            # Log the incoming submission request
            logger.debug(f"Processing job submission from client {client_id}: {message_data}")
            
            # Parse the message
            message = SubmitJobMessage(**message_data)
            
            # Generate job ID if not provided
            job_id = f"job-{uuid.uuid4()}"
            logger.debug(f"Generated job ID: {job_id}")
            
            # Add job to Redis
            try:
                job_data = redis_service.add_job(
                    job_id=job_id,
                    job_type=message.job_type,
                    priority=message.priority,
                    params=message.payload,
                    client_id=client_id
                )
                logger.debug(f"Job added to Redis: {job_data}")
            except Exception as redis_error:
                logger.error(f"Redis error adding job {job_id}: {str(redis_error)}")
                raise Exception(f"Error adding job to queue: {str(redis_error)}")
            
            # Subscribe client to job updates
            try:
                connection_manager.subscribe_to_job(job_id, client_id)
                logger.debug(f"Client {client_id} subscribed to job {job_id}")
            except Exception as sub_error:
                logger.error(f"Error subscribing to job {job_id}: {str(sub_error)}")
                # Continue anyway, as this is non-critical
            
            # Send confirmation to client
            try:
                position = job_data.get("position", 0)
                response = JobAcceptedMessage(
                    job_id=job_id,
                    position=position,
                    estimated_start="30s" if position > 0 else "immediate"
                )
                await connection_manager.send_to_client(client_id, response)
                logger.debug(f"Job acceptance message sent to client {client_id}")
            except Exception as send_error:
                logger.error(f"Error sending job acceptance for {job_id}: {str(send_error)}")
                # Try to send a simple error message instead
                try:
                    error = ErrorMessage(error="Job accepted but error sending confirmation")
                    await connection_manager.send_to_client(client_id, error)
                except:
                    logger.error("Failed to send even the error message")
            
            logger.info(f"Job {job_id} added for client {client_id}")
        except Exception as e:
            logger.error(f"Error submitting job: {str(e)}")
            try:
                error = ErrorMessage(error=f"Error submitting job: {str(e)}")
                await connection_manager.send_to_client(client_id, error)
            except Exception as msg_error:
                logger.error(f"Failed to send error message: {str(msg_error)}")
                # Don't raise further exceptions to prevent WebSocket disconnection
    
    async def handle_get_job_status(client_id: str, message_data: Dict[str, Any]):
        """Handle job status request from client"""
        message = GetJobStatusMessage(**message_data)
        job_id = message.job_id
        
        # Get job status from Redis
        job_data = redis_service.get_job(job_id)
        
        if not job_data:
            # Job not found
            error = ErrorMessage(error=f"Job {job_id} not found")
            await connection_manager.send_to_client(client_id, error)
            return
        
        # Subscribe client to job updates
        connection_manager.subscribe_to_job(job_id, client_id)
        
        # Send status to client
        status = job_data.get("status", "unknown")
        progress = int(job_data.get("progress", 0)) if "progress" in job_data else None
        worker_id = job_data.get("worker")
        started_at = float(job_data.get("started_at", 0)) if "started_at" in job_data else None
        completed_at = float(job_data.get("completed_at", 0)) if "completed_at" in job_data else None
        
        # Parse result if available
        result = None
        if "result" in job_data and job_data["result"]:
            result = job_data["result"]
        
        response = JobStatusMessage(
            job_id=job_id,
            status=status,
            progress=progress,
            worker_id=worker_id,
            started_at=started_at,
            completed_at=completed_at,
            result=result
        )
        await connection_manager.send_to_client(client_id, response)
    
    async def handle_get_stats(client_id: str, message_data: Dict[str, Any]):
        """Handle stats request from client"""
        start_time = time.time()
        # Clear debug separator to make these logs stand out
        logger.critical("\n\n################################################")
        logger.critical("LOOK AT ME MOM I'M A LOG")
        logger.critical("################################################\n")
        logger.critical("\n\n==== GET_STATS REQUEST PROCESSING START ====\n")
        logger.critical(f"Processing get_stats request from client {client_id}")
        
        try:
            # Get stats from Redis
            logger.debug(f"Fetching stats from Redis for client {client_id}")
            stats = redis_service.get_stats()
            fetch_time = time.time() - start_time
            logger.debug(f"Stats fetched in {fetch_time:.4f}s from Redis")
            
            # Raw data dump for debugging
            logger.debug("\n=== RAW REDIS STATS DATA ===")
            logger.debug(f"FULL STATS: {stats}")
            
            # Raw type information for every field - this will show exactly what's happening
            print("\n=== DETAILED TYPE INFO FOR STATS DATA ===")
            print(f"Type of stats: {type(stats).__name__}")
            
            # Queues section
            print("\nQUEUES DATA:")
            print(f"Type of stats['queues']: {type(stats['queues']).__name__}")
            for key, value in stats['queues'].items():
                print(f"  - queues['{key}']: {value} (type: {type(value).__name__})")
                
            # Jobs section
            print("\nJOBS DATA:")
            print(f"Type of stats['jobs']: {type(stats['jobs']).__name__}")
            print(f"  - jobs['total']: {stats['jobs']['total']} (type: {type(stats['jobs']['total']).__name__})")
            
            # Jobs status section
            print("\nJOBS STATUS DATA:")
            print(f"Type of stats['jobs']['status']: {type(stats['jobs']['status']).__name__}")
            for key, value in stats['jobs']['status'].items():
                print(f"  - jobs['status']['{key}']: {value} (type: {type(value).__name__})")
                
            # Workers section
            print("\nWORKERS DATA:")
            print(f"Type of stats['workers']: {type(stats['workers']).__name__}")
            print(f"  - workers['total']: {stats['workers']['total']} (type: {type(stats['workers']['total']).__name__})")
            
            # Workers status section - THE PROBLEM AREA
            print("\nWORKERS STATUS DATA - VALIDATION ERROR AREA:")
            print(f"Type of stats['workers']['status']: {type(stats['workers']['status']).__name__}")
            print(f"Workers status value: {stats['workers']['status']}")
            for key, value in stats['workers']['status'].items():
                print(f"  - workers['status']['{key}']: {value} (type: {type(value).__name__})")
            
            # Detailed logging of worker and job status for troubleshooting
            if 'status' in stats['jobs']:
                job_status = stats['jobs']['status']
                logger.debug(f"Job status breakdown: {job_status}")
                for status, count in job_status.items():
                    logger.debug(f"Job status '{status}' has value of type {type(count).__name__}: {count}")
                    
            if 'status' in stats['workers']:
                worker_status = stats['workers']['status']
                logger.debug(f"Worker status breakdown: {worker_status}")
                for status, count in worker_status.items():
                    logger.debug(f"Worker status '{status}' has value of type {type(count).__name__}: {count}")
            
            # Debug the StatsResponseMessage model
            print("\n=== MODEL VALIDATION ATTEMPT ===")
            print("StatsResponseMessage expects:")
            print("  - 'queues' to be QueueStats model")
            print("  - 'jobs' to be JobStats model")
            print("  - 'workers' to be WorkerStats model")
            print("  - 'workers.status' to be WorkerStatusCounts model")
            
            # Let's try to debug what's happening when we create WorkerStats directly
            print("\n=== DEBUG VALIDATION ATTEMPT - WorkerStats only ===")
            try:
                from queue_api.models import WorkerStats, WorkerStatusCounts
                
                # Extract just the workers section
                workers_data = stats['workers']
                print(f"Workers data: {workers_data}")
                
                # Try to create a WorkerStats model directly
                print("Attempting WorkerStats validation...")
                workers_model = WorkerStats(**workers_data)
                print(f"Success! Created WorkerStats model: {workers_model}")
            except Exception as work_err:
                print(f"FAILED to create WorkerStats: {str(work_err)}")
            
            # Then try to debug the workers.status field specifically
            print("\n=== DEBUG VALIDATION ATTEMPT - WorkerStatusCounts only ===")
            try:
                # Extract just the workers.status section
                worker_status_data = stats['workers']['status']
                print(f"Worker status data: {worker_status_data}")
                
                # Try to create a WorkerStatusCounts model directly
                print("Attempting WorkerStatusCounts validation...")
                status_model = WorkerStatusCounts(**worker_status_data)
                print(f"Success! Created WorkerStatusCounts model: {status_model}")
            except Exception as status_err:
                print(f"FAILED to create WorkerStatusCounts: {str(status_err)}")

            # Manual conversion
            print("\n=== ATTEMPTING DATA SANITIZATION ===")
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
            print(f"Sanitized stats: {sanitized_stats}")
            
            # Try creating the stats response with sanitized data
            print("\n=== VALIDATION WITH SANITIZED DATA ===")
            try:
                print("Attempting to create StatsResponseMessage with sanitized data...")
                response = StatsResponseMessage(**sanitized_stats)
                print("SUCCESS: StatsResponseMessage created with sanitized data!")
            except Exception as validation_err:
                print(f"VALIDATION ERROR with sanitized data: {str(validation_err)}")
                print(f"Validation error type: {type(validation_err).__name__}")
                print("\n=== FALL BACK TO ORIGINAL DATA ===")
                print("Attempting to create StatsResponseMessage with original data...")
                response = StatsResponseMessage(**stats)
            
            # Convert the response to JSON for logging validation
            try:
                response_json = response.json()
                logger.debug(f"Validated response JSON structure: {response_json[:200]}...") 
            except Exception as json_err:
                logger.error(f"Failed to serialize response to JSON: {str(json_err)}")
                logger.error(traceback.format_exc())
            
            # Send response to client
            print("\n=== ATTEMPTING TO SEND RESPONSE ===")
            print(f"Sending stats response to client {client_id}")
            success = await connection_manager.send_to_client(client_id, response)
            
            if success:
                total_time = time.time() - start_time
                print(f"SUCCESS: Stats response sent to client {client_id} in {total_time:.4f}s")
            else:
                print(f"FAILED: Could not send stats response to client {client_id}")
                
            print("\n==== GET_STATS REQUEST PROCESSING END ====\n")
        except Exception as e:
            print("\n=== ERROR PROCESSING GET_STATS ===\n")
            print(f"ERROR handling stats request from client {client_id}: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            print(f"Full traceback:\n{traceback.format_exc()}")
            print("\n==== GET_STATS ERROR END ====\n")
            error = ErrorMessage(error=f"Error retrieving stats: {str(e)}")
            await connection_manager.send_to_client(client_id, error)
    
    # Define worker message handlers
    async def handle_get_next_job(worker_id: str, message_data: Dict[str, Any]):
        """Handle next job request from worker"""
        start_time = time.time()
        logger.debug(f"Worker {worker_id} requesting next job")
        
        try:
            # Get next job from Redis
            job_data = redis_service.get_next_job(worker_id)
            
            if not job_data:
                logger.debug(f"No jobs available for worker {worker_id}")
                # No jobs available
                await asyncio.sleep(1)  # Wait before responding
                return
            
            # Extract job details
            job_id = job_data["id"]
            job_type = job_data["type"]
            priority = int(job_data.get("priority", 0))
            params = job_data["params"]
            
            # Log detailed job assignment information
            logger.info(f"Assigning job {job_id} (type: {job_type}, priority: {priority}) to worker {worker_id}")
            logger.debug(f"Job parameters summary for {job_id}: {str(params)[:200]}{'...' if len(str(params)) > 200 else ''}")
            
            # Create job assigned message
            response = JobAssignedMessage(
                job_id=job_id,
                job_type=job_type,
                priority=priority,
                params=params
            )
            
            # Send job to worker
            logger.debug(f"Sending job assignment message for job {job_id} to worker {worker_id}")
            send_success = await connection_manager.send_to_worker(worker_id, response)
            
            if send_success:
                logger.debug(f"Job assignment message sent successfully to worker {worker_id}")
                
                # Also send update to client if subscribed
                if job_id in connection_manager.job_subscriptions:
                    client_id = connection_manager.job_subscriptions[job_id]
                    update = JobUpdateMessage(
                        job_id=job_id,
                        status="processing",
                        progress=0,
                        worker_id=worker_id
                    )
                    logger.debug(f"Sending initial job status update to client {client_id}")
                    await connection_manager.send_job_update(job_id, update)
            else:
                logger.warning(f"Failed to send job assignment to worker {worker_id} for job {job_id}")
                
            total_time = time.time() - start_time
            logger.debug(f"Job assignment processed in {total_time:.4f}s")
        except Exception as e:
            logger.error(f"Error in handle_get_next_job for worker {worker_id}: {str(e)}")
            logger.error(traceback.format_exc())
            error = ErrorMessage(error=f"Error getting next job: {str(e)}")
            await connection_manager.send_to_worker(worker_id, error)
    
    async def handle_update_job_progress(worker_id: str, message_data: Dict[str, Any]):
        """Handle job progress update from worker"""
        start_time = time.time()
        
        try:
            # Clear debug separator to make these logs stand out
            print("\n\n===================================================")
            print(f"==== WORKER {worker_id} JOB PROGRESS UPDATE ====")
            print("===================================================\n")
            
            # Parse the progress update message
            message = UpdateJobProgressMessage(**message_data)
            job_id = message.job_id
            progress = message.progress
            msg_content = message.message
            
            logger.info(f"💡 PROCESSING: Worker {worker_id} reported progress on job {job_id}: {progress}%")
            logger.info(f"Raw message from worker: {json.dumps(message_data)}")
            
            if msg_content:
                logger.info(f"Progress message: '{msg_content}'")
            
            # Update job progress in Redis
            logger.info(f"Updating job {job_id} progress in Redis to {progress}%")
            success = redis_service.update_job_progress(
                job_id=job_id,
                progress=progress,
                worker_id=worker_id,
                message=msg_content
            )
            
            if not success:
                # Job not found in Redis
                logger.warning(f"Job {job_id} not found in Redis during progress update")
                error = ErrorMessage(error=f"Job {job_id} not found")
                await connection_manager.send_to_worker(worker_id, error)
                return
            
            # Log current stats after update
            stats = redis_service.get_stats()
            logger.info(f"Current stats after progress update: {json.dumps(stats)}")
            
            # Create job update message for client
            update = JobUpdateMessage(
                job_id=job_id,
                status="processing",
                progress=progress,
                eta="15s" if progress < 90 else "5s",
                message=msg_content
            )
            
            # Send update to subscribed client
            if job_id in connection_manager.job_subscriptions:
                client_id = connection_manager.job_subscriptions[job_id]
                logger.info(f"Sending progress update for job {job_id} to client {client_id}: {progress}%")
                send_success = await connection_manager.send_job_update(job_id, update)
                
                if not send_success:
                    logger.warning(f"Failed to send progress update for job {job_id} to client {client_id}")
            else:
                logger.info(f"No client subscribed for updates on job {job_id}")
                
            total_time = time.time() - start_time
            logger.info(f"Progress update for job {job_id} processed in {total_time:.4f}s")
            print("\n==== END OF WORKER PROGRESS UPDATE ====\n")
        except Exception as e:
            logger.error(f"Error handling progress update from worker {worker_id}: {str(e)}")
            logger.error(traceback.format_exc())
            # Don't propagate exception to avoid worker disconnect
    
    async def handle_complete_job(worker_id: str, message_data: Dict[str, Any]):
        """Handle job completion from worker"""
        start_time = time.time()
        
        try:
            # Clear debug separator to make these logs stand out
            print("\n\n****************************************************")
            print(f"********** WORKER {worker_id} JOB COMPLETION **********")
            print("****************************************************\n")
            
            # Log raw message data
            print(f"RAW JOB COMPLETION MESSAGE: {json.dumps(message_data)}")
            
            # Parse completion message
            message = CompleteJobMessage(**message_data)
            job_id = message.job_id
            result = message.result
            
            logger.info(f"\ud83c\udf89 COMPLETE: Worker {worker_id} completed job {job_id}")
            
            # Log result summary (without excessive detail)
            if result and isinstance(result, dict):
                # Extract important metrics without logging the entire result
                metrics = result.get('metrics', {})
                errors = result.get('errors', [])
                logger.info(f"Job {job_id} result summary - metrics: {metrics}, errors: {errors if errors else 'none'}")
            
            # Get stats before update
            before_stats = redis_service.get_stats()
            logger.info(f"Stats BEFORE job completion:\n{json.dumps(before_stats, indent=2)}")
            
            # Mark job as completed in Redis
            logger.info(f"Marking job {job_id} as completed in Redis")
            success = redis_service.complete_job(
                job_id=job_id,
                worker_id=worker_id,
                result=result
            )
            
            if not success:
                # Job not found in Redis
                logger.warning(f"Job {job_id} not found in Redis during completion")
                error = ErrorMessage(error=f"Job {job_id} not found")
                await connection_manager.send_to_worker(worker_id, error)
                return
            
            # Get stats after update
            after_stats = redis_service.get_stats()
            logger.info(f"Stats AFTER job completion:\n{json.dumps(after_stats, indent=2)}")
            
            # Highlight stats changes
            completed_before = before_stats['jobs']['status'].get('completed', 0)
            completed_after = after_stats['jobs']['status'].get('completed', 0)
            processing_before = before_stats['jobs']['status'].get('processing', 0)
            processing_after = after_stats['jobs']['status'].get('processing', 0)
            
            logger.info(f"STATS CHANGES - Completed jobs: {completed_before} → {completed_after}")
            logger.info(f"STATS CHANGES - Processing jobs: {processing_before} → {processing_after}")
            
            logger.info(f"Successfully marked job {job_id} as completed in Redis")
            
            # Create completion message
            completion = JobCompletedMessage(
                job_id=job_id,
                result=result
            )
            
            # Send completion to subscribed client
            if job_id in connection_manager.job_subscriptions:
                client_id = connection_manager.job_subscriptions[job_id]
                logger.info(f"Sending completion notification for job {job_id} to client {client_id}")
                await connection_manager.send_job_update(job_id, completion)
            else:
                logger.info(f"No client subscribed for updates on job {job_id}")
            
            total_time = time.time() - start_time
            logger.info(f"Job completion for job {job_id} processed in {total_time:.4f}s")
            print("\n******** END OF JOB COMPLETION HANDLING ********\n")
        except Exception as e:
            logger.error(f"Error handling job completion from worker {worker_id}: {str(e)}")
            logger.error(traceback.format_exc())
            # Don't propagate exception to avoid worker disconnect
    
    async def handle_subscribe_stats(client_id: str, message_data: Dict[str, Any]):
        """Handle stats subscription request from client"""
        start_time = time.time()
        logger.info(f"Client {client_id} subscribing to system stats updates")
        
        try:
            # Parse subscription message
            message = SubscribeStatsMessage(**message_data)
            
            # Subscribe client to stats updates
            connection_manager.subscribe_to_stats(client_id)
            
            # Get current stats and send them immediately
            stats = redis_service.get_stats()
            
            # Sanitize stats data (convert string values to integers)
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
            
            # Create stats response
            response = StatsResponseMessage(**sanitized_stats)
            
            # Send stats to client
            await connection_manager.send_to_client(client_id, response)
            
            total_time = time.time() - start_time
            logger.info(f"Client {client_id} subscribed to stats updates in {total_time:.4f}s")
        except Exception as e:
            logger.error(f"Error handling stats subscription from client {client_id}: {str(e)}")
            logger.error(traceback.format_exc())
            error = ErrorMessage(error=f"Error subscribing to stats: {str(e)}")
            await connection_manager.send_to_client(client_id, error)
    
    async def handle_subscribe_job(client_id: str, message_data: Dict[str, Any]):
        """Handle job subscription request from client"""
        try:
            print(f"\n\n🔔🔔🔔 CLIENT {client_id} SUBSCRIBING TO JOB UPDATES 🔔🔔🔔")
            print(f"Message data: {json.dumps(message_data)[:200]}")
            
            # Parse the subscription message
            message = SubscribeJobMessage(**message_data)
            job_id = message.job_id
            
            # Log with high visibility for debugging
            print(f"🔔 Job subscription request received from client {client_id} for job {job_id}")
            logger.info(f"Client {client_id} subscribing to job {job_id} updates")
            
            # Subscribe the client to the job
            connection_manager.subscribe_to_job(job_id, client_id)
            
            # Get current job status from Redis
            job_status = redis_service.get_job(job_id)
            if job_status:
                # Create job status response
                status_message = JobStatusMessage(
                    job_id=job_id,
                    status=job_status.get("status", "unknown"),
                    progress=job_status.get("progress"),
                    worker_id=job_status.get("worker_id"),
                    started_at=job_status.get("started_at"),
                    completed_at=job_status.get("completed_at"),
                    result=job_status.get("result"),
                    message=f"Job status as of subscription time"
                )
                
                # Send current job status to the client
                print(f"🔄 Sending current job status for job {job_id} to client {client_id}")
                await connection_manager.send_to_client(client_id, status_message)
            else:
                print(f"⚠️ Job {job_id} not found in Redis, but client {client_id} subscribed anyway")
                # Still subscribe but send a message that the job wasn't found
                error = ErrorMessage(
                    error=f"Job {job_id} not found, but subscription was registered",
                    details={"job_id": job_id, "subscription": "registered"}
                )
                await connection_manager.send_to_client(client_id, error)
            
            print(f"✅ Successfully subscribed client {client_id} to job {job_id}")
        except Exception as e:
            logger.error(f"Error handling job subscription from client {client_id}: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"❌ ERROR subscribing client {client_id} to job updates: {str(e)}")
            error = ErrorMessage(error=f"Error subscribing to job: {str(e)}")
            await connection_manager.send_to_client(client_id, error)
    
    # Register client message handlers
    client_message_handlers[MessageType.SUBMIT_JOB] = handle_submit_job
    client_message_handlers[MessageType.GET_JOB_STATUS] = handle_get_job_status
    client_message_handlers[MessageType.GET_STATS] = handle_get_stats
    client_message_handlers[MessageType.SUBSCRIBE_STATS] = handle_subscribe_stats
    client_message_handlers[MessageType.SUBSCRIBE_JOB] = handle_subscribe_job
    
    # Register worker message handlers
    worker_message_handlers[MessageType.GET_NEXT_JOB] = handle_get_next_job
    worker_message_handlers[MessageType.UPDATE_JOB_PROGRESS] = handle_update_job_progress
    worker_message_handlers[MessageType.COMPLETE_JOB] = handle_complete_job
    
    logger.info("WebSocket routes initialized")
    
    # Start the stats broadcast task
    asyncio.create_task(broadcast_stats_task())
    logger.info("Stats broadcast task started")

# Redis Pub/Sub listener for job updates
async def start_redis_listener():
    """Start listening for Redis pub/sub messages"""
    async def handle_redis_message(message):
        """Handle Redis pub/sub message"""
        if message["type"] != "pmessage" and message["type"] != "message":
            return
        
        try:
            channel = message["channel"]
            data = json.loads(message["data"])
            
            # Handle job-specific updates
            if channel.startswith("job:") and channel.endswith(":updates"):
                job_id = channel.split(":")[1]
                
                # Create job update message
                status = data.get("status", "processing")
                progress = data.get("progress")
                result = data.get("result")
                
                if status == "completed":
                    update = JobCompletedMessage(
                        job_id=job_id,
                        result=result
                    )
                else:
                    update = JobUpdateMessage(
                        job_id=job_id,
                        status=status,
                        progress=progress,
                        eta="30s" if progress and progress < 50 else "15s",
                        message=data.get("message")
                    )
                
                # Send update to subscribed client
                await connection_manager.send_job_update(job_id, update)
        except Exception as e:
            logger.error(f"Error handling Redis message: {str(e)}")
    
    # Subscribe to job update channels
    await redis_service.subscribe("job:*:updates", handle_redis_message)
    
    # Start the listener
    asyncio.create_task(redis_service.listen())
    logger.info("Redis pub/sub listener started")
