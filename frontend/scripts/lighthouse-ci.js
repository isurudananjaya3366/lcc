#!/usr/bin/env node

/**
 * Lighthouse CI Runner Script
 *
 * Usage: node scripts/lighthouse-ci.js
 * Requires: npm install -D @lhci/cli
 */

const { execSync } = require('child_process');
const path = require('path');

const configPath = path.join(__dirname, '..', '.lighthouserc.js');

console.log('Running Lighthouse CI...');
console.log('Config:', configPath);

try {
  execSync(`npx @lhci/cli autorun --config=${configPath}`, {
    stdio: 'inherit',
    cwd: path.join(__dirname, '..'),
  });
  console.log('\n✅ Lighthouse CI completed successfully.');
} catch (error) {
  console.error('\n❌ Lighthouse CI failed. Check the report above for details.');
  process.exit(1);
}
