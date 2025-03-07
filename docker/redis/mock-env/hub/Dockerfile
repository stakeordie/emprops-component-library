FROM python:3.9-slim

WORKDIR /app

# Install Redis and Python dependencies
RUN apt-get update && \
    apt-get install -y redis-server && \
    pip install --no-cache-dir fastapi uvicorn websockets aioredis redis

# Copy the hub service files
COPY ./mock-env/hub /app/

# Create core directory
RUN mkdir -p /app/core

# Manually copy each core module file
COPY ./core/__init__.py /app/core/
COPY ./core/models.py /app/core/
COPY ./core/connections.py /app/core/
COPY ./core/redis_service.py /app/core/
COPY ./core/main.py /app/core/
COPY ./core/routes.py /app/core/

# Create empty __init__.py if it doesn't exist (important for Python modules)
RUN touch /app/core/__init__.py

# Redis will listen on default port 6379
EXPOSE 6379 8001

# Add debugging to show directory contents
RUN echo "HUB container setup" && \
    echo "Contents of /app:" && ls -la /app && \
    echo "Contents of /app/core:" && ls -la /app/core && \
    echo "Python version:" && python --version && \
    echo "Python path:" && python -c "import sys; print(sys.path)"

# Start Redis server and FastAPI application
CMD ["bash", "-c", "redis-server --daemonize yes && echo 'Directory contents:' && ls -la /app && echo '/app/core contents:' && ls -la /app/core && echo 'Python path:' && python -c 'import sys; print(sys.path)' && uvicorn main:app --host 0.0.0.0 --port 8001 --reload"]
