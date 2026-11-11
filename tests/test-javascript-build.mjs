import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { runInNewContext } from 'node:vm';
import { parse } from 'acorn';
import { compileJavaScript, generateJavaScript } from '../scripts/build-javascript.mjs';

const ASSETS = new URL('../skills/documentation/visual-explainers/assets/', import.meta.url);
const SOURCE_NAMES = ['charts.js', 'navigation.js', 'core.js'];

function programShape(source) {
  return JSON.stringify(parse(source, { ecmaVersion: 'latest' }), function (key, value) {
    // Ignore source positions and literal spelling while retaining raw template text.
    if (['start', 'end'].includes(key) || (key === 'raw' && this.type === 'Literal')) {
      return undefined;
    }

    // Ignore redundant standalone semicolons only inside statement lists.
    if (key === 'body' && Array.isArray(value)) {
      return value.filter(statement => statement.type !== 'EmptyStatement');
    }

    return value;
  });
}

async function checkModernSyntax() {
  // Exercise regexes, comment-like string text, nested templates, and significant newlines.
  const source = [
    '// Remove this source comment.',
    'const url = "https://example.com/a//b";',
    'const label = `outer ${`inner ${2 + 3}`} end`;',
    'const expression = /a\\/\\/b/;',
    'function newlineReturn() { return\n{ value: 1 }; }',
    'let count = 1;',
    'const total = count + ++count;',
    'JSON.stringify([url, label, expression.test("a//b"), newlineReturn(), total]);',
  ].join('\n');

  // Minify the program through the build operation used by the CLI.
  const compact = await compileJavaScript(source, 'syntax.js');

  // Verify both parsed structure and observable execution, preserving template spacing.
  assert.equal(programShape(compact), programShape(source));
  assert.equal(runInNewContext(compact), runInNewContext(source));
  assert.ok(compact.length < source.length);
  assert.ok(!compact.includes('Remove this source comment'));
}

async function checkBundledPrograms() {
  for (const name of SOURCE_NAMES) {
    // Read each real source and its committed browser artifact.
    const source = await readFile(new URL(name, ASSETS), 'utf8');
    const generated = await readFile(new URL(name.replace(/\.js$/, '.min.js'), ASSETS), 'utf8');

    // Verify freshness, compactness, and unchanged executable syntax.
    assert.equal(generated, await compileJavaScript(source, name), name);
    assert.ok(generated.length < source.length, name);
    assert.equal(programShape(generated), programShape(source), name);
  }
}

async function checkFreshnessLifecycle() {
  // Create isolated sources so stale and missing artifacts cannot affect the repository.
  const temporary = await mkdtemp(join(tmpdir(), 'agent-skills-js-build-'));
  const directory = pathToFileURL(temporary + '/');

  try {
    // Seed readable files for the complete browser source set.
    for (const name of SOURCE_NAMES) {
      await writeFile(new URL(name, directory), 'globalThis.value = 1;\n');
    }

    // Generate the initial artifacts and establish a clean freshness check.
    assert.deepEqual(await generateJavaScript(directory), []);
    assert.deepEqual(await generateJavaScript(directory, true), []);
    const originalCore = await readFile(new URL('core.min.js', directory), 'utf8');

    // Change one source and verify that check mode reports it without repairing output.
    await writeFile(new URL('core.js', directory), 'globalThis.value = 2;\n');
    assert.deepEqual(await generateJavaScript(directory, true), ['core.min.js']);
    assert.equal(await readFile(new URL('core.min.js', directory), 'utf8'), originalCore);

    // Remove another artifact and verify that check mode leaves it absent.
    await rm(new URL('charts.min.js', directory));
    assert.deepEqual(await generateJavaScript(directory, true), ['charts.min.js', 'core.min.js']);
    await assert.rejects(readFile(new URL('charts.min.js', directory)), { code: 'ENOENT' });

    // Regenerate both outdated artifacts and verify recovery to a clean check.
    await generateJavaScript(directory);
    assert.deepEqual(await generateJavaScript(directory, true), []);
    const recoveredCore = await readFile(new URL('core.min.js', directory), 'utf8');

    // Reject invalid JavaScript before publishing any otherwise valid source changes.
    await writeFile(new URL('core.js', directory), 'globalThis.value = 3;\n');
    await writeFile(new URL('navigation.js', directory), 'const invalid = ;\n');
    await assert.rejects(generateJavaScript(directory), {
      name: 'SyntaxError', message: /navigation\.js/,
    });
    assert.equal(await readFile(new URL('core.min.js', directory), 'utf8'), recoveredCore);
  } finally {
    await rm(temporary, { recursive: true, force: true });
  }
}

await checkModernSyntax();
await checkBundledPrograms();
await checkFreshnessLifecycle();
console.log('JavaScript minification, syntax equivalence, and freshness lifecycle checks passed.');
