#!/bin/bash
# Start script for GPU container

# Start execution service
echo "Starting execution service on port $EXECUTION_SERVICE_PORT..."
python execution_service.py &

# Start workers based on NUM_WORKERS environment variable
echo "Starting $NUM_WORKERS workers..."
for ((i=1; i<=$NUM_WORKERS; i++))
do
  echo "Starting worker $i..."
  python worker.py --worker-id "${MACHINE_ID}-worker-$i" &
done

# Keep container running
tail -f /dev/null
