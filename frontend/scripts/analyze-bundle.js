#!/usr/bin/env node

/**
 * Bundle Analysis Script
 *
 * Usage:
 *   node scripts/analyze-bundle.js          # Analyze and open report
 *   node scripts/analyze-bundle.js --json   # Output JSON metrics
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const isJson = process.argv.includes('--json');

// Run Next.js build with analyzer
console.log('Building with bundle analyzer...');
execSync('cross-env ANALYZE=true next build', {
  stdio: isJson ? 'pipe' : 'inherit',
  env: { ...process.env, ANALYZE: 'true' },
});

// Collect build metrics
const buildDir = path.join(__dirname, '..', '.next');
const buildManifest = path.join(buildDir, 'build-manifest.json');

if (fs.existsSync(buildManifest)) {
  const manifest = JSON.parse(fs.readFileSync(buildManifest, 'utf8'));
  const pages = Object.keys(manifest.pages);

  const metrics = {
    timestamp: new Date().toISOString(),
    totalPages: pages.length,
    pages: pages.map((page) => ({
      route: page,
      chunks: manifest.pages[page]?.length ?? 0,
    })),
  };

  if (isJson) {
    console.log(JSON.stringify(metrics, null, 2));
  } else {
    console.log(`\nTotal pages: ${metrics.totalPages}`);
  }
}
