#!/usr/bin/env python3
# Core WebSocket connection manager for the queue system
import json
import logging
import asyncio
from typing import Dict, Set, List, Any, Optional, Callable
from fastapi import WebSocket
from .models import BaseMessage, ErrorMessage

# Create a dedicated logger for WebSocket connections
logger = logging.getLogger(__name__)

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
        
        # Set of worker IDs subscribed to job notifications
        self.job_notification_subscriptions: Set[str] = set()
        
        # Tracks worker status ("idle", "busy", etc.)
        self.worker_status: Dict[str, str] = {}
        
        logger.info("WebSocket connection manager initialized")
    
    async def connect_client(self, websocket: WebSocket, client_id: str) -> None:
        """Connect a client WebSocket"""
        try:
            # Check if client is already connected to avoid duplicate connections
            if client_id in self.client_connections:
                logger.warning(f"Client {client_id} already has an active connection. Closing the old one.")
                try:
                    old_websocket = self.client_connections[client_id]
                    await self._close_websocket(old_websocket, f"Replaced by new connection for {client_id}")
                except Exception as e:
                    logger.warning(f"Error closing old WebSocket for client {client_id}: {str(e)}")
            
            logger.debug(f"Accepting WebSocket connection from client {client_id}")
            print(f"\n\n==== ACCEPTING CLIENT CONNECTION: {client_id} ====\n")
            
            # We won't call websocket.accept() here since it's now handled in the router
            # This allows us to separate connection management from protocol handling
            self.client_connections[client_id] = websocket
            logger.info(f"Client {client_id} connected successfully")
            
            # Send a confirmation message to client
            try:
                welcome_message = {
                    "type": "connection_established",
                    "status": "connected", 
                    "client_id": client_id,
                    "message": "Successfully connected to Redis Hub"
                }
                await websocket.send_text(json.dumps(welcome_message))
                print(f"\n==== WELCOME MESSAGE SENT TO CLIENT: {client_id} ====\n")
            except Exception as e:
                logger.warning(f"Unable to send connection confirmation to client {client_id}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error accepting connection from client {client_id}: {str(e)}")
            print(f"\n\n==== ERROR CONNECTING CLIENT {client_id}: {str(e)} ====\n")
            # Attempt to close connection gracefully if possible
            try:
                await websocket.close(code=1011, reason=f"Connection error: {str(e)}")
            except Exception as close_err:
                logger.warning(f"Failed to close websocket after connection error: {str(close_err)}")
            raise
    
    async def connect_worker(self, websocket: WebSocket, worker_id: str) -> None:
        """Connect a worker WebSocket"""
        try:
            # Check if worker is already connected to avoid duplicate connections
            if worker_id in self.worker_connections:
                logger.warning(f"Worker {worker_id} already has an active connection. Closing the old one.")
                try:
                    old_websocket = self.worker_connections[worker_id]
                    await self._close_websocket(old_websocket, f"Replaced by new connection for {worker_id}")
                except Exception as e:
                    logger.warning(f"Error closing old WebSocket for worker {worker_id}: {str(e)}")
            
            logger.debug(f"Accepting WebSocket connection from worker {worker_id}")
            print(f"\n\n==== ACCEPTING WORKER CONNECTION: {worker_id} ====\n")
            
            # We won't call websocket.accept() here since it's now handled in the router
            # This allows us to separate connection management from protocol handling
            self.worker_connections[worker_id] = websocket
            self.worker_status[worker_id] = "idle"  # Set initial status to idle
            logger.info(f"Worker {worker_id} connected successfully")
            
            # Send a confirmation message to worker
            try:
                welcome_message = {
                    "type": "connection_established",
                    "status": "connected", 
                    "worker_id": worker_id,
                    "message": "Successfully connected to Redis Hub"
                }
                await websocket.send_text(json.dumps(welcome_message))
                print(f"\n==== WELCOME MESSAGE SENT TO WORKER: {worker_id} ====\n")
            except Exception as e:
                logger.warning(f"Unable to send connection confirmation to worker {worker_id}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error accepting connection from worker {worker_id}: {str(e)}")
            print(f"\n\n==== ERROR CONNECTING WORKER {worker_id}: {str(e)} ====\n")
            # Attempt to close connection gracefully if possible
            try:
                await websocket.close(code=1011, reason=f"Connection error: {str(e)}")
            except Exception as close_err:
                logger.warning(f"Failed to close websocket after connection error: {str(close_err)}")
            raise
    
    def disconnect_client(self, client_id: str) -> None:
        """Disconnect a client"""
        if client_id in self.client_connections:
            # Store reference to WebSocket object before deletion
            websocket = self.client_connections[client_id]
            
            # Clean up connections dict first
            del self.client_connections[client_id]
            
            # Clean up subscriptions
            if client_id in self.stats_subscriptions:
                self.stats_subscriptions.remove(client_id)
                
            # Clean up job subscriptions
            jobs_to_remove = []
            for job_id, subscriber_id in self.job_subscriptions.items():
                if subscriber_id == client_id:
                    jobs_to_remove.append(job_id)
            
            for job_id in jobs_to_remove:
                del self.job_subscriptions[job_id]
                logger.debug(f"Removed job subscription for {job_id} from disconnected client {client_id}")
            
            logger.info(f"Client {client_id} disconnected and all subscriptions cleaned up")
            
            # Try to close the connection gracefully (async context but sync function)
            try:
                asyncio.create_task(self._close_websocket(websocket, f"Client {client_id} disconnected"))
            except Exception as e:
                logger.warning(f"Error while closing WebSocket for client {client_id}: {str(e)}")
    
    def disconnect_worker(self, worker_id: str) -> None:
        """Disconnect a worker"""
        if worker_id in self.worker_connections:
            # Store reference to WebSocket object before deletion
            websocket = self.worker_connections[worker_id]
            
            # Clean up connections dict first
            del self.worker_connections[worker_id]
            
            # Clean up worker subscriptions
            if worker_id in self.job_notification_subscriptions:
                self.job_notification_subscriptions.remove(worker_id)
                
            # Clean up worker status
            if worker_id in self.worker_status:
                del self.worker_status[worker_id]
                
            logger.info(f"Worker {worker_id} disconnected and all subscriptions cleaned up")
            
            # Try to close the connection gracefully (async context but sync function)
            try:
                asyncio.create_task(self._close_websocket(websocket, f"Worker {worker_id} disconnected"))
            except Exception as e:
                logger.warning(f"Error while closing WebSocket for worker {worker_id}: {str(e)}")
    
    def is_worker_connected(self, worker_id: str) -> bool:
        """Check if a worker is connected"""
        return worker_id in self.worker_connections
    
    def subscribe_to_job(self, job_id: str, client_id: str) -> None:
        """Subscribe a client to job updates"""
        # Check if client is connected before subscribing
        is_connected = client_id in self.client_connections
        
        print(f"\n\n🔊🔊🔊 JOB SUBSCRIPTION 🔊🔊🔊")
        print(f"🔊 Job ID: {job_id}")
        print(f"🔊 Client ID: {client_id}")
        print(f"🔊 Client connected: {is_connected}")
        
        # Record previous subscription if exists
        prev_client = self.job_subscriptions.get(job_id)
        if prev_client:
            print(f"🔊 Replacing previous subscription: Job {job_id} was subscribed by client {prev_client}")
            logger.info(f"[JOB-SUB] Job {job_id} subscription changed from client {prev_client} to {client_id}")
        
        # Update subscription mapping
        self.job_subscriptions[job_id] = client_id
        
        # Log all current subscriptions after update
        print(f"🔊 Current job subscriptions after update: {self.job_subscriptions}")
        logger.info(f"[JOB-SUB] Client {client_id} subscribed to job {job_id}")
        print(f"🔊🔊🔊 END JOB SUBSCRIPTION 🔊🔊🔊\n\n")
    
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
        print(f"\n\n📢📢📢 CLIENT MESSAGE DELIVERY 📢📢📢")
        print(f"📢 Client ID: {client_id}")
        print(f"📢 Message type: {type(message).__name__}")
        
        # Check client connection status
        if client_id not in self.client_connections:
            print(f"📢 ERROR: Cannot send message - client {client_id} not connected! ❌")
            logger.warning(f"[CLIENT-MSG] Cannot send message to client {client_id}: not connected")
            print(f"📢📢📢 END CLIENT MESSAGE DELIVERY (NO CONNECTION) 📢📢📢\n\n")
            return False
        
        # Get WebSocket connection
        websocket = self.client_connections[client_id]
        print(f"📢 WebSocket connection found for client {client_id}")
        
        try:
            # Serialize the message appropriately
            message_text = None
            message_type = type(message).__name__
            print(f"📢 Serializing message of type {message_type}...")
            
            if hasattr(message, "json"):
                message_text = message.json()
                print(f"📢 Used .json() method for serialization")
            elif isinstance(message, dict):
                message_text = json.dumps(message)
                print(f"📢 Used json.dumps() for dictionary serialization")
            else:
                message_text = str(message)
                print(f"📢 Used str() conversion for serialization")
                
            # Extract and log message details
            msg_type = "unknown"
            msg_id = "unknown"
            msg_status = None
            
            if isinstance(message, dict):
                if "type" in message:
                    msg_type = message["type"]
                if "id" in message:
                    msg_id = message["id"]
                elif "job_id" in message:
                    msg_id = message["job_id"]
                if "status" in message:
                    msg_status = message["status"]
            elif hasattr(message, "type"):
                msg_type = message.type
                if hasattr(message, "id"):
                    msg_id = message.id
                elif hasattr(message, "job_id"):
                    msg_id = message.job_id
                if hasattr(message, "status"):
                    msg_status = message.status
                
            print(f"📢 Message details: type={msg_type}, id={msg_id}")
            if msg_status:
                print(f"📢 Message status: {msg_status}")
                
            # Log message content summary
            if len(message_text) > 1000:
                content_preview = message_text[:500] + "..." + message_text[-500:]
                print(f"📢 Message content preview (first/last 500 chars): {content_preview}")
            else:
                print(f"📢 Message content: {message_text}")
                
            print(f"📢 Message size: {len(message_text)} bytes")
            logger.info(f"[CLIENT-MSG] Sending {message_type} message (type: {msg_type}, id: {msg_id}) to client {client_id}: {len(message_text)} bytes")
            
            # Actually send the message
            print(f"📢 Sending message to client {client_id}...")
            await websocket.send_text(message_text)
            
            print(f"📢 Successfully sent message to client {client_id} ✅")
            logger.info(f"[CLIENT-MSG] Successfully sent message to client {client_id}")
            print(f"📢📢📢 END CLIENT MESSAGE DELIVERY (SUCCESS) 📢📢📢\n\n")
            return True
            
        except RuntimeError as e:
            print(f"📢 RUNTIME ERROR: {str(e)} ❌")
            if "WebSocket is not connected" in str(e) or "Connection is closed" in str(e):
                print(f"📢 WebSocket for client {client_id} is closed, removing connection")
                logger.warning(f"[CLIENT-MSG] WebSocket for client {client_id} is closed, removing connection")
                self.disconnect_client(client_id)
            else:
                logger.error(f"[CLIENT-MSG] Runtime error sending message to client {client_id}: {str(e)}")
            print(f"📢📢📢 END CLIENT MESSAGE DELIVERY (ERROR) 📢📢📢\n\n")
            return False
                
        except Exception as e:
            print(f"📢 ERROR: {str(e)} (type: {type(e).__name__}) ❌")
            logger.error(f"[CLIENT-MSG] Error sending message to client {client_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"📢📢📢 END CLIENT MESSAGE DELIVERY (EXCEPTION) 📢📢📢\n\n")
            return False
    
    async def send_to_worker(self, worker_id: str, message: Any) -> bool:
        """Send a message to a specific worker"""
        print(f"\n\n🔰🔰🔰 WORKER MESSAGE DELIVERY 🔰🔰🔰")
        print(f"🔰 Worker ID: {worker_id}")
        print(f"🔰 Message type: {type(message).__name__}")
        
        # Check worker connection status
        if worker_id not in self.worker_connections:
            print(f"🔰 ERROR: Cannot send message - worker {worker_id} not connected! ❌")
            logger.warning(f"[WORKER-MSG] Cannot send message to worker {worker_id}: not connected")
            print(f"🔰🔰🔰 END WORKER MESSAGE DELIVERY (NO CONNECTION) 🔰🔰🔰\n\n")
            return False
        
        # Get WebSocket connection
        websocket = self.worker_connections[worker_id]
        print(f"🔰 WebSocket connection found for worker {worker_id}")
        
        try:
            # Serialize the message appropriately
            message_text = None
            message_type = type(message).__name__
            print(f"🔰 Serializing message of type {message_type}...")
            
            if hasattr(message, "json"):
                message_text = message.json()
                print(f"🔰 Used .json() method for serialization")
            elif isinstance(message, dict):
                message_text = json.dumps(message)
                print(f"🔰 Used json.dumps() for dictionary serialization")
            else:
                message_text = str(message)
                print(f"🔰 Used str() conversion for serialization")
                
            # Extract and log message details
            msg_type = "unknown"
            msg_id = "unknown"
            job_type = None
            
            if isinstance(message, dict):
                if "type" in message:
                    msg_type = message["type"]
                if "id" in message:
                    msg_id = message["id"]
                elif "job_id" in message:
                    msg_id = message["job_id"]
                if "job_type" in message:
                    job_type = message["job_type"]
            elif hasattr(message, "type"):
                msg_type = message.type
                if hasattr(message, "id"):
                    msg_id = message.id
                elif hasattr(message, "job_id"):
                    msg_id = message.job_id
                if hasattr(message, "job_type"):
                    job_type = message.job_type
                
            print(f"🔰 Message details: type={msg_type}, id={msg_id}")
            if job_type:
                print(f"🔰 Job type: {job_type}")
                
            # Log message content summary
            if len(message_text) > 1000:
                content_preview = message_text[:500] + "..." + message_text[-500:]
                print(f"🔰 Message content preview (first/last 500 chars): {content_preview}")
            else:
                print(f"🔰 Message content: {message_text}")
                
            print(f"🔰 Message size: {len(message_text)} bytes")
            logger.info(f"[WORKER-MSG] Sending {message_type} message (type: {msg_type}, id: {msg_id}) to worker {worker_id}: {len(message_text)} bytes")
            
            # Actually send the message
            print(f"🔰 Sending message to worker {worker_id}...")
            await websocket.send_text(message_text)
            
            print(f"🔰 Successfully sent message to worker {worker_id} ✅")
            logger.info(f"[WORKER-MSG] Successfully sent message to worker {worker_id}")
            print(f"🔰🔰🔰 END WORKER MESSAGE DELIVERY (SUCCESS) 🔰🔰🔰\n\n")
            return True
            
        except RuntimeError as e:
            print(f"🔰 RUNTIME ERROR: {str(e)} ❌")
            if "WebSocket is not connected" in str(e) or "Connection is closed" in str(e):
                print(f"🔰 WebSocket for worker {worker_id} is closed, removing connection")
                logger.warning(f"[WORKER-MSG] WebSocket for worker {worker_id} is closed, removing connection")
                self.disconnect_worker(worker_id)
            else:
                logger.error(f"[WORKER-MSG] Runtime error sending message to worker {worker_id}: {str(e)}")
            print(f"🔰🔰🔰 END WORKER MESSAGE DELIVERY (ERROR) 🔰🔰🔰\n\n")
            return False
                
        except Exception as e:
            print(f"🔰 ERROR: {str(e)} (type: {type(e).__name__}) ❌")
            logger.error(f"[WORKER-MSG] Error sending message to worker {worker_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"🔰🔰🔰 END WORKER MESSAGE DELIVERY (EXCEPTION) 🔰🔰🔰\n\n")
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
            print(f"\n\n🔄🔄🔄 JOB UPDATE FORWARDING 🔄🔄🔄")
            print(f"🔄 Job ID: {job_id}")
            print(f"🔄 Update type: {type(update).__name__}")
            
            # Log all current job subscriptions for debugging
            print(f"🔄 Current job subscriptions: {self.job_subscriptions}")
            
            if job_id in self.job_subscriptions:
                client_id = self.job_subscriptions[job_id]
                logger.info(f"[JOB-UPDATE] Forwarding job {job_id} update to client {client_id}")
                print(f"🔄 Client ID: {client_id}")
                
                # Detailed update content logging
                if hasattr(update, "dict"):
                    update_content = update.dict()
                    print(f"🔄 Update content (dict): {update_content}")
                elif isinstance(update, dict):
                    update_content = update
                    print(f"🔄 Update content (dict): {update_content}")
                else:
                    print(f"🔄 Update content (str): {str(update)}")
                
                # Additional status debugging
                status = None
                if isinstance(update, dict) and "status" in update:
                    status = update["status"]
                elif hasattr(update, "status"):
                    status = update.status
                    
                if status:
                    print(f"🔄 Job status: {status}")
                    logger.info(f"[JOB-UPDATE] Job {job_id} status: {status}")
                
                # Verify client connection exists
                if client_id not in self.client_connections:
                    print(f"🔄 ERROR: Client {client_id} not connected!")
                    logger.error(f"[JOB-UPDATE] Cannot forward update for job {job_id}: Client {client_id} not connected")
                    return False
                
                # Send the update
                print(f"🔄 Attempting to send update to client {client_id}...")
                success = await self.send_to_client(client_id, update)
                
                if success:
                    print(f"🔄 Successfully sent job update to client {client_id} ✅")
                    logger.info(f"[JOB-UPDATE] Successfully sent job {job_id} update to client {client_id}")
                    print(f"🔄🔄🔄 END JOB UPDATE FORWARDING (SUCCESS) 🔄🔄🔄\n\n")
                    return True
                else:
                    print(f"🔄 Failed to send job update to client {client_id} ❌")
                    logger.warning(f"[JOB-UPDATE] Failed to send job {job_id} update to client {client_id}")
                    print(f"🔄🔄🔄 END JOB UPDATE FORWARDING (FAILED) 🔄🔄🔄\n\n")
                    return False
            else:
                print(f"🔄 No client subscribed to job {job_id}, update not forwarded ❌")
                logger.warning(f"[JOB-UPDATE] No client subscribed to job {job_id}, update not forwarded")
                print(f"🔄🔄🔄 END JOB UPDATE FORWARDING (NO SUBSCRIPTION) 🔄🔄🔄\n\n")
                return False
                
        except Exception as e:
            print(f"🔄 ERROR sending job update: {str(e)} ❌")
            logger.error(f"[JOB-UPDATE] Error sending update for job {job_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"🔄🔄🔄 END JOB UPDATE FORWARDING (ERROR) 🔄🔄🔄\n\n")
            return False
    
    async def broadcast_stats(self, stats: Any) -> int:
        """Broadcast stats to all subscribed clients"""
        successful_sends = 0
        
        for client_id in list(self.stats_subscriptions):
            if await self.send_to_client(client_id, stats):
                successful_sends += 1
        
        return successful_sends
        
    def subscribe_worker_to_job_notifications(self, worker_id: str) -> None:
        """Subscribe a worker to job notifications"""
        self.job_notification_subscriptions.add(worker_id)
        logger.debug(f"Worker {worker_id} subscribed to job notifications")
    
    def unsubscribe_worker_from_job_notifications(self, worker_id: str) -> None:
        """Unsubscribe a worker from job notifications"""
        if worker_id in self.job_notification_subscriptions:
            self.job_notification_subscriptions.remove(worker_id)
            logger.debug(f"Worker {worker_id} unsubscribed from job notifications")
    
    def update_worker_status(self, worker_id: str, status: str) -> None:
        """Update a worker's status"""
        if worker_id in self.worker_connections:
            self.worker_status[worker_id] = status
            logger.debug(f"Updated worker {worker_id} status to {status}")
    
    async def notify_idle_workers(self, job_notification: Any) -> int:
        """Send job notification to idle workers subscribed to notifications"""
        successful_sends = 0
        
        # Convert Pydantic model to dict if needed
        if hasattr(job_notification, 'dict'):
            # It's a Pydantic model, convert to dict
            notification_dict = job_notification.dict()
        else:
            # It's already a dict
            notification_dict = job_notification
            
        job_id = notification_dict.get('job_id', 'unknown')
        job_type = notification_dict.get('job_type', 'unknown')
        
        # Ensure the notification has the correct type
        if 'type' not in notification_dict:
            notification_dict['type'] = 'job_available'
        
        print(f"\n\n🔔🔔🔔 JOB NOTIFICATION TO WORKERS 🔔🔔🔔")
        print(f"🔔 Job ID: {job_id}")
        print(f"🔔 Job Type: {job_type}")
        print(f"🔔 Notification content: {notification_dict}")
        
        logger.info(f"[WORKER-NOTIFY] Notifying idle workers about job {job_id} of type {job_type}")
        
        # Log all current worker statuses
        print(f"🔔 All worker statuses: {self.worker_status}")
        print(f"🔔 All workers subscribed to notifications: {self.job_notification_subscriptions}")
        
        # Count total eligible workers for better logging
        idle_workers = []
        for worker_id in list(self.job_notification_subscriptions):
            if worker_id in self.worker_status:
                status = self.worker_status[worker_id]
                print(f"🔔 Worker {worker_id} status: {status}")
                if status == "idle":
                    idle_workers.append(worker_id)
                    print(f"🔔 Worker {worker_id} is idle and will be notified")
                elif status == "out_of_service":
                    print(f"🔔 Worker {worker_id} is out of service, will not be notified")
                else:
                    print(f"🔔 Worker {worker_id} is not idle (status: {status}), will not be notified")
            else:
                print(f"🔔 Worker {worker_id} has no status recorded, will not be notified")
        
        if not idle_workers:
            print(f"🔔 No idle workers found to notify about job {job_id} ⚠️")
            logger.warning(f"[WORKER-NOTIFY] No idle workers found to notify about job {job_id}")
            print(f"🔔🔔🔔 END JOB NOTIFICATION (NO WORKERS) 🔔🔔🔔\n\n")
            return 0
            
        logger.info(f"[WORKER-NOTIFY] Found {len(idle_workers)} idle workers for job {job_id}")
        print(f"🔔 Found {len(idle_workers)} idle workers: {idle_workers}")
        
        # Check that workers are actually connected
        for worker_id in idle_workers.copy():
            if worker_id not in self.worker_connections:
                print(f"🔔 WARNING: Worker {worker_id} marked as idle but not connected! ⚠️")
                logger.warning(f"[WORKER-NOTIFY] Worker {worker_id} is marked as idle but not connected")
                idle_workers.remove(worker_id)
        
        # Create a copy of the notification for each worker to avoid shared references
        # This ensures each worker gets its own notification with accurate worker count
        base_notification = notification_dict.copy()
        
        # Send to eligible workers
        print(f"🔔 Attempting to notify {len(idle_workers)} idle workers about job {job_id}...")
        for worker_id in idle_workers:
            print(f"🔔 Sending job notification to worker {worker_id}...")
            logger.debug(f"[WORKER-NOTIFY] Sending job {job_id} notification to worker {worker_id}")
            
            # Create a worker-specific notification with accurate worker count
            worker_notification = base_notification.copy()
            # If this is a worker_notification type message, ensure worker_count is correct
            if worker_notification.get('type') == 'worker_notification':
                worker_notification['worker_count'] = len(idle_workers)
            
            success = await self.send_to_worker(worker_id, worker_notification)
            if success:
                successful_sends += 1
                print(f"🔔 Successfully sent job notification to worker {worker_id} ✅")
                logger.info(f"[WORKER-NOTIFY] Successfully sent job {job_id} notification to worker {worker_id}")
            else:
                print(f"🔔 Failed to send job notification to worker {worker_id} ❌")
                logger.warning(f"[WORKER-NOTIFY] Failed to send job {job_id} notification to worker {worker_id}")
        
        if successful_sends > 0:
            print(f"🔔 Successfully notified {successful_sends}/{len(idle_workers)} idle workers about job {job_id} ✅")
            logger.info(f"[WORKER-NOTIFY] Successfully notified {successful_sends}/{len(idle_workers)} idle workers about job {job_id}")
        else:
            print(f"🔔 No idle workers could be notified about job {job_id} ❌")
            logger.warning(f"[WORKER-NOTIFY] No idle workers could be notified about job {job_id}")
            
        print(f"🔔🔔🔔 END JOB NOTIFICATION TO WORKERS 🔔🔔🔔\n\n")
        return successful_sends
    
    async def broadcast_job_notification(self, job_notification: Dict[str, Any]) -> int:
        """Broadcast job notification to all workers regardless of status"""
        successful_sends = 0
        
        for worker_id in list(self.worker_connections.keys()):
            if await self.send_to_worker(worker_id, job_notification):
                successful_sends += 1
        
        return successful_sends
        
    async def _close_websocket(self, websocket: WebSocket, reason: str) -> None:
        """Gracefully close a WebSocket connection with error handling
        
        Args:
            websocket: The WebSocket connection to close
            reason: The reason for closing the connection
        """
        try:
            logger.debug(f"Attempting to close WebSocket connection: {reason}")
            # Use a standard WebSocket close code (1000 = normal closure)
            await websocket.close(code=1000, reason=reason)
            logger.info(f"WebSocket connection closed successfully: {reason}")
        except RuntimeError as e:
            # Handle specific runtime errors like "WebSocket is not connected"
            if "WebSocket is not connected" in str(e) or "Connection is closed" in str(e):
                logger.debug(f"WebSocket already closed: {reason}")
            else:
                logger.warning(f"Runtime error while closing WebSocket: {str(e)}")
        except Exception as e:
            # Handle any other unexpected errors
            logger.warning(f"Error while closing WebSocket: {str(e)}, type: {type(e).__name__}")
