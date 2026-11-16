const fs = require('fs');
const path = require('path');

console.log('--- Running Catalyst Slate & Web Dashboard Build ---');

const rootDir = __dirname;
const indexHtmlPath = path.join(rootDir, 'index.html');

if (!fs.existsSync(indexHtmlPath)) {
  console.error('Error: index.html not found at root!');
  process.exit(1);
}

const targetDirs = [
  path.join(rootDir, 'dist'),
  path.join(rootDir, 'build'),
  path.join(rootDir, 'public'),
  path.join(rootDir, 'frontend', 'dist')
];

targetDirs.forEach((dir) => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`Created directory: ${path.relative(rootDir, dir)}`);
  }
  const dest = path.join(dir, 'index.html');
  fs.copyFileSync(indexHtmlPath, dest);
  console.log(`Copied index.html -> ${path.relative(rootDir, dest)}`);
});

console.log('--- Build Finished Successfully ---');
