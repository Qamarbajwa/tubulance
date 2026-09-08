import { createHash } from 'node:crypto';
import { readFileSync, readdirSync, lstatSync } from 'node:fs';
import { resolve, join, relative, isAbsolute, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

export function verifyPackage(root) {
  root = resolve(root);
  const manifest = JSON.parse(readFileSync(join(root, 'MANIFEST.sha256.json'), 'utf8'));
  if (manifest.version !== '4.0.3' || manifest.algorithm !== 'SHA-256' ||
      !Array.isArray(manifest.files) || manifest.files.length === 0) {
    throw new Error('Invalid package manifest');
  }
  const expected = new Set();
  for (const entry of manifest.files) {
    const name = entry.path;
    if (typeof name !== 'string' || !name || name.includes('\\') ||
        name.includes(':') || isAbsolute(name) || name.split('/').some(p => !p || p === '.' || p === '..') ||
        name === 'MANIFEST.sha256.json' || expected.has(name.toLowerCase()) ||
        !/^[a-f0-9]{64}$/i.test(entry.sha256 ?? '')) throw new Error('Unsafe or duplicate manifest entry');
    expected.add(name.toLowerCase());
    let cursor = root;
    for (const part of name.split('/')) {
      cursor = join(cursor, part);
      if (lstatSync(cursor).isSymbolicLink()) throw new Error('Symlink not allowed');
    }
    if (!lstatSync(cursor).isFile()) throw new Error('Not a regular file');
    const digest = createHash('sha256').update(readFileSync(cursor)).digest('hex');
    if (digest !== entry.sha256.toLowerCase()) throw new Error(`Hash mismatch: ${name}`);
  }
  function walk(folder) {
    for (const item of readdirSync(folder, { withFileTypes: true })) {
      const target = join(folder, item.name);
      if (item.isSymbolicLink()) throw new Error('Symlink not allowed');
      if (item.isDirectory()) walk(target);
      else {
        const name = relative(root, target).split('\\').join('/');
        if (name !== 'MANIFEST.sha256.json' && !expected.has(name.toLowerCase())) {
          throw new Error(`Unlisted file: ${name}`);
        }
      }
    }
  }
  walk(root);
  return manifest.files.length;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const count = verifyPackage(process.argv[2] ?? resolve(dirname(fileURLToPath(import.meta.url)), '..'));
    console.log(`INTEGRITY PASS: ${count} files. Not project acceptance or authenticity proof.`);
  } catch (error) {
    console.error(`INTEGRITY FAIL: ${error.message}`);
    process.exitCode = 1;
  }
}
