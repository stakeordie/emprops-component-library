#!/usr/bin/env python3
"""
Monitor script for the Redis queue test environment.
Provides real-time statistics on job distribution and worker activity.
"""
import os
import time
import redis
import json
import argparse
import curses
from collections import defaultdict

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# Initialize Redis connection
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
)

def get_queue_stats():
    """Get queue statistics"""
    # Get queue lengths
    priority_queue_length = redis_client.zcard("priority_queue")
    standard_queue_length = redis_client.llen("job_queue")
    
    # Get job counts by status
    all_jobs = redis_client.keys("job:*")
    total_jobs = len(all_jobs)
    
    status_counts = defaultdict(int)
    worker_jobs = defaultdict(int)
    machine_jobs = defaultdict(int)
    worker_times = {}
    
    for job_key in all_jobs:
        job_data = redis_client.hgetall(job_key)
        status = job_data.get("status", "unknown")
        worker = job_data.get("worker", "none")
        
        status_counts[status] += 1
        
        if worker != "none" and status == "processing":
            worker_jobs[worker] += 1
            machine_id = worker.split(":")[0]
            machine_jobs[machine_id] += 1
    
    # Get worker start times and status
    all_workers = redis_client.keys("worker:*")
    current_time = time.time()
    
    for worker_key in all_workers:
        worker_data = redis_client.hgetall(worker_key)
        if worker_data and 'start_time' in worker_data:
            worker_id = worker_key.replace('worker:', '')
            start_time = float(worker_data.get('start_time', 0))
            uptime_seconds = current_time - start_time
            worker_times[worker_id] = uptime_seconds
    
    return {
        "queues": {
            "priority": priority_queue_length,
            "standard": standard_queue_length,
            "total": priority_queue_length + standard_queue_length
        },
        "jobs": {
            "total": total_jobs,
            "status": dict(status_counts)
        },
        "workers": dict(worker_jobs),
        "machines": dict(machine_jobs),
        "worker_times": worker_times
    }

def format_uptime(seconds):
    """Format uptime in seconds to human-readable string"""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def display_monitor(stdscr):
    """Display real-time monitoring interface using curses"""
    # Get terminal size to handle resizing
    height, width = stdscr.getmaxyx()
    
    curses.curs_set(0)  # Hide cursor
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    
    GREEN = curses.color_pair(1)
    YELLOW = curses.color_pair(2)
    RED = curses.color_pair(3)
    CYAN = curses.color_pair(4)
    MAGENTA = curses.color_pair(5)
    
    while True:
        try:
            stats = get_queue_stats()
            stdscr.clear()
            
            # Title
            stdscr.addstr(0, 0, "Redis Queue Monitor", curses.A_BOLD)
            stdscr.addstr(1, 0, "=" * 50)
            
            # Queue stats
            stdscr.addstr(3, 0, "Queue Status:", curses.A_BOLD)
            stdscr.addstr(4, 2, f"Priority Queue: {stats['queues']['priority']} jobs")
            stdscr.addstr(5, 2, f"Standard Queue: {stats['queues']['standard']} jobs")
            stdscr.addstr(6, 2, f"Total Queued: {stats['queues']['total']} jobs")
            
            # Job stats
            stdscr.addstr(8, 0, "Job Status:", curses.A_BOLD)
            stdscr.addstr(9, 2, f"Total Jobs: {stats['jobs']['total']}")
            
            row = 10
            for status, count in stats['jobs']['status'].items():
                color = GREEN if status == "completed" else YELLOW if status == "processing" else RED if status == "failed" else 0
                stdscr.addstr(row, 2, f"{status.capitalize()}: {count} jobs", color)
                row += 1
            
            # Machine stats
            stdscr.addstr(row + 1, 0, "Machine Activity:", curses.A_BOLD)
            row += 2
            
            if stats['machines']:
                for machine, count in sorted(stats['machines'].items()):
                    stdscr.addstr(row, 2, f"{machine}: {count} active jobs", CYAN)
                    row += 1
            else:
                stdscr.addstr(row, 2, "No active machines")
            
            # Worker stats
            stdscr.addstr(row + 1, 0, "Worker Activity:", curses.A_BOLD)
            row += 2
            
            # Only attempt to print if there's enough room
            max_display_row = height - 4  # Leave space for update instructions
            
            if stats['workers']:
                for worker, count in sorted(stats['workers'].items()):
                    if row >= max_display_row:
                        break
                        
                    machine_id, gpu_id = worker.split(":")
                    uptime_str = ""
                    
                    # Add uptime information if available
                    if worker in stats['worker_times']:
                        uptime = stats['worker_times'][worker]
                        uptime_str = f" - uptime: {format_uptime(uptime)}"
                    
                    worker_line = f"{machine_id} (GPU {gpu_id}): {count} active jobs{uptime_str}"
                    
                    # Make sure the line fits within the width of the screen
                    if len(worker_line) > width - 3:
                        worker_line = worker_line[:width - 6] + "..."
                        
                    try:
                        stdscr.addstr(row, 2, worker_line, CYAN)
                        row += 1
                    except curses.error:
                        # Skip this line if an error occurs
                        pass
            elif stats['worker_times']:
                # Show idle workers with uptime
                for worker, uptime in sorted(stats['worker_times'].items()):
                    if row >= max_display_row:
                        break
                        
                    machine_id, gpu_id = worker.split(":")
                    worker_line = f"{machine_id} (GPU {gpu_id}): idle - uptime: {format_uptime(uptime)}"
                    
                    # Make sure the line fits within the width of the screen
                    if len(worker_line) > width - 3:
                        worker_line = worker_line[:width - 6] + "..."
                        
                    try:
                        stdscr.addstr(row, 2, worker_line, MAGENTA)
                        row += 1
                    except curses.error:
                        # Skip this line if an error occurs
                        pass
            else:
                try:
                    stdscr.addstr(row, 2, "No active workers")
                except curses.error:
                    pass
            
            # Make sure there's enough room for the instructions
            if row + 2 < height - 1:
                try:
                    # Update instructions
                    stdscr.addstr(row + 2, 0, "Press 'q' to quit, any other key to refresh")
                except curses.error:
                    pass
            
            # Refresh and wait for input with timeout
            stdscr.refresh()
            stdscr.timeout(1000)  # Refresh every second
            key = stdscr.getch()
            
            if key == ord('q'):
                break
                
        except redis.RedisError as e:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Redis Error: {str(e)}", RED)
            stdscr.addstr(2, 0, "Trying to reconnect...")
            stdscr.refresh()
            time.sleep(2)
            
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Error: {str(e)}", RED)
            stdscr.refresh()
            time.sleep(2)

def main():
    parser = argparse.ArgumentParser(description="Monitor the Redis queue test environment")
    parser.add_argument("--host", default=REDIS_HOST, help="Redis host")
    parser.add_argument("--port", type=int, default=REDIS_PORT, help="Redis port")
    args = parser.parse_args()
    
    # Update Redis connection parameters
    redis_client.connection_pool.disconnect()
    redis_client.connection_pool = redis.ConnectionPool(
        host=args.host,
        port=args.port,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True
    )
    
    try:
        curses.wrapper(display_monitor)
    except KeyboardInterrupt:
        print("Monitor stopped.")

if __name__ == "__main__":
    main()
