#!/usr/bin/env python3
# Hub Container - Redis API + Redis DB
import os
import sys
import time
import json
import uuid
import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Set up enhanced logging first
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
    logging.getLogger("core.connections").setLevel(logging.DEBUG)
    logging.getLogger("core.routes").setLevel(logging.DEBUG)
    logging.getLogger("core.redis_service").setLevel(logging.DEBUG)
    
    return root_logger

# Initialize enhanced logging
setup_logging()
logger = logging.getLogger("redis-hub")
logger.info("Enhanced logging configured for Redis Hub")

# Add core to sys.path so we can import the Redis service
# In the container, core is mounted at /app/core
sys.path.append('/app')

# Configure Redis environment variables for proper container networking
# For the hub container, we need to set REDIS_HOST to localhost since Redis is running locally
os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PORT'] = '6379'

logger.info("System path configuration:")
logger.info(f"sys.path: {sys.path}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Environment variables: REDIS_HOST={os.environ.get('REDIS_HOST')}, REDIS_PORT={os.environ.get('REDIS_PORT')}")

# List directories to help with debugging
logger.info(f"Directory contents: {os.listdir('.')}")
if os.path.exists('/app/core'):
    logger.info(f"/app/core contents: {os.listdir('/app/core')}")

try:
    from core.redis_service import RedisService
    from core.connections import ConnectionManager
    from core.routes import init_routes, start_redis_listener
    logger.info("Successfully imported core modules")
except ImportError as e:
    logger.error(f"Failed to import core modules: {e}")
    # List directories to debug
    if os.path.exists('/app/core'):
        logger.error(f"/app/core contents: {os.listdir('/app/core')}")
    raise

# Logging already set up at the top of the file

# FastAPI startup and shutdown event handling using lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log startup
    logger.info("🚀 Starting Redis Hub service with lifespan context manager")
    logger.info(f"Redis configured at {os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}")
    
    # Initialize Redis service
    redis_service = RedisService()
    
    # Initialize connection manager
    connection_manager = ConnectionManager()
    
    # Initialize WebSocket routes with our services
    init_routes(app, redis_service=redis_service, connection_manager=connection_manager)
    
    # Initialize Redis data structures
    await redis_service.init_redis()
    logger.info("Redis data structures initialized")
    
    # Start Redis pub/sub listener
    await start_redis_listener()
    logger.info("Redis pub/sub listener started")
    
    # Signal readiness for connections
    logger.info("✅ Redis Hub service fully initialized and ready to accept connections")
    
    yield
    
    # Shutdown cleanup
    logger.info("Shutting down Redis Hub service")
    await redis_service.close()
    logger.info("Redis Hub service shut down successfully")

# Create FastAPI application with lifespan manager
app = FastAPI(
    title="EmProps Redis Hub", 
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root endpoint for health check"""
    return {"status": "ok", "message": "Redis Hub service is running"}

if __name__ == "__main__":
    import uvicorn
    
    # Configure uvicorn logging
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["loggers"]["uvicorn"]["level"] = "DEBUG"
    log_config["loggers"]["uvicorn.error"]["level"] = "DEBUG"
    log_config["loggers"]["uvicorn.access"]["level"] = "DEBUG"
    
    # Print startup banner
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║                EmProps Redis Hub Service                   ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    logger.info("Starting Redis Hub WebSocket server on 0.0.0.0:8001")
    
    # Run with settings optimized for WebSocket performance
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",           # Bind to all network interfaces
        port=8001, 
        reload=False,             # Disable reload in production
        workers=1,                # Single worker process for WebSockets
        log_level="debug",
        log_config=log_config,
        timeout_keep_alive=120,   # Increase WebSocket keepalive timeout
        ws_ping_interval=20,      # Send WebSocket ping frames periodically
        ws_ping_timeout=30,       # Timeout for WebSocket ping/pong
        ws_max_size=16777216      # 16MB max message size for large payloads
    )
