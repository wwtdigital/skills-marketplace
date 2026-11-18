import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const read = path => readFile(new URL(path, import.meta.url), 'utf8');
const retiredBrand = new RegExp(['arc', 'works'].join(''), 'i');

test('Pattern Shop uses Castworks in current copy, metadata and design references', async () => {
  for (const path of [
    '../app/layout.tsx', '../app/page.tsx', '../components/Footer.tsx',
    '../app/globals.css', '../public/brand/README.md', '../../README.md', '../../CLAUDE.md',
  ]) {
    assert.doesNotMatch(await read(path), retiredBrand, path);
  }
  assert.match(await read('../app/layout.tsx'), /Pattern Shop, from WWT Digital Castworks OS:/);
  assert.match(await read('../app/page.tsx'), /WWT Digital Castworks OS/);
  assert.match(await read('../components/Footer.tsx'), /Part of WWT Digital Castworks OS/);
});
