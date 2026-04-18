#!/usr/bin/env node

/**
 * Surface FRU Selector - Startup Verification Script
 * Verifies all required files and configuration for the application to run
 */

const fs = require('fs');
const path = require('path');

const requiredFiles = [
  'package.json',
  'dist/main/index.js',
  'build/index.html',
  'src/App.tsx',
  'src/index.tsx',
  'src/shared/types.ts',
  'src/shared/data.ts',
  'src/main/index.ts',
  'src/components/FamilySelector.tsx',
  'src/components/ModelSelector.tsx',
  'src/components/VariantSelector.tsx',
  'src/components/SKUDisplay.tsx',
  'README.md',
  '.github/copilot-instructions.md',
];

const projectRoot = __dirname;
let allGood = true;

console.log('Surface FRU Selector - Startup Verification\n');
console.log('Checking required files...\n');

requiredFiles.forEach(file => {
  const filePath = path.join(projectRoot, file);
  const exists = fs.existsSync(filePath);
  const status = exists ? '✓' : '✗';
  console.log(`${status} ${file}`);
  if (!exists) allGood = false;
});

console.log('\n' + (allGood ? '✓ All files present!' : '✗ Some files missing!'));
console.log('\nTo start the application:');
console.log('  npm run dev       - Start development with hot reload');
console.log('  npm run build     - Build for production');
console.log('  npm start         - Launch the built application\n');

process.exit(allGood ? 0 : 1);
