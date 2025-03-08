#!/usr/bin/env python3
# Main entry point for the core WebSocket-based Queue API
import os
import logging
import asyncio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .routes import init_routes, start_redis_listener
from .redis_service import RedisService

# Configure logging
def setup_logging():
    """Set up basic logging configuration"""
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Clear any existing handlers to avoid duplicate logs
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Default level from environment or INFO for production
    log_level_name = os.environ.get("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    
    # Set root logger level
    root_logger.setLevel(log_level)
    
    # Create console handler with basic formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Basic format for production
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    return root_logger

# Initialize logging
logger = setup_logging()
logger = logging.getLogger(__name__)

# Background task for stale job cleanup
async def stale_job_cleanup_task():
    """Periodically check for and clean up stale jobs"""
    # Run cleanup every 5 minutes (300 seconds)
    cleanup_interval = int(os.environ.get("JOB_CLEANUP_INTERVAL", 300))
    # Max heartbeat age - default 10 minutes (600 seconds)
    max_heartbeat_age = int(os.environ.get("MAX_WORKER_HEARTBEAT_AGE", 600))
    
    logger.info(f"Starting periodic job cleanup task (interval: {cleanup_interval}s, max heartbeat age: {max_heartbeat_age}s)")
    
    while True:
        try:
            # Wait first to allow system to stabilize on startup
            await asyncio.sleep(cleanup_interval)
            
            # Run cleanup
            redis_service = RedisService()
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
    redis_service = RedisService()
    await redis_service.close_async()
    logger.info("WebSocket Queue API shutting down")

# Initialize FastAPI with lifespan manager
app = FastAPI(title="WebSocket Queue API", lifespan=lifespan)

@app.get("/")
def read_root():
    """Root endpoint for health check"""
    return {"status": "ok", "message": "WebSocket Queue API is running"}

# Run the application
if __name__ == "__main__":
    uvicorn.run("core.main:app", host="0.0.0.0", port=8000, reload=False)
