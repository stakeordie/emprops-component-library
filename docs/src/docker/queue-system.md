# AI Request Queue System

This page describes different approaches to orchestrating requests between ComfyUI and A1111 Stable Diffusion WebUI in the hybrid container setup, with a focus on preventing simultaneous GPU usage.

## Overview

When running both ComfyUI and A1111 on the same GPU, it's important to ensure that only one service processes a request at a time. This prevents GPU memory conflicts and ensures more stable operation.

## NGINX-Based Request Limiting (Recommended)

The simplest and most lightweight approach uses NGINX's built-in rate limiting and connection control features to manage request flow.

```mermaid
flowchart TD
    Client1[Client 1] -->|Request 1| NGINX
    Client2[Client 2] -->|Request 2| NGINX
    Client3[Client 3] -->|Request 3| NGINX
    
    subgraph "NGINX with Connection Limiting"
        NGINX -->|limit_conn zone=ai_proc_limit:10m| ConnectionQueue[Connection Queue]
        ConnectionQueue -->|"One at a time"| Router
    end
    
    Router -->|Request for ComfyUI| ComfyUI
    Router -->|Request for A1111| A1111
    
    subgraph "Shared GPU"
        ComfyUI -->|Uses| GPU[GPU Memory]
        A1111 -->|Uses| GPU
    end
    
    ComfyUI -->|Response| NGINX
    A1111 -->|Response| NGINX
    
    NGINX -->|Response 1| Client1
    NGINX -->|Response 2| Client2
    NGINX -->|Response 3| Client3
```

### Implementation

In your NGINX configuration:

```nginx
# Define a shared memory zone for limiting connections
limit_conn_zone $binary_remote_addr zone=ai_proc_limit:10m;

# Server block for AI services
server {
    listen 80;
    server_name example.com;
    
    # Apply connection limit
    limit_conn ai_proc_limit 1;  
    limit_conn_status 429;       # Return 429 when limit reached
    
    # Comfy location
    location /comfy/ {
        proxy_pass http://localhost:3188/;
        # other proxy settings...
    }
    
    # A1111 location
    location /sd/ {
        proxy_pass http://localhost:3130/;
        # other proxy settings...
    }
}
```

### Request Flow Sequence

```mermaid
sequenceDiagram
    participant Client1 as Client 1
    participant Client2 as Client 2
    participant NGINX
    participant ComfyUI
    participant A1111
    
    Client1->>NGINX: Request to ComfyUI
    NGINX->>NGINX: Check connection limit
    Note over NGINX: Limit not reached
    NGINX->>ComfyUI: Forward request
    
    Client2->>NGINX: Request to A1111
    NGINX->>NGINX: Check connection limit
    Note over NGINX: Limit reached, queue request
    
    ComfyUI-->>NGINX: Processing complete
    NGINX-->>Client1: Return response
    
    NGINX->>NGINX: Check connection limit
    Note over NGINX: Limit not reached
    NGINX->>A1111: Forward queued request
    
    A1111-->>NGINX: Processing complete
    NGINX-->>Client2: Return response
```

## Alternative: Redis-Based Queue System

For more complex scenarios, a Redis-based queue system offers more control and visibility.

```mermaid
flowchart TD
    Client1[Client 1] -->|Request 1| APIGateway
    Client2[Client 2] -->|Request 2| APIGateway
    Client3[Client 3] -->|Request 3| APIGateway
    
    subgraph "Request Orchestration"
        APIGateway -->|Enqueue| Redis[(Redis Queue)]
        QueueWorker -->|Dequeue one at a time| Redis
        QueueWorker -->|Route request| ServiceRouter
    end
    
    ServiceRouter -->|ComfyUI request| ComfyUI
    ServiceRouter -->|A1111 request| A1111
    
    ComfyUI -->|Result| QueueWorker
    A1111 -->|Result| QueueWorker
    
    QueueWorker -->|Response| APIGateway
    
    APIGateway -->|Response 1| Client1
    APIGateway -->|Response 2| Client2
    APIGateway -->|Response 3| Client3
```

## Alternative: File-Based Semaphore

A simple file-based semaphore approach that requires minimal additional components.

