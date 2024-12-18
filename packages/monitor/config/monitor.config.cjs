const path = require('path');

const baseConfig = {
  paths: {
    logsDir: path.join(__dirname, '..', 'logs'),
    logs: {
      generator: 'generator.log',
      monitor: 'monitor.log'
    }
  },
  timing: {
    generatorInterval: 5000,  // 5 seconds
    monitorInterval: 30000    // 30 seconds
  }
};

module.exports = {
  test: {
    ...baseConfig,
    env: 'test'
  },
  production: {
    ...baseConfig,
    env: 'production'
  }
};
