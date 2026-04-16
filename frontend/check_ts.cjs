const { spawnSync } = require('child_process');
const r = spawnSync('node', ['node_modules/typescript/bin/tsc', '--noEmit', '--pretty', 'false'], {
  encoding: 'utf8',
  maxBuffer: 10 * 1024 * 1024,
});
const out = (r.stdout || '') + (r.stderr || '');
const lines = out.split('\n').filter((l) => l.includes('error TS'));
process.stdout.write('Total errors: ' + lines.length + '\n');
lines.forEach((l) => process.stdout.write(l + '\n'));
