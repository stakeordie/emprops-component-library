#!/usr/bin/env python3
# Core Redis service for the queue system
import os
import json
import time
import logging
import redis
import redis.asyncio as aioredis
from typing import Dict, Any, Optional, List, Union, Callable

logger = logging.getLogger(__name__)

# Redis configuration
# When running in Docker, "REDIS_HOST" env var should be set to the container name (e.g., "hub")
# For local development, default to "localhost"
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# Log the actual Redis host being used for debugging
logger.info(f"Redis configured to connect to {REDIS_HOST}:{REDIS_PORT}")

# Queue names
STANDARD_QUEUE = "job_queue"
PRIORITY_QUEUE = "priority_queue"

# Redis key prefixes
JOB_PREFIX = "job:"
WORKER_PREFIX = "worker:"

class RedisService:
    """Core service for interacting with Redis for job queue operations"""
    
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
    
    async def init_redis(self):
        """Initialize Redis connections and data structures
        
        This method ensures that both synchronous and asynchronous
        Redis connections are properly established and initializes
        any necessary data structures for the job queue system.
        """
        # Ensure async connection is established
        await self.connect_async()
        
        # Initialize Redis data structures if they don't exist
        # Clear any stale temporary keys
        self.client.delete("temp:workers")
        
        # Create worker set if it doesn't exist
        if not self.client.exists("workers:all"):
            self.client.sadd("workers:all", "placeholder")  # Create the set
            self.client.srem("workers:all", "placeholder")  # Remove placeholder
            
        # Create idle workers set if it doesn't exist
        if not self.client.exists("workers:idle"):
            self.client.sadd("workers:idle", "placeholder")  # Create the set
            self.client.srem("workers:idle", "placeholder")  # Remove placeholder
            
        # Ensure queue structures exist
        if not self.client.exists(STANDARD_QUEUE):
            # Initialize empty list for standard queue
            self.client.rpush(STANDARD_QUEUE, "placeholder")  # Create the list
            self.client.lpop(STANDARD_QUEUE)  # Remove placeholder
            
        # Initialize job statistics counters if they don't exist
        stats_keys = ["stats:jobs:completed", "stats:jobs:failed", "stats:jobs:total"]
        for key in stats_keys:
            if not self.client.exists(key):
                self.client.set(key, 0)
                
        logger.info("Redis data structures initialized successfully")
        return True
    
    async def close(self):
        """Close all Redis connections
        
        This method ensures that both synchronous and asynchronous
        Redis connections are properly closed and resources are released.
        """
        # Close async connections
        await self.close_async()
        
        # Close synchronous connection
        if self.client:
            self.client.close()
            logger.info("Synchronous Redis connection closed")
            
        logger.info("All Redis connections closed successfully")
    
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
        
        # Notify idle workers about the new job
        self.notify_idle_workers_of_job(job_id, job_type, params)
        
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
        
    def fail_job(self, job_id: str, worker_id: str, error: Optional[str] = None) -> bool:
        """Mark a job as failed"""
        job_key = f"{JOB_PREFIX}{job_id}"
        
        # Check if job exists
        if not self.client.exists(job_key):
            logger.error(f"Job {job_id} not found in Redis")
            return False
        
        # Update job status
        self.client.hset(job_key, "status", "failed")
        self.client.hset(job_key, "error", error if error else "Unknown error")
        
        logger.info(f"Worker {worker_id} failed job {job_id}: {error}")
        
        # Publish failure event
        self.publish_job_update(job_id, "failed", error=error, worker_id=worker_id)
        
        return True
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a job"""
        job_key = f"{JOB_PREFIX}{job_id}"
        
        # Check if job exists
        if not self.client.exists(job_key):
            logger.error(f"Job {job_id} not found in Redis")
            return None
        
        # Get job details
        job_data = self.client.hgetall(job_key)
        
        # Parse params and result if present
        if "params" in job_data:
            try:
                job_data["params"] = json.loads(job_data["params"])
            except:
                job_data["params"] = {}
                
        if "result" in job_data:
            try:
                job_data["result"] = json.loads(job_data["result"])
            except:
                job_data["result"] = {}
        
        # Add queue position if job is pending
        if job_data.get("status") == "pending":
            priority = int(job_data.get("priority", 0))
            if priority > 0:
                position = self.client.zrank(PRIORITY_QUEUE, job_id)
            else:
                position = self.client.llen(STANDARD_QUEUE) - self.client.lpos(STANDARD_QUEUE, job_id)
            job_data["position"] = position if position is not None else -1
        
        return job_data
    
    def register_worker(self, worker_id: str, worker_info: Dict[str, Any]) -> bool:
        """Register a worker in Redis"""
        worker_key = f"{WORKER_PREFIX}{worker_id}"
        
        # Add worker info with current timestamp
        worker_info["registered_at"] = time.time()
        worker_info["last_heartbeat"] = time.time()
        worker_info["status"] = "idle"
        
        # Add worker to hash storage
        self.client.hset(worker_key, mapping=worker_info)
        
        # Add worker to tracking sets
        self.client.sadd("workers:all", worker_id)
        
        # Add to idle workers set since all workers start as idle
        self.client.sadd("workers:idle", worker_id)
        
        logger.info(f"Registered worker {worker_id} and added to worker tracking sets")
        
        return True
    
    def update_worker_heartbeat(self, worker_id: str, status: str = None) -> bool:
        """Update worker heartbeat timestamp and optionally status"""
        worker_key = f"{WORKER_PREFIX}{worker_id}"
        
        # Check if worker exists
        if not self.client.exists(worker_key):
            logger.error(f"Worker {worker_id} not found in Redis")
            return False
        
        # Update heartbeat
        update_data = {"last_heartbeat": time.time()}
        
        # Update status if provided
        if status is not None:
            # Get current status for comparison
            current_status = self.client.hget(worker_key, "status")
            update_data["status"] = status
            
            # Update worker tracking sets based on status change
            if status == "idle":
                # Worker is now idle, add to idle workers set
                self.client.sadd("workers:idle", worker_id)
                logger.debug(f"Added {worker_id} to idle workers set")
            elif current_status == "idle" and status != "idle":
                # Worker was idle but now is not, remove from idle workers set
                self.client.srem("workers:idle", worker_id)
                logger.debug(f"Removed {worker_id} from idle workers set")
            
            logger.debug(f"Updated worker {worker_id} status from {current_status} to {status}")
        
        # Update the worker hash
        self.client.hset(worker_key, mapping=update_data)
        return True
        
    def worker_exists(self, worker_id: str) -> bool:
        """Check if a worker exists in Redis"""
        worker_key = f"{WORKER_PREFIX}{worker_id}"
        exists = self.client.exists(worker_key)
        
        if exists:
            # Also check if worker is in the all workers set as a safeguard
            in_all_set = self.client.sismember("workers:all", worker_id)
            if not in_all_set:
                logger.warning(f"Worker {worker_id} exists as hash but not in workers:all set, repairing")
                self.client.sadd("workers:all", worker_id)
            
            return True
        return False
    
    def update_worker_status(self, worker_id: str, status: str) -> bool:
        """Update worker status"""
        worker_key = f"{WORKER_PREFIX}{worker_id}"
        
        # Check if worker exists
        if not self.client.exists(worker_key):
            logger.error(f"Worker {worker_id} not found in Redis")
            return False
        
        # Get current status for comparison
        current_status = self.client.hget(worker_key, "status")
        
        # Update status in the worker hash
        self.client.hset(worker_key, "status", status)
        
        # Update worker tracking sets based on status change
        if status == "idle":
            # Worker is now idle, add to idle workers set
            self.client.sadd("workers:idle", worker_id)
            logger.debug(f"Added {worker_id} to idle workers set")
        elif current_status == "idle" and status != "idle":
            # Worker was idle but now is not, remove from idle workers set
            self.client.srem("workers:idle", worker_id)
            logger.debug(f"Removed {worker_id} from idle workers set")
        
        logger.info(f"Updated worker {worker_id} status from {current_status} to {status}")
        
        return True
    
    def get_worker_info(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a worker"""
        worker_key = f"{WORKER_PREFIX}{worker_id}"
        
        # Check if worker exists
        if not self.client.exists(worker_key):
            logger.error(f"Worker {worker_id} not found in Redis")
            return None
        
        return self.client.hgetall(worker_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        # Initialize stats structure
        stats = {
            "queues": {
                "priority": 0,
                "standard": 0,
                "total": 0
            },
            "jobs": {
                "total": 0,
                "status": {}
            },
            "workers": {
                "total": 0,
                "status": {}
            }
        }
        
        try:
            # Queue stats
            stats["queues"]["priority"] = self.client.zcard(PRIORITY_QUEUE)
            stats["queues"]["standard"] = self.client.llen(STANDARD_QUEUE)
            stats["queues"]["total"] = stats["queues"]["priority"] + stats["queues"]["standard"]
            
            # Job stats
            job_keys = self.client.keys(f"{JOB_PREFIX}*")
            stats["jobs"]["total"] = len(job_keys)
            
            # Job status counts
            for job_key in job_keys:
                job_status = self.client.hget(job_key, "status")
                if job_status:
                    stats["jobs"]["status"][job_status] = stats["jobs"]["status"].get(job_status, 0) + 1
            
            # Worker stats
            worker_keys = self.client.keys(f"{WORKER_PREFIX}*")
            stats["workers"]["total"] = len(worker_keys)
            
            # Worker status counts
            for worker_key in worker_keys:
                worker_status = self.client.hget(worker_key, "status")
                if worker_status:
                    stats["workers"]["status"][worker_status] = stats["workers"]["status"].get(worker_status, 0) + 1
            
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
        
        return stats
    
    def cleanup_stale_jobs(self, max_heartbeat_age: int = 600) -> int:
        """Clean up stale jobs from workers that have disappeared"""
        current_time = time.time()
        stale_count = 0
        
        # Get all worker information
        worker_keys = self.client.keys(f"{WORKER_PREFIX}*")
        
        for worker_key in worker_keys:
            worker_id = worker_key.replace(f"{WORKER_PREFIX}", "")
            worker_data = self.client.hgetall(worker_key)
            
            # Skip if no heartbeat data
            if "last_heartbeat" not in worker_data:
                continue
                
            last_heartbeat = float(worker_data["last_heartbeat"])
            heartbeat_age = current_time - last_heartbeat
            
            # Check if worker is stale
            if heartbeat_age > max_heartbeat_age:
                logger.info(f"Worker {worker_id} is stale (no heartbeat for {heartbeat_age:.1f}s)")
                
                # Find any jobs assigned to this worker
                job_keys = self.client.keys(f"{JOB_PREFIX}*")
                
                for job_key in job_keys:
                    job_id = job_key.replace(f"{JOB_PREFIX}", "")
                    job_worker = self.client.hget(job_key, "worker")
                    job_status = self.client.hget(job_key, "status")
                    
                    # Only reset jobs that are in processing status and assigned to this worker
                    if job_worker == worker_id and job_status == "processing":
                        # Get job priority
                        priority = int(self.client.hget(job_key, "priority") or 0)
                        
                        # Reset job status to pending
                        self.client.hset(job_key, "status", "pending")
                        self.client.hdel(job_key, "worker")
                        self.client.hdel(job_key, "started_at")
                        
                        # Add back to queue
                        if priority > 0:
                            self.client.zadd(PRIORITY_QUEUE, {job_id: priority})
                        else:
                            self.client.lpush(STANDARD_QUEUE, job_id)
                            
                        logger.info(f"Reset stale job {job_id} back to pending status (was assigned to worker {worker_id})")
                        stale_count += 1
                
                # Mark worker as disconnected
                self.client.hset(worker_key, "status", "disconnected")
        
        return stale_count
    
    def mark_stale_workers_out_of_service(self, max_heartbeat_age: int = 120) -> int:
        """Mark workers without recent heartbeats as out_of_service
        
        Args:
            max_heartbeat_age: Maximum age of heartbeat in seconds (default: 120 seconds / 2 minutes)
            
        Returns:
            Number of workers marked as out_of_service
        """
        current_time = time.time()
        stale_count = 0
        worker_keys = self.client.keys(f"{WORKER_PREFIX}*")
        
        for worker_key in worker_keys:
            worker_id = worker_key.replace(f"{WORKER_PREFIX}", "")
            worker_status = self.client.hget(worker_key, "status")
            last_heartbeat = float(self.client.hget(worker_key, "last_heartbeat") or 0)
            heartbeat_age = current_time - last_heartbeat
            
            # Skip workers already marked as out_of_service or disconnected
            if worker_status in ["out_of_service", "disconnected"]:
                continue
                
            # Check if heartbeat is stale (older than max_heartbeat_age)
            if heartbeat_age > max_heartbeat_age:
                # Mark worker as out_of_service
                self.client.hset(worker_key, "status", "out_of_service")
                logger.warning(f"Worker {worker_id} marked as out_of_service (no heartbeat for {heartbeat_age:.1f} seconds)")
                stale_count += 1
        
        return stale_count
        
    def notify_idle_workers_of_job(self, job_id: str, job_type: str, params: Dict[str, Any] = None) -> List[str]:
        """Notify idle workers about an available job"""
        # Find idle workers
        idle_workers = []
        worker_keys = self.client.keys(f"{WORKER_PREFIX}*")
        
        # First mark stale workers as out_of_service
        self.mark_stale_workers_out_of_service()
        
        for worker_key in worker_keys:
            worker_id = worker_key.replace(f"{WORKER_PREFIX}", "")
            worker_status = self.client.hget(worker_key, "status")
            last_heartbeat = float(self.client.hget(worker_key, "last_heartbeat") or 0)
            
            # Check if worker is idle and has recent heartbeat (last 30 seconds)
            # Explicitly exclude out_of_service workers
            if (worker_status == "idle" and 
                worker_status != "out_of_service" and
                (time.time() - last_heartbeat) < 30):
                idle_workers.append(worker_id)
        
        # Publish notification to job channel
        notification = {
            "type": "job_available",
            "job_id": job_id,
            "job_type": job_type
        }
        
        if params:
            notification["params"] = params
            
        self.client.publish("job_notifications", json.dumps(notification))
        
        logger.info(f"Notified {len(idle_workers)} idle workers about job {job_id}")
        return idle_workers
    
    def claim_job(self, job_id: str, worker_id: str, claim_timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Atomically claim a job with a timeout"""
        job_key = f"{JOB_PREFIX}{job_id}"
        
        # Use Redis transaction to ensure atomicity
        with self.client.pipeline() as pipe:
            try:
                # Watch the job status to ensure it's still pending
                pipe.watch(job_key)
                job_status = pipe.hget(job_key, "status")
                
                if job_status != "pending":
                    pipe.unwatch()
                    logger.warning(f"Worker {worker_id} tried to claim job {job_id}, but status is {job_status}")
                    return None
                
                # Start transaction
                pipe.multi()
                
                # Update job status to claimed with timeout
                pipe.hset(job_key, "status", "claimed")
                pipe.hset(job_key, "worker", worker_id)
                pipe.hset(job_key, "claimed_at", time.time())
                pipe.hset(job_key, "claim_timeout", claim_timeout)
                
                # Execute transaction
                pipe.execute()
                
                # Get job details
                job_data = self.client.hgetall(job_key)
                
                # Parse params back to dict
                if "params" in job_data:
                    job_data["params"] = json.loads(job_data["params"])
                
                logger.info(f"Worker {worker_id} claimed job {job_id}")
                return job_data
                
            except Exception as e:
                logger.error(f"Error claiming job {job_id} by worker {worker_id}: {str(e)}")
                return None
    
    def cleanup_stale_claims(self, max_claim_age: int = 60) -> int:
        """Reset jobs that were claimed but never started processing"""
        current_time = time.time()
        stale_count = 0
        
        # Find claimed jobs
        job_keys = self.client.keys(f"{JOB_PREFIX}*")
        
        for job_key in job_keys:
            job_id = job_key.replace(f"{JOB_PREFIX}", "")
            job_status = self.client.hget(job_key, "status")
            
            # Only check claimed jobs
            if job_status == "claimed":
                claimed_at = float(self.client.hget(job_key, "claimed_at") or 0)
                claim_age = current_time - claimed_at
                claim_timeout = int(self.client.hget(job_key, "claim_timeout") or 30)
                
                # Check if claim is stale
                if claim_age > claim_timeout:
                    # Get job priority
                    priority = int(self.client.hget(job_key, "priority") or 0)
                    
                    # Reset job status to pending
                    self.client.hset(job_key, "status", "pending")
                    self.client.hdel(job_key, "worker")
                    self.client.hdel(job_key, "claimed_at")
                    self.client.hdel(job_key, "claim_timeout")
                    
                    # Add back to queue
                    if priority > 0:
                        self.client.zadd(PRIORITY_QUEUE, {job_id: priority})
                    else:
                        self.client.lpush(STANDARD_QUEUE, job_id)
                        
                    logger.info(f"Reset stale claim for job {job_id} back to pending status")
                    stale_count += 1
        
        return stale_count
    
    # Redis pub/sub methods
    def publish_job_update(self, job_id: str, status: str, **kwargs) -> bool:
        """Publish a job update event"""
        try:
            # Create update message
            message = {
                "job_id": job_id,
                "status": status,
                "timestamp": time.time(),
                **kwargs
            }
            
            # Publish to job-specific channel
            self.client.publish(f"job_updates:{job_id}", json.dumps(message))
            
            # Also publish to global job updates channel
            self.client.publish("job_updates", json.dumps(message))
            
            return True
        except Exception as e:
            logger.error(f"Error publishing job update: {str(e)}")
            return False
    
    async def subscribe_to_channel(self, channel: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe to a Redis channel for updates"""
        if not self.async_client:
            await self.connect_async()
        
        await self.pubsub.subscribe(**{channel: callback})
        logger.info(f"Subscribed to Redis channel: {channel}")
