#!/usr/bin/env node 
 
async function main() { 
  const { execute } = await import('@oclif/core'); 
  const path = require('path'); 
  await execute({ development: false, dir: path.resolve(__dirname, '..') }); 
} 
 
main(); 
