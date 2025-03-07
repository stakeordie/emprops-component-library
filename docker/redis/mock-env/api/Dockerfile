FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn websockets requests aiohttp redis

# Copy the API files
COPY ./mock-env/api /app/

# Create static directory
RUN mkdir -p /app/static

# Copy sequence monitor HTML file
COPY ./mock-env/api/static/sequence-monitor.html /app/static/

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

# We'll create the debug UI file from within the container

EXPOSE 8000

# Add debugging to show directory contents
RUN echo "API container setup" && \
    echo "Contents of /app:" && ls -la /app && \
    echo "Contents of /app/core:" && ls -la /app/core && \
    echo "Python version:" && python --version && \
    echo "Python path:" && python -c "import sys; print(sys.path)"

# Show directory contents when starting container for debugging
CMD ["bash", "-c", "echo 'Directory contents:' && ls -la /app && echo '/app/core contents:' && ls -la /app/core && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
