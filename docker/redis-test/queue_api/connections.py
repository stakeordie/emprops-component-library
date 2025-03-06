#!/usr/bin/env python3
# WebSocket connection manager for the queue system
import json
import logging
import asyncio
import traceback
from typing import Dict, Set, List, Any, Optional, Callable
from fastapi import WebSocket, WebSocketDisconnect
from .models import BaseMessage, ErrorMessage

# Create a dedicated logger for WebSocket connections
logger = logging.getLogger(__name__)

# Function to safely get message type for logging
def get_message_type(message: Any) -> str:
    """Extract message type in a safe way for logging purposes"""
    try:
        if hasattr(message, 'type'):
            return message.type
        elif isinstance(message, dict) and 'type' in message:
            return message['type']
        else:
            return type(message).__name__
    except Exception:
        return 'unknown'

class ConnectionManager:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self):
        """Initialize connection manager"""
        # Maps client IDs to their WebSocket connections
        self.client_connections: Dict[str, WebSocket] = {}
        
        # Maps worker IDs to their WebSocket connections
        self.worker_connections: Dict[str, WebSocket] = {}
        
        # Maps job IDs to client IDs that should receive updates
        self.job_subscriptions: Dict[str, str] = {}
        
        # Set of client IDs subscribed to system stats updates
        self.stats_subscriptions: Set[str] = set()
        
        logger.info("WebSocket connection manager initialized")
    
    async def connect_client(self, websocket: WebSocket, client_id: str) -> None:
        """Connect a client WebSocket"""
        await websocket.accept()
        self.client_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
    
    async def connect_worker(self, websocket: WebSocket, worker_id: str) -> None:
        """Connect a worker WebSocket"""
        await websocket.accept()
        self.worker_connections[worker_id] = websocket
        logger.info(f"Worker {worker_id} connected")
    
    def disconnect_client(self, client_id: str) -> None:
        """Disconnect a client"""
        if client_id in self.client_connections:
            del self.client_connections[client_id]
            # Also remove from stats subscriptions when disconnected
            if client_id in self.stats_subscriptions:
                self.stats_subscriptions.remove(client_id)
            logger.info(f"Client {client_id} disconnected")
    
    def disconnect_worker(self, worker_id: str) -> None:
        """Disconnect a worker"""
        if worker_id in self.worker_connections:
            del self.worker_connections[worker_id]
            logger.info(f"Worker {worker_id} disconnected")
    
    def subscribe_to_job(self, job_id: str, client_id: str) -> None:
        """Subscribe a client to job updates"""
        self.job_subscriptions[job_id] = client_id
        logger.debug(f"Client {client_id} subscribed to job {job_id}")
    
    def subscribe_to_stats(self, client_id: str) -> None:
        """Subscribe a client to system stats updates"""
        self.stats_subscriptions.add(client_id)
        logger.debug(f"Client {client_id} subscribed to system stats updates")
        
    def unsubscribe_from_stats(self, client_id: str) -> None:
        """Unsubscribe a client from system stats updates"""
        if client_id in self.stats_subscriptions:
            self.stats_subscriptions.remove(client_id)
            logger.debug(f"Client {client_id} unsubscribed from system stats updates")
    
    async def send_to_client(self, client_id: str, message: Any) -> bool:
        """Send a message to a specific client"""
        if client_id not in self.client_connections:
            logger.warning(f"Cannot send message to client {client_id}: not connected")
            return False
        
        websocket = self.client_connections[client_id]
        message_type = get_message_type(message)
        
        logger.debug(f"Sending message of type '{message_type}' to client {client_id}")
        
        try:
            # Log detailed serialization attempt for debugging
            if hasattr(message, "json"):
                message_json = message.json()
                logger.debug(f"Serialized pydantic model to JSON: {message_json[:200]}{'...' if len(message_json) > 200 else ''}")
                await websocket.send_text(message_json)
            elif isinstance(message, dict):
                message_json = json.dumps(message)
                logger.debug(f"Serialized dict to JSON: {message_json[:200]}{'...' if len(message_json) > 200 else ''}")
                await websocket.send_text(message_json)
            else:
                message_str = str(message)
                logger.debug(f"Converted to string: {message_str[:200]}{'...' if len(message_str) > 200 else ''}")
                await websocket.send_text(message_str)
                
            logger.debug(f"Successfully sent message of type '{message_type}' to client {client_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending message to client {client_id}: {str(e)}")
            logger.error(f"Message type: {message_type}, Error details: {traceback.format_exc()}")
            return False
    
    async def send_to_worker(self, worker_id: str, message: Any) -> bool:
        """Send a message to a specific worker"""
        if worker_id not in self.worker_connections:
            logger.warning(f"Cannot send message to worker {worker_id}: not connected")
            return False
        
        websocket = self.worker_connections[worker_id]
        message_type = get_message_type(message)
        
        logger.debug(f"Sending message of type '{message_type}' to worker {worker_id}")
        
        try:
            # Log detailed serialization attempt for debugging
            if hasattr(message, "json"):
                message_json = message.json()
                logger.debug(f"Serialized pydantic model to JSON: {message_json[:200]}{'...' if len(message_json) > 200 else ''}")
                await websocket.send_text(message_json)
            elif isinstance(message, dict):
                message_json = json.dumps(message)
                logger.debug(f"Serialized dict to JSON: {message_json[:200]}{'...' if len(message_json) > 200 else ''}")
                await websocket.send_text(message_json)
            else:
                message_str = str(message)
                logger.debug(f"Converted to string: {message_str[:200]}{'...' if len(message_str) > 200 else ''}")
                await websocket.send_text(message_str)
                
            logger.debug(f"Successfully sent message of type '{message_type}' to worker {worker_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending message to worker {worker_id}: {str(e)}")
            logger.error(f"Message type: {message_type}, Error details: {traceback.format_exc()}")
            return False
    
    async def broadcast_to_clients(self, message: Any) -> int:
        """Broadcast a message to all connected clients"""
        successful_sends = 0
        
        for client_id in list(self.client_connections.keys()):
            if await self.send_to_client(client_id, message):
                successful_sends += 1
        
        return successful_sends
    
    async def broadcast_to_workers(self, message: Any) -> int:
        """Broadcast a message to all connected workers"""
        successful_sends = 0
        
        for worker_id in list(self.worker_connections.keys()):
            if await self.send_to_worker(worker_id, message):
                successful_sends += 1
        
        return successful_sends
    
    async def send_job_update(self, job_id: str, update: Any) -> bool:
        """Send a job update to the subscribed client"""
        try:
            if job_id in self.job_subscriptions:
                client_id = self.job_subscriptions[job_id]
                
                # Get detailed information about the update for logging
                update_type = get_message_type(update)
                update_status = getattr(update, 'status', 'unknown') if hasattr(update, 'status') else None
                update_progress = getattr(update, 'progress', None) if hasattr(update, 'progress') else None
                
                # Log detailed information about the job update
                log_msg = f"Sending job update type {update_type} for job {job_id} to client {client_id}"
                if update_status:
                    log_msg += f", status: {update_status}"
                if update_progress is not None:
                    log_msg += f", progress: {update_progress}"
                    
                logger.debug(log_msg)
                
                # Try to serialize the update for logging purposes
                try:
                    if hasattr(update, "dict"):
                        update_dict = update.dict()
                        logger.debug(f"Job update content: {json.dumps(update_dict)[:300]}{'...' if len(json.dumps(update_dict)) > 300 else ''}")
                except Exception as ser_err:
                    logger.debug(f"Could not serialize job update for logging: {str(ser_err)}")
                
                return await self.send_to_client(client_id, update)
            else:
                logger.debug(f"No client subscribed to job {job_id}")
                return False
        except Exception as e:
            logger.error(f"Error sending job update for job {job_id}: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            # Don't propagate the exception to prevent WebSocket disconnection
            return False
            
    async def broadcast_stats(self, stats: Any) -> int:
        """Broadcast system stats to all subscribed clients"""
        successful_sends = 0
        
        if not self.stats_subscriptions:
            logger.debug("No clients subscribed to stats, skipping broadcast")
            return 0
        
        # Get stats type for logging
        stats_type = get_message_type(stats)
        logger.debug(f"Broadcasting stats of type '{stats_type}' to {len(self.stats_subscriptions)} subscribed clients")
        
        # Try to serialize the stats for logging purposes
        try:
            if hasattr(stats, "dict"):
                stats_dict = stats.dict()
                logger.debug(f"Stats content: {json.dumps(stats_dict)[:300]}{'...' if len(json.dumps(stats_dict)) > 300 else ''}")
        except Exception as ser_err:
            logger.debug(f"Could not serialize stats for logging: {str(ser_err)}")
        
        for client_id in list(self.stats_subscriptions):
            try:
                if await self.send_to_client(client_id, stats):
                    successful_sends += 1
                    logger.debug(f"Successfully sent stats to client {client_id}")
                else:
                    logger.warning(f"Failed to send stats to client {client_id}")
            except Exception as e:
                logger.error(f"Error sending stats to client {client_id}: {str(e)}")
                logger.error(f"Error details: {traceback.format_exc()}")
        
        logger.debug(f"Stats broadcast complete: {successful_sends}/{len(self.stats_subscriptions)} successful sends")
        return successful_sends
    
    async def handle_client_message(self, client_id: str, message_data: Dict[str, Any], 
                                    message_handlers: Dict[str, Callable]) -> None:
        """Handle a message from a client"""
        message_type = message_data.get("type")
        
        # Super visible log with special highlight for get_stats
        if message_type == "get_stats":
            logger.debug("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            logger.debug("!!!!!! GET_STATS REQUEST DETECTED FROM CLIENT !!!!!!")
            logger.debug(f"!!!!!! CLIENT ID: {client_id} !!!!!!")
            logger.debug(f"!!!!!! FULL MESSAGE: {json.dumps(message_data)} !!!!!!")
            logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
        else:
            logger.debug("\n\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logger.debug(f"INCOMING CLIENT MESSAGE: type={message_type} from {client_id}")
            logger.debug(f"FULL MESSAGE DATA: {json.dumps(message_data)}")
            logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n")
        
        # Log receiving a message
        logger.debug(f"Received message from client {client_id}: type={message_type}")
        logger.debug(f"Message data: {json.dumps(message_data)[:300]}{'...' if len(json.dumps(message_data)) > 300 else ''}")
        
        if message_type not in message_handlers:
            logger.warning(f"Unknown message type from client {client_id}: {message_type}")
            error = ErrorMessage(error=f"Unknown message type: {message_type}")
            await self.send_to_client(client_id, error)
            return
        
        try:
            logger.debug(f"Invoking handler for message type '{message_type}' from client {client_id}")
            handler = message_handlers[message_type]
            await handler(client_id, message_data)
            logger.debug(f"Successfully handled message type '{message_type}' from client {client_id}")
        except Exception as e:
            logger.error(f"Error handling message type '{message_type}' from client {client_id}: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            logger.error(f"Message data: {json.dumps(message_data)[:300]}{'...' if len(json.dumps(message_data)) > 300 else ''}")
            logger.error(f"Error handling message from client {client_id}: {str(e)}")
            error = ErrorMessage(error=str(e))
            await self.send_to_client(client_id, error)
    
    async def handle_worker_message(self, worker_id: str, message_data: Dict[str, Any],
                                    message_handlers: Dict[str, Callable]) -> None:
        """Handle a message from a worker"""
        message_type = message_data.get("type")
        
        # Log receiving a message
        logger.debug(f"Received message from worker {worker_id}: type={message_type}")
        logger.debug(f"Message data: {json.dumps(message_data)[:300]}{'...' if len(json.dumps(message_data)) > 300 else ''}")
        
        if message_type not in message_handlers:
            logger.warning(f"Unknown message type from worker {worker_id}: {message_type}")
            error = ErrorMessage(error=f"Unknown message type: {message_type}")
            await self.send_to_worker(worker_id, error)
            return
        
        try:
            logger.debug(f"Invoking handler for message type '{message_type}' from worker {worker_id}")
            handler = message_handlers[message_type]
            await handler(worker_id, message_data)
            logger.debug(f"Successfully handled message type '{message_type}' from worker {worker_id}")
        except Exception as e:
            logger.error(f"Error handling message type '{message_type}' from worker {worker_id}: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            logger.error(f"Message data: {json.dumps(message_data)[:300]}{'...' if len(json.dumps(message_data)) > 300 else ''}")
            logger.error(f"Error handling message from worker {worker_id}: {str(e)}")
            error = ErrorMessage(error=str(e))
            await self.send_to_worker(worker_id, error)
