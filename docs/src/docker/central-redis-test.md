# Testing the Central Redis Queue System

## Overview

This document outlines a comprehensive testing strategy for the distributed AI job queue system based on Redis. The testing approach allows you to validate the queue's functionality, performance, and reliability in a controlled environment before deploying to production.

The test strategy simulates a multi-machine, multi-GPU environment using mock workers that emulate real GPU processing behavior without requiring actual GPU hardware or AI model inference.

## Testing Philosophy

The testing approach follows these key principles:

1. **Simulation over Hardware Requirements**: Test the queue logic without needing actual GPU hardware
2. **Controlled Variability**: Simulate different processing times to test queue behavior under various conditions
3. **Observable Behavior**: Focus on monitoring job routing, distribution, and completion
4. **Component Isolation**: Test individual components before testing the full system
5. **Real-world Scenarios**: Design tests that mirror actual production workloads

## Test Environment Setup

The test environment consists of the following components:

1. **Redis Server**: Central queue database
2. **Queue API Service**: FastAPI service for queue management
3. **Mock Workers**: Python scripts that simulate GPU machines
4. **Job Submitter**: Script to generate test jobs

### Docker-based Test Environment

The fastest way to set up a complete test environment is using Docker Compose:

```yaml
# docker-compose.test.yml
version: '3'

services:
  redis:
    image: redis:6
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  queue-api:
    build:
      context: ./queue-api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - LOG_LEVEL=INFO
    depends_on:
      - redis

  mock-worker-1:
    build:
      context: ./test
      dockerfile: Dockerfile.mock-worker
    environment:
      - MACHINE_ID=test-machine-1
      - MOCK_GPU_COUNT=2
      - QUEUE_API_URL=http://queue-api:8000
      - MIN_PROCESS_TIME=5
      - MAX_PROCESS_TIME=15
    depends_on:
      - queue-api

  mock-worker-2:
    build:
      context: ./test
      dockerfile: Dockerfile.mock-worker
    environment:
      - MACHINE_ID=test-machine-2
      - MOCK_GPU_COUNT=2
      - QUEUE_API_URL=http://queue-api:8000
      - MIN_PROCESS_TIME=10
      - MAX_PROCESS_TIME=30
    depends_on:
      - queue-api

  job-submitter:
    build:
      context: ./test
      dockerfile: Dockerfile.job-submitter
    environment:
      - QUEUE_API_URL=http://queue-api:8000
      - JOB_COUNT=20
      - SUBMISSION_INTERVAL=2
    depends_on:
      - queue-api

volumes:
  redis-data:
```

### Running the Test Environment

```bash
# Start the test environment
docker-compose -f docker-compose.test.yml up -d

# View logs from all services
docker-compose -f docker-compose.test.yml logs -f

# View logs from a specific service
docker-compose -f docker-compose.test.yml logs -f mock-worker-1

# Stop the test environment
docker-compose -f docker-compose.test.yml down
```

## Mock Implementation

### Mock Worker Implementation

The mock worker simulates GPU processing by sleeping for random intervals. This allows testing of the queue system's distribution logic without requiring actual GPU workloads.

```python
# mock_worker.py
import time
import random
import requests
import os
import logging
from threading import Thread

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MACHINE_ID = os.environ.get('MACHINE_ID', 'test-machine-1')
GPU_COUNT = int(os.environ.get('MOCK_GPU_COUNT', 2))
QUEUE_API_URL = os.environ.get('QUEUE_API_URL', 'http://localhost:8000')
MIN_PROCESS_TIME = int(os.environ.get('MIN_PROCESS_TIME', 5))
MAX_PROCESS_TIME = int(os.environ.get('MAX_PROCESS_TIME', 30))

def process_job(gpu_id, job):
    """Simulate processing a job on a GPU"""
    job_id = job['id']
    logger.info(f"GPU {gpu_id} started processing job {job_id}")
    
    # Simulate processing time
    process_time = random.randint(MIN_PROCESS_TIME, MAX_PROCESS_TIME)
    logger.info(f"Job {job_id} will take {process_time} seconds on GPU {gpu_id}")
    time.sleep(process_time)
    
    # Report job completion
    response = requests.post(
        f"{QUEUE_API_URL}/jobs/{job_id}/complete",
        json={"machine_id": MACHINE_ID, "gpu_id": gpu_id}
    )
    
    if response.status_code == 200:
        logger.info(f"GPU {gpu_id} completed job {job_id} in {process_time}s")
    else:
        logger.error(f"Failed to report completion for job {job_id}: {response.text}")
    
    return True

def gpu_worker(gpu_id):
    """Worker thread for each simulated GPU"""
    logger.info(f"Starting worker thread for GPU {gpu_id}")
    
    while True:
        try:
            # Request a job from the queue
            response = requests.get(
                f"{QUEUE_API_URL}/jobs/next",
                params={"machine_id": MACHINE_ID, "gpu_id": str(gpu_id)}
            )
            
            if response.status_code == 200:
                job = response.json()
                process_job(gpu_id, job)
            elif response.status_code == 204:
                # No jobs available
                logger.debug(f"No jobs available for GPU {gpu_id}, waiting...")
                time.sleep(2)
            else:
                logger.warning(f"Failed to get job: {response.text}")
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"Error in GPU {gpu_id} worker: {str(e)}")
            time.sleep(5)

# Start a worker thread for each simulated GPU
if __name__ == "__main__":
    logger.info(f"Starting mock worker {MACHINE_ID} with {GPU_COUNT} GPUs")
    
    threads = []
    for gpu_id in range(GPU_COUNT):
        thread = Thread(
            target=gpu_worker, 
            args=(gpu_id,),
            name=f"GPU-{gpu_id}"
        )
        thread.daemon = True
        thread.start()
        threads.append(thread)
        
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down mock worker")
```

