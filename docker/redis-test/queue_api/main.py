#!/usr/bin/env python3
# Main entry point for the WebSocket-based Queue API
import os
import logging
import asyncio
import uvicorn
from fastapi import FastAPI
from typing import Dict, Any
from contextlib import asynccontextmanager

from .routes import init_routes, start_redis_listener
from .redis_service import RedisService

# Configure logging
import logging.handlers
import sys

# Set up detailed logging configuration
def setup_logging():
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Clear any existing handlers to avoid duplicate logs
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Default level from environment or DEBUG for better visibility
    log_level_name = os.environ.get("LOG_LEVEL", "DEBUG")
    log_level = getattr(logging, log_level_name.upper(), logging.DEBUG)
    
    # Set root logger level
    root_logger.setLevel(log_level)
    
    # Create console handler with detailed formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Detailed format with component name and line numbers for better debugging
    log_format = "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for different components to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Ensure our application components log at DEBUG level
    logging.getLogger("queue_api.connections").setLevel(logging.DEBUG)
    logging.getLogger("queue_api.routes").setLevel(logging.DEBUG)
    logging.getLogger("queue_api.redis_service").setLevel(logging.DEBUG)
    
    return root_logger

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)
logger.info("Logging configured with enhanced debug information")

# Background task for stale job cleanup
async def stale_job_cleanup_task():
    """Periodically check for and clean up stale jobs"""
    # Run cleanup every 5 minutes (300 seconds)
    cleanup_interval = int(os.environ.get("JOB_CLEANUP_INTERVAL", 300))
    # Max heartbeat age - default 10 minutes (600 seconds)
    max_heartbeat_age = int(os.environ.get("MAX_WORKER_HEARTBEAT_AGE", 600))
    
    logger.info(f"🔄 Starting periodic job cleanup task (interval: {cleanup_interval}s, max heartbeat age: {max_heartbeat_age}s)")
    
    while True:
        try:
            # Wait first to allow system to stabilize on startup
            await asyncio.sleep(cleanup_interval)
            
            # Run cleanup
            cleaned_count = redis_service.cleanup_stale_jobs(max_heartbeat_age)
            logger.info(f"Job cleanup completed - cleaned {cleaned_count} stale jobs")
            
        except Exception as e:
            logger.error(f"Error in job cleanup task: {str(e)}")
            # Continue running even if there's an error

# FastAPI startup and shutdown event handling
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background tasks
    cleanup_task = asyncio.create_task(stale_job_cleanup_task())
    
    # Initialize WebSocket routes
    init_routes(app)
    
    # Start Redis pub/sub listener
    await start_redis_listener()
    
    # Log startup
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = os.environ.get("REDIS_PORT", 6379)
    logger.info(f"Starting WebSocket Queue API with Redis at {redis_host}:{redis_port}")
    
    yield
    
    # Shutdown tasks
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    # Close Redis connections
    await redis_service.close_async()
    logger.info("WebSocket Queue API shutting down")

# Initialize FastAPI with lifespan manager
app = FastAPI(title="WebSocket Queue API", lifespan=lifespan)

# These event handlers are replaced by the lifespan context manager

@app.get("/")
def read_root():
    """Root endpoint for health check"""
    return {"status": "ok", "message": "WebSocket Queue API is running"}

# Run the application
if __name__ == "__main__":
    uvicorn.run("queue_api.main:app", host="0.0.0.0", port=8000, reload=True)
