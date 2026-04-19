#!/usr/bin/env node

/**
 * Collect build metrics for performance tracking.
 */

const fs = require('fs');
const path = require('path');

const NEXT_DIR = path.join(__dirname, '..', '.next');

function collectMetrics() {
  const metrics = {
    timestamp: new Date().toISOString(),
    buildId: getBuildId(),
    pages: getPageMetrics(),
    chunks: getChunkMetrics(),
  };

  const outputPath = path.join(__dirname, '..', 'build-metrics.json');
  fs.writeFileSync(outputPath, JSON.stringify(metrics, null, 2));
  console.log(`Metrics written to ${outputPath}`);
  return metrics;
}

function getBuildId() {
  const idFile = path.join(NEXT_DIR, 'BUILD_ID');
  return fs.existsSync(idFile) ? fs.readFileSync(idFile, 'utf8').trim() : 'unknown';
}

function getPageMetrics() {
  const manifest = path.join(NEXT_DIR, 'build-manifest.json');
  if (!fs.existsSync(manifest)) return [];

  const data = JSON.parse(fs.readFileSync(manifest, 'utf8'));
  return Object.entries(data.pages).map(([route, chunks]) => ({
    route,
    chunkCount: Array.isArray(chunks) ? chunks.length : 0,
  }));
}

function getChunkMetrics() {
  const staticDir = path.join(NEXT_DIR, 'static', 'chunks');
  if (!fs.existsSync(staticDir)) return { total: 0, files: [] };

  const files = fs.readdirSync(staticDir).filter((f) => f.endsWith('.js'));
  const details = files.map((file) => {
    const stats = fs.statSync(path.join(staticDir, file));
    return { file, sizeKB: Math.round(stats.size / 1024) };
  });

  return {
    total: details.reduce((sum, f) => sum + f.sizeKB, 0),
    files: details.sort((a, b) => b.sizeKB - a.sizeKB).slice(0, 20),
  };
}

collectMetrics();
