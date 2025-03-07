#!/usr/bin/env python3
# Test client for submitting jobs to the EmProps Redis Queue Mock Environment
import asyncio
import json
import uuid
import random
import argparse
import aiohttp
import logging
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test-client")

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/client"

JOB_TYPES = ["image_generation", "text_generation", "upscale", "inpainting", "style_transfer"]

async def submit_job(session: aiohttp.ClientSession, job_type: str, priority: int) -> Dict[str, Any]:
    """Submit a job to the API"""
    # Generate random parameters based on job type
    if job_type == "image_generation":
        params = {
            "prompt": f"Test prompt {uuid.uuid4()}",
            "width": random.choice([512, 768, 1024]),
            "height": random.choice([512, 768, 1024]),
            "steps": random.randint(20, 50),
            "seed": random.randint(0, 1000000)
        }
    elif job_type == "text_generation":
        params = {
            "prompt": f"Test prompt {uuid.uuid4()}",
            "max_tokens": random.randint(50, 200),
            "temperature": random.uniform(0.7, 1.0)
        }
    else:
        params = {
            "test_param": f"Test value {uuid.uuid4()}",
            "random_param": random.randint(1, 100)
        }
    
    # Create job payload
    payload = {
        "job_type": job_type,
        "priority": priority,
        "params": params
    }
    
    logger.info(f"Submitting {job_type} job with priority {priority}")
    
    # Submit job
    async with session.post(f"{API_URL}/jobs", json=payload) as response:
        if response.status == 200:
            result = await response.json()
            logger.info(f"Job submitted successfully: {result.get('job_id')}")
            return result
        else:
            error = await response.text()
            logger.error(f"Failed to submit job: {error}")
            return {"error": error}

async def check_job_status(session: aiohttp.ClientSession, job_id: str) -> Dict[str, Any]:
    """Check the status of a job"""
    async with session.get(f"{API_URL}/jobs/{job_id}") as response:
        if response.status == 200:
            result = await response.json()
            logger.info(f"Job {job_id} status: {result.get('status')}")
            return result
        else:
            error = await response.text()
            logger.error(f"Failed to get job status: {error}")
            return {"error": error}

async def get_system_stats(session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Get system stats"""
    async with session.get(f"{API_URL}/stats") as response:
        if response.status == 200:
            result = await response.json()
            logger.info(f"System stats: {result}")
            return result
        else:
            error = await response.text()
            logger.error(f"Failed to get system stats: {error}")
            return {"error": error}

async def listen_for_updates(client_id: str):
    """Connect to WebSocket and listen for job updates"""
    logger.info(f"Connecting to WebSocket for real-time updates with client ID: {client_id}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(f"{WS_URL}/{client_id}") as ws:
                logger.info("Connected to WebSocket")
                
                while True:
                    msg = await ws.receive()
                    
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        logger.info(f"Received update: {data}")
                    elif msg.type in [aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR]:
                        logger.warning("WebSocket connection closed")
                        break
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")

async def submit_batch_jobs(num_jobs: int):
    """Submit a batch of random jobs"""
    client_id = f"test-client-{uuid.uuid4()}"
    logger.info(f"Starting test client with ID: {client_id}")
    
    # Start WebSocket listener in the background
    asyncio.create_task(listen_for_updates(client_id))
    
    active_jobs = []
    
    try:
        async with aiohttp.ClientSession() as session:
            # Submit initial batch of jobs
            for _ in range(num_jobs):
                job_type = random.choice(JOB_TYPES)
                priority = random.randint(0, 10)
                
                result = await submit_job(session, job_type, priority)
                
                if "job_id" in result:
                    active_jobs.append(result["job_id"])
                
                # Wait a bit between job submissions
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Periodically check job status and submit new jobs
            while True:
                # Check status of active jobs
                for job_id in list(active_jobs):
                    result = await check_job_status(session, job_id)
                    
                    # Remove completed or failed jobs
                    if result.get("status") in ["completed", "failed"]:
                        active_jobs.remove(job_id)
                        
                        # Submit a new job to replace completed/failed
                        job_type = random.choice(JOB_TYPES)
                        priority = random.randint(0, 10)
                        
                        result = await submit_job(session, job_type, priority)
                        
                        if "job_id" in result:
                            active_jobs.append(result["job_id"])
                
                # Get system stats every 10 seconds
                if random.random() < 0.2:
                    await get_system_stats(session)
                
                # Wait before next check
                await asyncio.sleep(5)
                
    except KeyboardInterrupt:
        logger.info("Test client stopping...")
    except Exception as e:
        logger.error(f"Error in test client: {str(e)}")

async def interactive_mode():
    """Run in interactive mode"""
    client_id = f"interactive-client-{uuid.uuid4()}"
    logger.info(f"Starting interactive client with ID: {client_id}")
    
    # Start WebSocket listener in the background
    asyncio.create_task(listen_for_updates(client_id))
    
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                print("\nEmProps Redis Queue Test Client")
                print("--------------------------------")
                print("1. Submit a job")
                print("2. Check job status")
                print("3. Get system stats")
                print("4. Start batch submission (10 jobs)")
                print("0. Exit")
                
                choice = input("\nEnter your choice: ")
                
                if choice == "1":
                    print("\nJob Types:")
                    for i, job_type in enumerate(JOB_TYPES):
                        print(f"{i+1}. {job_type}")
                    
                    job_choice = int(input("\nSelect job type (1-5): ")) - 1
                    if 0 <= job_choice < len(JOB_TYPES):
                        job_type = JOB_TYPES[job_choice]
                    else:
                        print("Invalid choice, using image_generation")
                        job_type = "image_generation"
                    
                    priority = int(input("Enter priority (0-10): "))
                    priority = max(0, min(10, priority))
                    
                    result = await submit_job(session, job_type, priority)
                    print(f"\nSubmission result: {json.dumps(result, indent=2)}")
                
                elif choice == "2":
                    job_id = input("\nEnter job ID: ")
                    result = await check_job_status(session, job_id)
                    print(f"\nJob status: {json.dumps(result, indent=2)}")
                
                elif choice == "3":
                    result = await get_system_stats(session)
                    print(f"\nSystem stats: {json.dumps(result, indent=2)}")
                
                elif choice == "4":
                    print("\nStarting batch submission of 10 jobs...")
                    for _ in range(10):
                        job_type = random.choice(JOB_TYPES)
                        priority = random.randint(0, 10)
                        await submit_job(session, job_type, priority)
                        await asyncio.sleep(0.5)
                    print("Batch submission complete!")
                
                elif choice == "0":
                    print("\nExiting...")
                    break
                
                else:
                    print("\nInvalid choice!")
                
    except KeyboardInterrupt:
        print("\nTest client stopping...")
    except Exception as e:
        logger.error(f"Error in interactive client: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EmProps Redis Queue Test Client")
    parser.add_argument("--batch", type=int, help="Run in batch mode with specified number of jobs")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.batch:
        asyncio.run(submit_batch_jobs(args.batch))
    elif args.interactive:
        asyncio.run(interactive_mode())
    else:
        print("Please specify --batch <number_of_jobs> or --interactive")
