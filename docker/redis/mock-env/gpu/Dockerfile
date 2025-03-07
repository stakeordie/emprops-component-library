FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn websockets aiohttp redis

# Copy the GPU service files
COPY ./mock-env/gpu /app/

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

# Add debugging to show directory contents
RUN echo "GPU container setup" && \
    echo "Contents of /app:" && ls -la /app && \
    echo "Contents of /app/core:" && ls -la /app/core && \
    echo "Python version:" && python --version && \
    echo "Python path:" && python -c "import sys; print(sys.path)"

# Add command that will run during container startup to show debugging info
CMD ["bash", "-c", "echo 'Directory contents:' && ls -la /app && echo '/app/core contents:' && ls -la /app/core && python -c 'import sys; print(\"Python path:\", sys.path)' && tail -f /dev/null"]

# No entrypoint - using direct commands in docker-compose.yml instead
