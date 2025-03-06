#!/usr/bin/env python3
# Data models for the Redis queue system
import logging
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List, Union
import time
import uuid

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

# WebSocket message models
class MessageType:
    # Client to Server Messages
    SUBMIT_JOB = "submit_job"
    GET_JOB_STATUS = "get_job_status"
    REGISTER_WORKER = "register_worker"
    GET_NEXT_JOB = "get_next_job"
    UPDATE_JOB_PROGRESS = "update_job_progress"
    COMPLETE_JOB = "complete_job"
    GET_STATS = "get_stats"
    SUBSCRIBE_STATS = "subscribe_stats"
    SUBSCRIBE_JOB = "subscribe_job"

    # Server to Client Messages
    JOB_ACCEPTED = "job_accepted"
    JOB_STATUS = "job_status"
    JOB_UPDATE = "job_update"
    JOB_ASSIGNED = "job_assigned"
    JOB_COMPLETED = "job_completed"
    STATS_RESPONSE = "stats_response"
    ERROR = "error"
    WORKER_REGISTERED = "worker_registered"

class BaseMessage(BaseModel):
    type: str
    timestamp: float = Field(default_factory=time.time)

# Client to Server Messages
class SubmitJobMessage(BaseMessage):
    type: str = MessageType.SUBMIT_JOB
    job_type: str
    priority: int = 0
    payload: Dict[str, Any]

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

class GetStatsMessage(BaseMessage):
    type: str = MessageType.GET_STATS

class SubscribeStatsMessage(BaseMessage):
    type: str = MessageType.SUBSCRIBE_STATS
    enabled: bool = True  # Whether to enable or disable stats subscription

class SubscribeJobMessage(BaseMessage):
    type: str = MessageType.SUBSCRIBE_JOB
    job_id: str

# Server to Client Messages
class JobAcceptedMessage(BaseMessage):
    type: str = MessageType.JOB_ACCEPTED
    job_id: str
    status: str = "pending"
    position: Optional[int] = None
    estimated_start: Optional[str] = None

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
    result: Optional[Dict[str, Any]] = None

# Nested Pydantic models for stats response
class QueueStats(BaseModel):
    """Stats about job queues"""
    priority: int
    standard: int
    total: int

class JobStatusCounts(BaseModel):
    """Counts of jobs by status"""
    pending: int = 0
    processing: int = 0
    completed: int = 0
    failed: int = 0
    
    # Allow extra fields for flexibility
    class Config:
        extra = "allow"

class JobStats(BaseModel):
    """Stats about jobs"""
    total: int
    status: JobStatusCounts

class WorkerStatusCounts(BaseModel):
    """Counts of workers by status"""
    active: int = 0
    idle: int = 0
    disconnected: int = 0
    
    # Allow extra fields for flexibility
    class Config:
        extra = "allow"

class WorkerStats(BaseModel):
    """Stats about workers"""
    total: int
    status: WorkerStatusCounts

class StatsResponseMessage(BaseMessage):
    """Response message for system statistics request.
    
    This model matches exactly the structure returned by the Redis service's get_stats method.
    Using nested Pydantic models for better validation and documentation.
    
    Structure:
    {
        "queues": {
            "priority": int,
            "standard": int,
            "total": int
        },
        "jobs": {
            "total": int,
            "status": {
                "pending": int,
                "processing": int,
                "completed": int,
                "failed": int
            }
        },
        "workers": {
            "total": int,
            "status": {
                "active": int,
                "idle": int,
                "disconnected": int
            }
        }
    }
    """
    type: str = MessageType.STATS_RESPONSE
    queues: QueueStats
    jobs: JobStats
    workers: WorkerStats
    
    @validator('*', pre=True)
    def log_validation(cls, v, field):
        """Log validation steps to help debug validation errors"""
        logger.debug(f"Validating field '{field.name}' with value: {v}")
        return v

class ErrorMessage(BaseMessage):
    type: str = MessageType.ERROR
    error: str
    details: Optional[Dict[str, Any]] = None

class WorkerRegisteredMessage(BaseMessage):
    type: str = MessageType.WORKER_REGISTERED
    worker_id: str
    status: str = "active"

# Message factory for parsing incoming messages
def parse_message(data: Dict[str, Any]) -> BaseMessage:
    message_type = data.get("type")
    
    if message_type == MessageType.SUBMIT_JOB:
        return SubmitJobMessage(**data)
    elif message_type == MessageType.GET_JOB_STATUS:
        return GetJobStatusMessage(**data)
    elif message_type == MessageType.REGISTER_WORKER:
        return RegisterWorkerMessage(**data)
    elif message_type == MessageType.GET_NEXT_JOB:
        return GetNextJobMessage(**data)
    elif message_type == MessageType.UPDATE_JOB_PROGRESS:
        return UpdateJobProgressMessage(**data)
    elif message_type == MessageType.COMPLETE_JOB:
        return CompleteJobMessage(**data)
    elif message_type == MessageType.GET_STATS:
        return GetStatsMessage(**data)
    elif message_type == MessageType.SUBSCRIBE_STATS:
        return SubscribeStatsMessage(**data)
    else:
        raise ValueError(f"Unknown message type: {message_type}")
