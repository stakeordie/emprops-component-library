# EmProps Redis Queue Mock Environment

This directory contains a Docker Compose setup that mimics the physical distributed architecture of the EmProps system. It's designed for testing the push-based Redis queue notification system and distributed job processing.

## Architecture

The mock environment consists of:

1. **API Container** - Frontend HTTP API for client interactions
   - Handles job submissions and status inquiries
   - Provides real-time WebSocket updates to clients

2. **Hub Container** - Combined Redis API and Redis Database
   - Manages the job queue and worker registry
   - Implements push-based job notifications
   - Handles atomic job claiming

3. **GPU Containers** - 5 simulated GPU machines with variable worker counts
   - GPU1: 4 workers
   - GPU2: 4 workers
   - GPU3: 1 worker
   - GPU4: 1 worker
   - GPU5: 2 workers

4. **Execution Service** - Separate service on each GPU container
   - Simulates actual job processing
   - Provides realistic progress updates
   - Occasionally simulates random failures

## Getting Started

### Starting the Environment

```bash
cd docker/redis/mock-env
docker-compose up --build
```

This will start all containers and set up the network between them.

### Submitting Jobs

You can submit jobs to the API using HTTP requests:

```bash
# Submit a sample image generation job
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "image_generation",
    "priority": 5,
    "params": {
      "prompt": "A beautiful landscape with mountains",
      "width": 512,
      "height": 512,
      "steps": 20
    }
  }'
```

### Monitoring Jobs

You can monitor job status through the API:

```bash
# Check job status
curl http://localhost:8000/jobs/{job_id}

# Get system stats
curl http://localhost:8000/stats
```

### Real-time Updates via WebSocket

Connect to the WebSocket endpoint to receive real-time updates:

```
ws://localhost:8000/ws/client/{client_id}
```

## System Behavior

1. When a job is submitted, it's added to the Redis queue
2. The system notifies idle workers about the available job
3. Workers can claim the job (with atomic transactions to prevent conflicts)
4. The claiming worker connects to its local execution service to process the job
5. The execution service simulates job processing with progress updates
6. Final job results are sent back through the worker to update the job status

## Monitoring Tools

You can monitor the execution services on each GPU container:

- GPU1: http://localhost:9001/stats
- GPU2: http://localhost:9002/stats
- GPU3: http://localhost:9003/stats
- GPU4: http://localhost:9004/stats
- GPU5: http://localhost:9005/stats

## Customizing the Environment

You can adjust worker counts and capabilities by modifying the environment variables in the `docker-compose.yml` file.

## Troubleshooting

If a container fails to start, check the logs:

```bash
docker-compose logs [service-name]
```

Where `[service-name]` is one of: api, hub, gpu1, gpu2, gpu3, gpu4, or gpu5.
