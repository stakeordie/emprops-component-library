#!/usr/bin/env python3
# Core data models for the Redis queue system
import json
import logging
import time
import uuid
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List, Union

# Initialize logger
logger = logging.getLogger(__name__)

# Job model for job submission
class Job(BaseModel):
    id: str = Field(default_factory=lambda: f"job-{uuid.uuid4()}")
    type: str
    priority: int = 0
    params: Dict[str, Any]
    client_id: Optional[str] = None

# Worker identification for job processing
class WorkerInfo(BaseModel):
    machine_id: str
    gpu_id: int
    worker_id: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.worker_id:
            self.worker_id = f"{self.machine_id}:{self.gpu_id}"

# WebSocket message types
class MessageType:
    # Client to Server Messages
    SUBMIT_JOB = "submit_job"
    GET_JOB_STATUS = "get_job_status"
    REGISTER_WORKER = "register_worker"
    GET_NEXT_JOB = "get_next_job"
    UPDATE_JOB_PROGRESS = "update_job_progress"
    COMPLETE_JOB = "complete_job"
    FAIL_JOB = "fail_job"
    GET_STATS = "get_stats"
    SUBSCRIBE_STATS = "subscribe_stats"
    SUBSCRIBE_JOB = "subscribe_job"
    
    # Worker Status Messages
    WORKER_HEARTBEAT = "worker_heartbeat"
    CLAIM_JOB = "claim_job"
    JOB_CLAIMED = "job_claimed"
    SUBSCRIBE_JOB_NOTIFICATIONS = "subscribe_job_notifications"

    # Server to Client Messages
    JOB_ACCEPTED = "job_accepted"
    JOB_STATUS = "job_status"
    JOB_UPDATE = "job_update"
    JOB_ASSIGNED = "job_assigned"
    JOB_COMPLETED = "job_completed"
    STATS_RESPONSE = "stats_response"
    ERROR = "error"
    WORKER_REGISTERED = "worker_registered"
    
    # Server to Worker Notifications
    JOB_AVAILABLE = "job_available"

# Base message class
class BaseMessage(BaseModel):
    type: str
    timestamp: float = Field(default_factory=time.time)

# Core Client to Server Messages
class SubmitJobMessage(BaseMessage):
    type: str = MessageType.SUBMIT_JOB
    job_type: str
    priority: int = 0
    payload: Dict[str, Any]
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is None:
            return 0
        try:
            return int(v)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert priority {v} to integer, using 0")
            return 0

class GetJobStatusMessage(BaseMessage):
    type: str = MessageType.GET_JOB_STATUS
    job_id: str

class RegisterWorkerMessage(BaseMessage):
    type: str = MessageType.REGISTER_WORKER
    machine_id: str
    gpu_id: int

class GetNextJobMessage(BaseMessage):
    type: str = MessageType.GET_NEXT_JOB
    machine_id: str
    gpu_id: int

class UpdateJobProgressMessage(BaseMessage):
    type: str = MessageType.UPDATE_JOB_PROGRESS
    job_id: str
    machine_id: str
    gpu_id: int
    progress: int
    status: str = "processing"
    message: Optional[str] = None

class CompleteJobMessage(BaseMessage):
    type: str = MessageType.COMPLETE_JOB
    job_id: str
    machine_id: str
    gpu_id: int
    result: Optional[Dict[str, Any]] = None

# Core Server to Client Messages
class JobAcceptedMessage(BaseMessage):
    type: str = MessageType.JOB_ACCEPTED
    job_id: str
    status: str = "pending"
    position: Optional[int] = None
    estimated_start: Optional[str] = None
    notified_workers: Optional[int] = 0  # Number of workers notified about this job

class JobStatusMessage(BaseMessage):
    type: str = MessageType.JOB_STATUS
    job_id: str
    status: str
    progress: Optional[int] = None
    worker_id: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class JobUpdateMessage(BaseMessage):
    type: str = MessageType.JOB_UPDATE
    job_id: str
    status: str
    priority: Optional[int] = None
    position: Optional[int] = None
    progress: Optional[int] = None
    eta: Optional[str] = None
    message: Optional[str] = None

class JobAssignedMessage(BaseMessage):
    type: str = MessageType.JOB_ASSIGNED
    job_id: str
    job_type: str
    priority: int
    params: Dict[str, Any]

class JobCompletedMessage(BaseMessage):
    type: str = MessageType.JOB_COMPLETED
    job_id: str
    status: str = "completed"
    priority: Optional[int] = None
    position: Optional[int] = None
    result: Optional[Dict[str, Any]] = None

class ErrorMessage(BaseMessage):
    type: str = MessageType.ERROR
    error: str
    details: Optional[Dict[str, Any]] = None

