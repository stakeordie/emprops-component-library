const path = require('path');
const { test, production } = require('./config/monitor.config.cjs');

// Convert milliseconds to seconds and ensure integer
const msToSec = (ms) => Math.floor(ms / 1000);

module.exports = {
  apps: [
    {
      name: 'generator',
      script: 'log_generator.sh',
      interpreter: '/bin/bash',
      args: ['start', 'generator.log', '5'],
      error_file: 'logs/generator-error.log',
      out_file: 'logs/generator-out.log',
      merge_logs: true,
      env: {
        NODE_ENV: 'development',
        PATH: process.env.PATH
      }
    }
  ]
};
