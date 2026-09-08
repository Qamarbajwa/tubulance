import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { verifyPackage } from './verify-package.mjs';

// Generated disposable fixtures are retained, not recursively cleaned up.
function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'governance-v403-integrity-'));
  const manifest = {version:'4.0.3', algorithm:'SHA-256', files:[{
    path:'sample.md', sha256:createHash('sha256').update('sample').digest('hex')
  }]};
  writeFileSync(join(root, 'sample.md'), 'sample');
  const save = () => writeFileSync(join(root, 'MANIFEST.sha256.json'), JSON.stringify(manifest));
  save();
  return {root, manifest, save};
}
test('valid package', () => { const f=fixture(); assert.equal(verifyPackage(f.root),1); });
test('reject changed bytes', () => { const f=fixture(); writeFileSync(join(f.root,'sample.md'),'changed'); assert.throws(()=>verifyPackage(f.root),/Hash mismatch/); });
test('reject unlisted files', () => { const f=fixture(); writeFileSync(join(f.root,'extra.md'),'extra'); assert.throws(()=>verifyPackage(f.root),/Unlisted/); });
test('reject parent traversal', () => { const f=fixture(); f.manifest.files[0].path='../sample.md'; f.save(); assert.throws(()=>verifyPackage(f.root),/Unsafe/); });
test('reject case-insensitive duplicate paths', () => { const f=fixture(); f.manifest.files.push({...f.manifest.files[0],path:'SAMPLE.md'}); f.save(); assert.throws(()=>verifyPackage(f.root),/duplicate/); });
test('reject missing files', () => { const f=fixture(); f.manifest.files[0].path='missing.md'; f.save(); assert.throws(()=>verifyPackage(f.root),/ENOENT/); });
test('reject malformed digest', () => { const f=fixture(); f.manifest.files[0].sha256='not-a-hash'; f.save(); assert.throws(()=>verifyPackage(f.root),/Unsafe/); });
test('reject unknown version', () => { const f=fixture(); f.manifest.version='unknown'; f.save(); assert.throws(()=>verifyPackage(f.root),/Invalid/); });
