#!/usr/bin/env python3
# Core Redis Queue System
"""
Core Redis Queue System - Essential functionality for production use
"""

# Version information
__version__ = "1.0.0"

# Export key classes for easy import
from .redis_service import RedisService, STANDARD_QUEUE, PRIORITY_QUEUE
from .connections import ConnectionManager
