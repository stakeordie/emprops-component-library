# Monitor System

This directory contains the monitoring system for the Comfy middleware service. It includes a test log generator and a monitoring service that watches for stalled or failed generations.

## Directory Structure

```
monitor/
├── README.md                # This file
├── log_generator.sh         # Test log generator script
├── monitor_service.sh       # Monitor service script
├── generator.mode           # Current mode of the test generator
├── config/                  # Configuration directory
│   ├── monitor.config.js    # Base configuration
│   ├── monitor.test.config.js    # Test environment config
│   ├── monitor.prod.config.js    # Production environment config
│   ├── monitor-process.test.config.js  # PM2 test config
│   └── monitor-process.prod.config.js  # PM2 production config
└── logs/                    # Log files directory
    ├── generator.log        # Test generator output
    └── monitor.log         # Monitor service logs
```

## Configuration

The configuration is split into several files for better organization and environment separation:

- `monitor.config.js`: Base configuration shared between environments
- `monitor.test.config.js`: Test-specific configuration, includes log generator
- `monitor.prod.config.js`: Production configuration
- `monitor-process.test.config.js`: PM2 test environment setup
- `monitor-process.prod.config.js`: PM2 production environment setup

## Usage

### Test Environment

The test environment includes both the monitor and a log generator for testing:

1. Start the test system:
```bash
pm2 start scripts/monitor/config/monitor-process.test.config.js
```

2. Change generator modes:
```bash
# Switch to normal mode
pkill -SIGUSR1 -f log_generator.sh

# Switch to stalled mode
pkill -SIGUSR2 -f log_generator.sh

# Switch to concurrent mode
pkill -HUP -f log_generator.sh
```

### Production Environment

The production environment runs only the monitor service:

```bash
pm2 start scripts/monitor/config/monitor-process.prod.config.js
```

### Common Commands

```bash
# View logs
pm2 logs                    # All logs
pm2 logs comfy-monitor-test # Test monitor logs
pm2 logs comfy-monitor-prod # Production monitor logs

# Stop services
pm2 delete all             # Stop all services
```

## Configuration Settings

### Base Configuration (`monitor.config.js`)
- `timing.monitorTimeout`: Time before considering service stalled (default: 30 seconds)
- `paths.logs.*`: Log file locations
- `services.*`: Base service names
- `pm2.*`: Base PM2 configurations

### Test Configuration (`monitor.test.config.js`)
Includes all base configuration plus:
- `timing.generatorInterval`: Time between test generations
- `paths.modeFile`: Location of generator mode file
- Log generator PM2 configuration

### Production Configuration (`monitor.prod.config.js`)
Includes base configuration with production-specific:
- Service names
- Environment variables
- No test generator

## Logs

All logs are stored in the `logs/` directory:
- `generator.log`: Test generator output (test environment only)
- `monitor.log`: Monitor service activity and status updates
