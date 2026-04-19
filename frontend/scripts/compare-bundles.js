#!/usr/bin/env node

/**
 * Compare two build-metrics.json files to detect regressions.
 *
 * Usage: node scripts/compare-bundles.js baseline.json current.json
 */

const fs = require('fs');

const [, , baselinePath, currentPath] = process.argv;

if (!baselinePath || !currentPath) {
  console.error('Usage: node compare-bundles.js <baseline.json> <current.json>');
  process.exit(1);
}

const baseline = JSON.parse(fs.readFileSync(baselinePath, 'utf8'));
const current = JSON.parse(fs.readFileSync(currentPath, 'utf8'));

const baselineTotal = baseline.chunks?.total ?? 0;
const currentTotal = current.chunks?.total ?? 0;
const diff = currentTotal - baselineTotal;
const pct = baselineTotal > 0 ? ((diff / baselineTotal) * 100).toFixed(1) : '0.0';

console.log('=== Bundle Size Comparison ===');
console.log(`Baseline: ${baselineTotal}KB`);
console.log(`Current:  ${currentTotal}KB`);
console.log(`Diff:     ${diff > 0 ? '+' : ''}${diff}KB (${diff > 0 ? '+' : ''}${pct}%)`);

if (diff > 50) {
  console.warn('\n⚠️  Bundle size increased by more than 50KB!');
  process.exit(1);
}

console.log('\n✅ Bundle size within acceptable range.');
