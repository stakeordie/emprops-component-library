#!/usr/bin/env python3
# WebSocket-based Queue API for Redis job processing - Entry Point
#
# This file serves as the main entry point for the WebSocket-based Queue API.
# It imports and runs the modular implementation from the queue_api package.

import os
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Run the application
if __name__ == "__main__":
    # Import the FastAPI app from the queue_api package
    from queue_api.main import app
    
    # Log startup
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = os.environ.get("REDIS_PORT", 6379)
    logger.info(f"Starting WebSocket Queue API with Redis at {redis_host}:{redis_port}")
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)
