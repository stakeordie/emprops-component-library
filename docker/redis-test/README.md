# Redis Queue Test Environment (WebSocket-based)

This directory contains a complete test environment for the distributed AI job queue system based on Redis and WebSockets. The system provides real-time communication between clients, workers, and the queue API, enabling efficient distribution of AI inference tasks across multiple worker machines.

## Test Environment Components

1. **Redis Server**: Central queue database for job storage and pub/sub messaging
2. **Queue API**: FastAPI service with WebSocket endpoints for queue management
3. **Worker Machines**: Each with configurable simulated GPUs
4. **Job Submitter**: Generates test jobs with varying priorities and types
5. **WebSocket Test Client**: Simple testing utility for WebSocket API interaction

## Running the Tests

### Start the Full Test Environment

```bash
# Build and start all services
docker-compose up -d

# View logs from all services
docker-compose logs -f
```

### View Logs for Specific Components

```bash
# View logs for the queue API
docker-compose logs -f queue-api

# View logs for a specific worker
docker-compose logs -f worker-3
```

### Check API Status and Statistics

```bash
# Check API status
curl http://localhost:8000/

# Get queue statistics
curl http://localhost:8000/stats
```

### Run Individual Components

```bash
# Start just the Redis server and queue API
docker-compose up -d redis queue-api

# Run the job submitter
docker-compose run --rm job-submitter

# Start a worker with custom configuration
docker-compose run --rm -e MACHINE_ID=custom-machine -e MOCK_GPU_COUNT=4 worker-1

# Run the WebSocket test client
python test_websocket_client.py

# Run the WebSocket test client in worker mode
python test_websocket_client.py worker 0
```

### Stop the Test Environment

```bash
docker-compose down
```

## Test Scenarios

This environment supports various test scenarios:

1. **Basic Distribution**: Watch how jobs are distributed across machines
2. **Priority Handling**: Test how higher priority jobs are processed first
3. **Failure Recovery**: Stop/start workers to test recovery
4. **Load Testing**: Increase JOB_COUNT for stress testing
5. **Real-time Updates**: Observe progress updates via WebSockets
6. **Job Type Routing**: Test routing of different job types to appropriate workers
7. **Multiple Clients**: Connect multiple clients simultaneously

## Configuration Options

Each component can be configured through environment variables in the docker-compose.yml file:

### Worker Configuration
- `MACHINE_ID`: Unique identifier for the worker
- `MOCK_GPU_COUNT`: Number of simulated GPUs
- `MIN_PROCESS_TIME`/`MAX_PROCESS_TIME`: Range of processing times in seconds
- `WS_HOST`/`WS_PORT`: WebSocket server host and port
- `PROGRESS_INTERVAL`: How often to send progress updates (seconds)

### Job Submitter Configuration
- `JOB_COUNT`: Number of jobs to submit
- `SUBMISSION_INTERVAL`: Time between job submissions in seconds
- `MAX_PRIORITY`: Maximum priority level for generated jobs
- `RESULT_TIMEOUT`: Max time to wait for job completion (seconds)
- `WS_HOST`/`WS_PORT`: WebSocket server host and port

### Queue API Configuration
- `REDIS_HOST`/`REDIS_PORT`: Redis server connection
- `LOG_LEVEL`: Logging verbosity level

## Monitoring

View the Redis database directly:

```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# View queue lengths
ZCARD priority_queue

# View all jobs
KEYS job:*

# View job details
HGETALL job:<job_id>

# View all workers
KEYS worker:*

# View worker details
HGETALL worker:<worker_id>

# View active channels for pub/sub
PUBSUB CHANNELS job:*
```

## WebSocket API Endpoints

### Client Endpoints
- `ws://localhost:8000/ws/client/{client_id}` - For job submission and status tracking

### Worker Endpoints
- `ws://localhost:8000/ws/worker/{machine_id}/{gpu_id}` - For worker registration and job processing

## Message Types

### Client Messages
- `submit_job` - Submit a new job to the queue
- `get_job_status` - Request status update for a job
- `cancel_job` - Cancel a pending job
- `ping` - Simple ping request

### Worker Messages
- `get_next_job` - Request the next available job
- `update_job_progress` - Send progress updates for a job
- `complete_job` - Mark a job as completed
- `failed_job` - Report job failure

## WebSocket Testing

Use the provided test client to interact with the WebSocket API:

```bash
# Test client connection and job submission
python test_websocket_client.py

# Test worker connection and job processing
python test_websocket_client.py worker 0
```