```mermaid
flowchart TD
    Client1[Client 1] -->|Request to ComfyUI| ComfyUI
    Client2[Client 2] -->|Request to A1111| A1111
    
    subgraph "Semaphore Coordination"
        ComfyUI -->|Try to acquire| Semaphore["/tmp/gpu.lock"]
        A1111 -->|Try to acquire| Semaphore
        
        Semaphore -->|Granted| ComfyUI
        Semaphore -.->|Blocked| A1111
        
        ComfyUI -->|Release when done| Semaphore
        Semaphore -->|Now granted| A1111
    end
    
    ComfyUI -->|Response| Client1
    A1111 -->|Response| Client2
```

## Comparison of Approaches

| Approach | Complexity | Dependencies | Maintenance | Scalability |
|----------|------------|--------------|------------|-------------|
| NGINX Connection Limiting | Low | None (using existing NGINX) | Minimal | Good |
| Redis Queue | Medium | Redis | Moderate | Excellent |
| File Semaphore | Low | None | Low | Limited |

## Implementation

To implement the recommended NGINX approach:

1. Update NGINX configuration to include connection limiting
2. Set appropriate timeout values
3. Restart NGINX to apply changes

### Optional Configuration

Adjust request timeout settings to accommodate longer-running jobs:

```nginx
# Longer timeouts for AI generation
proxy_read_timeout 300s;
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
```

## Multi-GPU Considerations

When using multiple GPUs, you can either:

1. Apply connection limiting per GPU
2. Allow one request per GPU simultaneously

```mermaid
flowchart TD
    Client -->|Request| NGINX
    
    NGINX -->|GPU 0 request| GPUZeroLimit[GPU 0 Limit]
    NGINX -->|GPU 1 request| GPUOneLimit[GPU 1 Limit]
    
    GPUZeroLimit -->|Forward| ComfyUI_GPU0[ComfyUI on GPU 0]
    GPUOneLimit -->|Forward| A1111_GPU1[A1111 on GPU 1]
    
    ComfyUI_GPU0 -->|Response| NGINX
    A1111_GPU1 -->|Response| NGINX
    
    NGINX -->|Response| Client
```

## Large-Scale Multi-Machine Architecture

For large deployments with multiple machines and many GPUs (e.g., 30 GPUs across several machines), a hierarchical architecture provides the best combination of performance and control.

### Queuing vs. Load Balancing

In a distributed architecture, we need to distinguish between:

- **Load Balancing**: Distributing requests across available resources
- **Request Queuing**: Ensuring requests don't exceed processing capacity

These happen at different levels in the architecture:

```mermaid
flowchart TD
    Client -->|Request| GlobalLB[Global Load Balancer]
    
    subgraph "Load Balancing Layer"
        GlobalLB -->|Distribution| Machine1[Machine 1]
        GlobalLB -->|Distribution| Machine2[Machine 2]
        GlobalLB -->|Distribution| Machine3[Machine 3]
        GlobalLB -->|Distribution| MachineN[Individual Machines...]
    end
    
    subgraph "Queuing Layer (Machine 1)"
        Machine1 -->|Local Queuing| M1GPU1Q[GPU 1 Queue]
        Machine1 -->|Local Queuing| M1GPU2Q[GPU 2 Queue]
        Machine1 -->|Local Queuing| M1GPU8Q[GPU 8 Queue]
    end
    
    subgraph "Processing Layer (Machine 1)"
        M1GPU1Q -->|Single Request| M1GPU1[GPU 1 Processing]
        M1GPU2Q -->|Single Request| M1GPU2[GPU 2 Processing]
        M1GPU8Q -->|Single Request| M1GPU8[GPU 8 Processing]
    end
```

### Detailed Architecture for 30 GPUs

This architecture works for our specific scenario of 30 GPUs across multiple machines (3 machines with 8 GPUs each, plus 6 individual machines).

```mermaid
flowchart TD
    Client -->|Request| CentralLB[Central Load Balancer]
    
    subgraph "Load Balancing"
        CentralLB -->|Route by availability| Cluster1[Cluster 1 - 8 GPUs]
        CentralLB -->|Route by availability| Cluster2[Cluster 2 - 8 GPUs]
        CentralLB -->|Route by availability| Cluster3[Cluster 3 - 8 GPUs]
        CentralLB -->|Route by availability| IndividualMachines[6 Individual Machines]
    end
    
    subgraph "Cluster 1 - Internal Queuing"
        Cluster1 -->|Internal Queue| C1_GPUQueues[8 GPU-Specific Queues]
        C1_GPUQueues -->|1:1 Mapping| C1_GPUs[8 GPU Processors]
    end
    
    subgraph "Individual Machine Queuing"
        IndividualMachines -->|Per Machine Queue| IM_Queues[6 Machine Queues]
        IM_Queues -->|1:1 Mapping| IM_GPUs[6 GPU Processors]
    end
    
    C1_GPUs -->|Responses| CentralLB
    IM_GPUs -->|Responses| CentralLB
    CentralLB -->|Response| Client
```