class WorkerRegisteredMessage(BaseMessage):
    type: str = MessageType.WORKER_REGISTERED
    worker_id: str
    status: str = "active"

# Message factory for parsing incoming messages
def parse_message(data: Dict[str, Any]) -> Optional[BaseMessage]:
    """Parse incoming message data into appropriate message model"""
    if not isinstance(data, dict) or "type" not in data:
        logger.error(f"Invalid message format: {data}")
        return None
    
    message_type = data.get("type")
    
    # Map message types to their models
    message_models = {
        MessageType.SUBMIT_JOB: SubmitJobMessage,
        MessageType.GET_JOB_STATUS: GetJobStatusMessage,
        MessageType.REGISTER_WORKER: RegisterWorkerMessage,
        MessageType.GET_NEXT_JOB: GetNextJobMessage,
        MessageType.UPDATE_JOB_PROGRESS: UpdateJobProgressMessage,
        MessageType.COMPLETE_JOB: CompleteJobMessage,
        MessageType.SUBSCRIBE_JOB: SubscribeJobMessage,
        MessageType.SUBSCRIBE_STATS: SubscribeStatsMessage,
        MessageType.GET_STATS: GetStatsMessage,
        
        # New message types for push-based notification system
        MessageType.WORKER_HEARTBEAT: WorkerHeartbeatMessage,
        MessageType.CLAIM_JOB: ClaimJobMessage,
        MessageType.SUBSCRIBE_JOB_NOTIFICATIONS: SubscribeJobNotificationsMessage,
    }
    
    if message_type not in message_models:
        logger.error(f"Unknown message type: {message_type}")
        return None
    
    try:
        # Add detailed logging for subscription messages
        if message_type == MessageType.SUBSCRIBE_JOB_NOTIFICATIONS:
            logger.info(f"\n\n🔎🔎🔎 PARSING SUBSCRIBE_JOB_NOTIFICATIONS MESSAGE: {data}")
            logger.info(f"🔎 FULL MESSAGE CONTENT: {json.dumps(data, indent=2)}")
            logger.info(f"🔎 Data keys: {list(data.keys())}")
            logger.info(f"🔎 worker_id present: {'worker_id' in data}")
            if 'worker_id' in data:
                logger.info(f"🔎 worker_id value: {data['worker_id']}")
            logger.info(f"🔎 Message type value: {data.get('type')}")
            logger.info(f"🔎 Expected type value: {MessageType.SUBSCRIBE_JOB_NOTIFICATIONS}")
            
        return message_models[message_type](**data)
    except Exception as e:
        logger.error(f"Error parsing message of type {message_type}: {str(e)}")
        # For subscription messages, log more details about the error
        if message_type == MessageType.SUBSCRIBE_JOB_NOTIFICATIONS:
            logger.error(f"🔴 Failed to parse subscription message. FULL DATA: {json.dumps(data, indent=2)}")
            logger.error(f"🔴 Expected model: {message_models[message_type].__name__}")
            logger.error(f"🔴 Error details: {str(e)}")
            # Print the exact validation error with full context
            import traceback
            logger.error(f"🔴 Error traceback: {traceback.format_exc()}")
        return None

# Simple stats models (basic versions for core functionality)
class SubscribeStatsMessage(BaseMessage):
    type: str = MessageType.SUBSCRIBE_STATS
    enabled: bool = True

class GetStatsMessage(BaseMessage):
    type: str = MessageType.GET_STATS

class SubscribeJobMessage(BaseMessage):
    type: str = MessageType.SUBSCRIBE_JOB
    job_id: str
    
# Worker Heartbeat and Status Messages
class WorkerHeartbeatMessage(BaseMessage):
    type: str = MessageType.WORKER_HEARTBEAT
    worker_id: str
    status: Optional[str] = "idle"
    load: Optional[float] = 0.0
    
class ClaimJobMessage(BaseMessage):
    type: str = MessageType.CLAIM_JOB
    worker_id: str
    job_id: str
    claim_timeout: Optional[int] = 30
    
class JobClaimedMessage(BaseMessage):
    type: str = MessageType.JOB_CLAIMED
    job_id: str
    worker_id: str
    success: bool
    job_data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    
class SubscribeJobNotificationsMessage(BaseMessage):
    type: str = MessageType.SUBSCRIBE_JOB_NOTIFICATIONS
    worker_id: str
    enabled: bool = True
    
# Job Notification Messages
class JobAvailableMessage(BaseMessage):
    type: str = MessageType.JOB_AVAILABLE
    job_id: str
    job_type: str
    priority: Optional[int] = 0
    params_summary: Optional[Dict[str, Any]] = None