### Job Submitter Implementation

The job submitter creates test jobs and sends them to the queue API:

```python
# job_submitter.py
import time
import random
import requests
import os
import logging
import json
import uuid

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
QUEUE_API_URL = os.environ.get('QUEUE_API_URL', 'http://localhost:8000')
JOB_COUNT = int(os.environ.get('JOB_COUNT', 10))
SUBMISSION_INTERVAL = float(os.environ.get('SUBMISSION_INTERVAL', 1.0))
MAX_PRIORITY = int(os.environ.get('MAX_PRIORITY', 3))

# Sample job templates for testing
def create_test_job(job_id, priority=0):
    """Create a test job with the given priority"""
    return {
        "id": job_id,
        "type": "test",
        "priority": priority,
        "params": {
            "test_param_1": random.randint(1, 100),
            "test_param_2": str(uuid.uuid4()),
        }
    }

def submit_jobs():
    """Submit a batch of test jobs to the queue API"""
    logger.info(f"Submitting {JOB_COUNT} test jobs...")
    
    for i in range(JOB_COUNT):
        job_id = f"test-job-{uuid.uuid4()}"
        priority = random.randint(0, MAX_PRIORITY)
        job = create_test_job(job_id, priority)
        
        try:
            response = requests.post(
                f"{QUEUE_API_URL}/jobs",
                json=job
            )
            
            if response.status_code == 200:
                logger.info(f"Submitted job {job_id} with priority {priority}")
            else:
                logger.error(f"Failed to submit job {job_id}: {response.text}")
                
        except Exception as e:
            logger.error(f"Error submitting job {job_id}: {str(e)}")
            
        # Wait between submissions
        time.sleep(SUBMISSION_INTERVAL)
    
    logger.info("All jobs submitted successfully")

if __name__ == "__main__":
    submit_jobs()
```

## Test Scenarios

The following test scenarios validate different aspects of the queue system:

### 1. Basic Queue Functionality

**Objective**: Verify that jobs are properly queued and processed in order of priority.

**Setup**:
- Start the queue API and a single worker with 1 mock GPU
- Submit 10 jobs with varying priorities

**Expected Results**:
- Higher priority jobs should be processed first
- All jobs should eventually be processed
- Job status should transition correctly: queued → processing → completed

### 2. Multi-GPU Distribution

**Objective**: Verify that jobs are distributed across multiple GPUs efficiently.

**Setup**:
- Start the queue API and a single worker with 4 mock GPUs
- Submit 20 jobs with the same priority
- Set varying processing times for the mock GPUs

**Expected Results**:
- Jobs should be distributed across all 4 GPUs
- Faster GPUs should process more jobs than slower ones
- All GPUs should be utilized

### 3. Multi-Machine Distribution

**Objective**: Verify that jobs are distributed across multiple machines efficiently.

**Setup**:
- Start the queue API and two workers, each with 2 mock GPUs
- Submit 30 jobs with varying priorities

**Expected Results**:
- Jobs should be distributed across both machines
- Higher priority jobs should be processed first, regardless of machine
- All machines and GPUs should be utilized

### 4. Failure Recovery

**Objective**: Verify that the system can recover from worker failures.

**Setup**:
- Start the queue API and two workers
- Submit 20 jobs
- After 10 jobs are processed, stop one worker

**Expected Results**:
- Remaining worker should continue processing jobs
- When the failed worker is restarted, it should resume taking jobs
- All jobs should eventually be processed

### 5. Load Testing

**Objective**: Verify that the system can handle a high volume of jobs.

**Setup**:
- Start the queue API and multiple workers
- Submit 1000 jobs in rapid succession

**Expected Results**:
- System should remain responsive
- Jobs should be distributed efficiently
- All jobs should eventually be processed

## Monitoring and Analysis

### Redis Monitoring

Use the Redis CLI to monitor queue state in real-time:

```bash
# Connect to Redis
redis-cli

# Monitor queue length
LLEN job_queue
LLEN priority_queue

# View all keys in the database
KEYS *

# Monitor job status
HGETALL job:{job_id}
```

### Performance Analysis

Track these metrics to evaluate system performance:

1. **Average Job Wait Time**: Time between submission and processing start
2. **Average Job Processing Time**: Time between processing start and completion
3. **Queue Length Over Time**: Number of jobs waiting in the queue
4. **GPU Utilization**: Percentage of time each GPU is busy
5. **Job Distribution**: Number of jobs processed by each worker/GPU

### Visualization

Create a simple dashboard using Grafana or a similar tool to visualize:

- Queue length over time
- Job processing rates
- Worker status and load
- Error rates

## Conclusion

By using this testing strategy, you can validate that your Redis-based job queue system properly distributes AI inference tasks across multiple machines and GPUs. The mock testing approach allows you to verify queue logic and job distribution without requiring actual GPU hardware or AI model inference.

The test scenarios cover the essential aspects of the system's functionality, from basic queue operations to failure recovery and load testing. By monitoring key metrics during testing, you can identify potential bottlenecks and optimize the system's performance before deploying to production.
