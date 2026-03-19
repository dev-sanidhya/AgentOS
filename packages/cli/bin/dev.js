#!/usr/bin/env node

// Development version - runs TypeScript directly with ts-node
const path = require('path');
const project = path.join(__dirname, '..', 'tsconfig.json');

// Register ts-node for development
require('ts-node').register({ project });

// Run the CLI
require('@oclif/core')
  .run(process.argv.slice(2), import.meta.url)
  .then(require('@oclif/core/flush'))
  .catch(require('@oclif/core/handle'));
