#!/usr/bin/env python3
# Redis service for the queue system
import os
import json
import time
import logging
import asyncio
import redis
import redis.asyncio as aioredis
from typing import Dict, Any, Optional, List, Union, Callable

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# Queue names
STANDARD_QUEUE = "job_queue"
PRIORITY_QUEUE = "priority_queue"

# Redis key prefixes
JOB_PREFIX = "job:"
WORKER_PREFIX = "worker:"

class RedisService:
    """Service for interacting with Redis for job queue operations"""
    
    def __init__(self):
        """Initialize Redis connections"""
        # Synchronous client for most operations
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
        
        # Asynchronous client for pub/sub
        self.async_client = None
        self.pubsub = None
        
        logger.info(f"Redis service initialized with host {REDIS_HOST}:{REDIS_PORT}")
    
    async def connect_async(self):
        """Connect to Redis asynchronously for pub/sub"""
        if self.async_client is None:
            self.async_client = aioredis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
            )
            self.pubsub = self.async_client.pubsub()
            logger.info("Async Redis connection established")
    
    async def close_async(self):
        """Close the async Redis connection"""
        if self.pubsub:
            await self.pubsub.close()
        if self.async_client:
            await self.async_client.close()
        logger.info("Async Redis connection closed")
    
    # Job operations
    def add_job(self, job_id: str, job_type: str, priority: int, params: Dict[str, Any], client_id: Optional[str] = None) -> Dict[str, Any]:
        """Add a job to the queue"""
        job_key = f"{JOB_PREFIX}{job_id}"
        
        # Store job details
        job_data = {
            "id": job_id,
            "type": job_type,
            "priority": priority,
            "params": json.dumps(params),
            "status": "pending",
            "created_at": time.time(),
        }
        
        if client_id:
            job_data["client_id"] = client_id
        
        self.client.hset(job_key, mapping=job_data)
        
        # Add to appropriate queue based on priority
        if priority > 0:
            self.client.zadd(PRIORITY_QUEUE, {job_id: priority})
        else:
            self.client.lpush(STANDARD_QUEUE, job_id)
        
        # Get queue position
        if priority > 0:
            position = self.client.zrank(PRIORITY_QUEUE, job_id)
        else:
            position = self.client.llen(STANDARD_QUEUE) - self.client.lpos(STANDARD_QUEUE, job_id)
        
        logger.info(f"Added job {job_id} to queue with priority {priority}, position {position}")
        
        # Return job data with position
        job_data["position"] = position if position is not None else -1
        return job_data
    
    def get_next_job(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get the next job for processing"""
        # First check priority queue
        priority_job_id = self.client.zrevrange(PRIORITY_QUEUE, 0, 0)
        if priority_job_id:
            job_id = priority_job_id[0]
            self.client.zrem(PRIORITY_QUEUE, job_id)
        else:
            # Then check standard queue
            job_id = self.client.rpop(STANDARD_QUEUE)
        
        if not job_id:
            # No jobs available
            return None
        
        # Get job details
        job_key = f"{JOB_PREFIX}{job_id}"
        job_data = self.client.hgetall(job_key)
        
        if not job_data:
            logger.error(f"Job {job_id} not found in Redis")
            return None
        
        # Update job status
        self.client.hset(job_key, "status", "processing")
        self.client.hset(job_key, "started_at", time.time())
        self.client.hset(job_key, "worker", worker_id)
        
        # Parse params back to dict
        if "params" in job_data:
            job_data["params"] = json.loads(job_data["params"])
        
        logger.info(f"Assigned job {job_id} to worker {worker_id}")
        
        # Publish job assignment event
        self.publish_job_update(job_id, "processing", worker_id=worker_id)
        
        return job_data
    
    def update_job_progress(self, job_id: str, progress: int, worker_id: str, message: Optional[str] = None) -> bool:
        """Update job progress"""
        job_key = f"{JOB_PREFIX}{job_id}"
        
        # Check if job exists
        if not self.client.exists(job_key):
            logger.error(f"Job {job_id} not found in Redis")
            return False
        
        # Update job progress
        self.client.hset(job_key, "progress", progress)
        if message:
            self.client.hset(job_key, "message", message)
        
        logger.debug(f"Updated job {job_id} progress to {progress}%")
        
        # Publish progress update event
        self.publish_job_update(job_id, "processing", progress=progress, message=message, worker_id=worker_id)
        
        return True
    
    def complete_job(self, job_id: str, worker_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """Mark a job as completed"""
        job_key = f"{JOB_PREFIX}{job_id}"
        
        # Check if job exists
        if not self.client.exists(job_key):
            logger.error(f"Job {job_id} not found in Redis")
            return False
        
        # Update job status
        completed_at = time.time()
        self.client.hset(job_key, "status", "completed")
        self.client.hset(job_key, "completed_at", completed_at)
        
        # Add result if provided
        if result:
            self.client.hset(job_key, "result", json.dumps(result))
        
        logger.info(f"Worker {worker_id} completed job {job_id}")
        
        # Publish completion event
        self.publish_job_update(job_id, "completed", result=result, worker_id=worker_id)
        
        return True
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job details"""
        job_key = f"{JOB_PREFIX}{job_id}"
        job_data = self.client.hgetall(job_key)
        
        if not job_data:
            return None
        
        # Parse JSON fields
        if "params" in job_data:
            job_data["params"] = json.loads(job_data["params"])
        
        if "result" in job_data:
            job_data["result"] = json.loads(job_data["result"])
        
        return job_data
    
    # Worker operations
    def register_worker(self, machine_id: str, gpu_id: int) -> str:
        """Register a worker"""
        worker_id = f"{machine_id}:{gpu_id}"
        worker_key = f"{WORKER_PREFIX}{worker_id}"
        
        # Store worker details
        self.client.hset(
            worker_key,
            mapping={
                "machine_id": machine_id,
                "gpu_id": str(gpu_id),
                "status": "active",
                "start_time": time.time(),
                "last_heartbeat": time.time(),
            }
        )
        
        logger.info(f"Registered worker {worker_id}")
        return worker_id
    
    def update_worker_heartbeat(self, worker_id: str) -> bool:
        """Update worker heartbeat"""
        worker_key = f"{WORKER_PREFIX}{worker_id}"
        
        if not self.client.exists(worker_key):
            logger.warning(f"Worker {worker_id} not found in Redis")
            return False
        
        self.client.hset(worker_key, "last_heartbeat", time.time())
        return True
    
    # Pub/Sub operations
    def publish_job_update(self, job_id: str, status: str, progress: Optional[int] = None, 
                           message: Optional[str] = None, result: Optional[Dict[str, Any]] = None,
                           worker_id: Optional[str] = None) -> int:
        """Publish a job update event"""
        # Create update payload
        update_data = {
            "job_id": job_id,
            "status": status,
            "timestamp": time.time()
        }
        
        if progress is not None:
            update_data["progress"] = progress
            
        if message:
            update_data["message"] = message
            
        if result:
            update_data["result"] = result
            
        if worker_id:
            update_data["worker_id"] = worker_id
        
        # Get client_id for client-specific channel
        job_key = f"{JOB_PREFIX}{job_id}"
        client_id = self.client.hget(job_key, "client_id")
        
        # Publish to job-specific channel
        job_channel = f"job:{job_id}:updates"
        count = self.client.publish(job_channel, json.dumps(update_data))
        
        # Also publish to client-specific channel if available
        if client_id:
            client_channel = f"client:{client_id}:updates"
            self.client.publish(client_channel, json.dumps(update_data))
        
        logger.debug(f"Published update for job {job_id} to {count} subscribers")
        return count
    
    async def subscribe(self, channel_pattern: str, callback: Callable) -> None:
        """Subscribe to a Redis channel pattern"""
        await self.connect_async()
        await self.pubsub.psubscribe(**{channel_pattern: callback})
        logger.info(f"Subscribed to channel pattern: {channel_pattern}")
    
    async def listen(self) -> None:
        """Listen for pub/sub messages"""
        if not self.pubsub:
            await self.connect_async()
        
        async for message in self.pubsub.listen():
            # Process in background to not block the listener
            if message["type"] == "pmessage" or message["type"] == "message":
                logger.debug(f"Received Redis pubsub message: {message}")
    
    # Stats operations
    # Store previous stats for comparison
    _previous_stats = None
    
    def cleanup_stale_jobs(self, max_heartbeat_age: int = 300) -> int:
        """Check for jobs in processing state with stale worker heartbeats and mark them as failed
        
        Args:
            max_heartbeat_age: Maximum allowed time (in seconds) since last heartbeat before worker is considered stale
            
        Returns:
            Number of jobs that were cleaned up
        """
        logger.info(f"📢 Checking for stale jobs with worker heartbeat threshold of {max_heartbeat_age} seconds...")
        current_time = time.time()
        cleaned_count = 0
        
        # Get all jobs in processing state
        all_jobs = self.client.keys(f"{JOB_PREFIX}*")
        
        for job_key in all_jobs:
            # Get job data
            job_data = self.client.hgetall(job_key)
            
            # Skip if not in processing state
            if job_data.get("status") != "processing":
                continue
                
            # Check if job has a worker assigned
            worker_id = job_data.get("worker")
            if not worker_id:
                logger.warning(f"⚠️ Job {job_key} is in processing state but has no worker assigned")
                continue
                
            # Get worker data
            worker_key = f"{WORKER_PREFIX}{worker_id}"
            worker_data = self.client.hgetall(worker_key)
            
            # If worker doesn't exist or last heartbeat is too old
            if not worker_data or current_time - float(worker_data.get("last_heartbeat", 0)) > max_heartbeat_age:
                job_id = job_data.get("id")
                logger.warning(f"🚨 Detected stale job {job_id} with inactive worker {worker_id}")
                
                # Mark job as failed
                error_message = f"Worker {worker_id} lost connection while processing job"
                self.client.hset(job_key, "status", "failed")
                self.client.hset(job_key, "completed_at", current_time)
                
                # Add failure reason
                failure_info = {
                    "error": error_message,
                    "details": {
                        "cause": "worker_heartbeat_timeout",
                        "max_heartbeat_age": max_heartbeat_age,
                        "cleanup_time": current_time
                    }
                }
                self.client.hset(job_key, "result", json.dumps(failure_info))
                
                # Publish update event
                self.publish_job_update(
                    job_id=job_id,
                    status="failed",
                    message=error_message,
                    result=failure_info
                )
                
                cleaned_count += 1
                logger.info(f"✅ Marked stale job {job_id} as failed due to worker heartbeat timeout")
        
        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} stale jobs")
        else:
            logger.debug("No stale jobs found")
            
        return cleaned_count
        
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        logger.debug("Fetching system stats from Redis...")
        
        # Get queue lengths
        priority_queue_length = self.client.zcard(PRIORITY_QUEUE)
        standard_queue_length = self.client.llen(STANDARD_QUEUE)
        logger.debug(f"Queue lengths - Priority: {priority_queue_length}, Standard: {standard_queue_length}")
        
        # Get job counts by status
        all_jobs = self.client.keys(f"{JOB_PREFIX}*")
        total_jobs = len(all_jobs)
        logger.debug(f"Found {total_jobs} jobs in Redis")
        
        status_counts = {
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0
        }
        
        # Log each job key and status
        for job_key in all_jobs:
            status = self.client.hget(job_key, "status")
            logger.debug(f"Job {job_key} has status: {status}")
            if status in status_counts:
                status_counts[status] += 1
        
        # Get worker counts
        all_workers = self.client.keys(f"{WORKER_PREFIX}*")
        total_workers = len(all_workers)
        logger.debug(f"Found {total_workers} workers in Redis")
        
        worker_status = {
            "active": 0,
            "idle": 0,
            "disconnected": 0
        }
        
        # Log each worker key and status
        for worker_key in all_workers:
            status = self.client.hget(worker_key, "status")
            logger.debug(f"Worker {worker_key} has status: {status}")
            if status in worker_status:
                worker_status[status] += 1
        
        # Construct the stats dictionary
        current_stats = {
            "queues": {
                "priority": priority_queue_length,
                "standard": standard_queue_length,
                "total": priority_queue_length + standard_queue_length
            },
            "jobs": {
                "total": total_jobs,
                "status": status_counts
            },
            "workers": {
                "total": total_workers,
                "status": worker_status
            }
        }
        
        # Compare with previous stats to detect changes
        if RedisService._previous_stats is not None:
            prev = RedisService._previous_stats
            changes_detected = False
            
            # Check for changes in queues
            if prev["queues"] != current_stats["queues"]:
                logger.info(f"Queue stats changed: {prev['queues']} -> {current_stats['queues']}")
                changes_detected = True
            
            # Check for changes in jobs
            if prev["jobs"] != current_stats["jobs"]:
                logger.info(f"Job stats changed: {prev['jobs']} -> {current_stats['jobs']}")
                changes_detected = True
            
            # Check for changes in workers
            if prev["workers"] != current_stats["workers"]:
                logger.info(f"Worker stats changed: {prev['workers']} -> {current_stats['workers']}")
                changes_detected = True
                
            if not changes_detected:
                logger.info("No changes detected in system stats")
        else:
            logger.info(f"Initial stats gathered: {current_stats}")
        
        # Update previous stats
        RedisService._previous_stats = current_stats
        
        return current_stats