### Request Flow Sequence

Here's how requests flow through this system:

```mermaid
sequenceDiagram
    participant Client
    participant CentralLB as Central Load Balancer
    participant ClusterLB as Machine Cluster Load Balancer
    participant GPUQueue as GPU-Specific Queue
    participant GPU as GPU Processor
    
    Client->>CentralLB: Send request
    CentralLB->>CentralLB: Determine least loaded machine
    CentralLB->>ClusterLB: Forward to selected machine
    
    ClusterLB->>ClusterLB: Check GPU availability
    ClusterLB->>GPUQueue: Place in queue for selected GPU
    
    Note over GPUQueue: Request waits if GPU busy
    
    GPUQueue->>GPU: Forward when GPU available
    GPU->>GPU: Process request (A1111 or ComfyUI)
    GPU->>ClusterLB: Return result
    ClusterLB->>CentralLB: Forward result
    CentralLB->>Client: Deliver response
```

### Implementation Details

#### Central Load Balancer Configuration

```nginx
# Central Load Balancer NGINX config

# Define machine upstreams
upstream machine1_cluster {
    server machine1.example.com:80 weight=8;  # Weight by number of GPUs
}

upstream machine2_cluster {
    server machine2.example.com:80 weight=8;
}

upstream machine3_cluster {
    server machine3.example.com:80 weight=8;
}

upstream individual_machines {
    server individual1.example.com:80 weight=1;
    server individual2.example.com:80 weight=1;
    # ... and so on for all individual machines
}

# Combined upstream with all machines
upstream all_ai_services {
    server machine1.example.com:80 weight=8;
    server machine2.example.com:80 weight=8;
    server machine3.example.com:80 weight=8;
    server individual1.example.com:80 weight=1;
    # ... etc for all individual machines
}

server {
    listen 80;
    server_name ai-central.example.com;
    
    # Simple round-robin load balancing
    location / {
        proxy_pass http://all_ai_services;
        proxy_next_upstream error timeout http_502;
        # Additional proxy settings...
    }
}
```

#### Machine-Level Load Balancer Configuration

```nginx
# Machine-Level NGINX (e.g., on machine1 with 8 GPUs)

# Define per-GPU services
upstream gpu0_services {
    server 127.0.0.1:3188;  # ComfyUI on GPU 0
    server 127.0.0.1:3130;  # A1111 on GPU 0
}

upstream gpu1_services {
    server 127.0.0.1:3189;  # ComfyUI on GPU 1
    server 127.0.0.1:3131;  # A1111 on GPU 1
}

# ... repeat for all 8 GPUs

# Create connection limiting zones for each GPU
limit_conn_zone $binary_remote_addr zone=gpu0_limit:10m;
limit_conn_zone $binary_remote_addr zone=gpu1_limit:10m;
# ... repeat for all GPUs

server {
    listen 80;
    
    # GPU 0 services
    location /gpu0/ {
        limit_conn gpu0_limit 1;  # This is where queuing happens!
        proxy_pass http://gpu0_services;
    }
    
    # GPU 1 services
    location /gpu1/ {
        limit_conn gpu1_limit 1;  # Queue requests for GPU 1
        proxy_pass http://gpu1_services;
    }
    
    # ... repeat for all GPUs
}
```

### Key Benefits of This Architecture

1. **Separation of Concerns**:
   - Load balancing happens at the central level (distributing across machines)
   - Queuing happens at the machine level (managing GPU-specific request flow)

2. **Horizontal Scalability**:
   - Add new machines to the central load balancer without reconfiguring existing machines
   - Each machine manages its own GPU resources independently

3. **Fault Tolerance**:
   - If a machine fails, the central load balancer routes traffic to other machines
   - Each machine can operate independently even if the central load balancer is temporarily unavailable

4. **Resource Optimization**:
   - Requests are queued only at the GPU level, ensuring max utilization
   - Load balancing ensures even distribution across all available machines
