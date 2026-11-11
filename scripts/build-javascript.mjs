import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { minify } from 'terser';

const ASSETS = new URL('../skills/documentation/visual-explainers/assets/', import.meta.url);
const SOURCE_NAMES = ['charts.js', 'navigation.js', 'core.js'];

/**
 * Remove comments and unnecessary whitespace without optimizing or renaming code.
 * @param {string} source Readable JavaScript parsed as a classic script.
 * @param {string} name Filename used in parser diagnostics.
 * @returns {Promise<string>} Compact JavaScript followed by one newline.
 * @throws {SyntaxError} The source cannot be parsed as JavaScript.
 */
export async function compileJavaScript(source, name) {
  // Parse and print the source without changing its bindings or optimizing logic.
  let result;
  try {
    result = await minify({ [name]: source }, {
      ecma: 2020,
      compress: false,
      mangle: false,
      format: { comments: false },
    });
  } catch (error) {
    // Preserve failures outside Terser's parser error family.
    if (error.name !== 'SyntaxError') throw error;

    // Normalize parser errors to native errors identifying the readable source.
    throw new SyntaxError(`${name}: ${error.message}`);
  }

  // Separate adjacent generated assets with a deterministic trailing newline.
  return result.code + '\n';
}

/**
 * Generate adjacent minified browser assets or inspect their freshness.
 * @param {URL} directory Asset directory URL ending in a slash.
 * @param {boolean} [checkOnly=false] Report stale or missing outputs without writing them.
 * @returns {Promise<string[]>} Outdated output names in check mode; otherwise empty.
 * @throws {SyntaxError} A source cannot be parsed; no outputs have been written.
 * @throws {Error} An asset cannot be read or written. A write failure may leave
 *   earlier outputs updated; rerun generation after correcting the I/O problem.
 */
export async function generateJavaScript(directory, checkOnly = false) {
  // Compile every source before writing so a parser failure leaves outputs alone.
  const assets = await Promise.all(SOURCE_NAMES.map(async name => {
    // Read each source at the filesystem boundary.
    const source = await readFile(new URL(name, directory), 'utf8');

    // Compile its contents and retain the adjacent generated filename.
    const code = await compileJavaScript(source, name);
    return { name: name.replace(/\.js$/, '.min.js'), code };
  }));

  // Inspect generated assets without repairing missing or outdated files.
  if (checkOnly) {
    const outdated = [];

    for (const asset of assets) {
      // Treat an absent generated file as stale and propagate other read failures.
      let current;
      try {
        current = await readFile(new URL(asset.name, directory), 'utf8');
      } catch (error) {
        if (error.code !== 'ENOENT') throw error;
      }

      // Record every byte mismatch, including a missing output.
      if (current !== asset.code) outdated.push(asset.name);
    }

    return outdated;
  }

  // Publish the compiled artifacts while leaving readable sources unchanged.
  for (const asset of assets) {
    await writeFile(new URL(asset.name, directory), asset.code, 'utf8');
  }

  return [];
}

async function main() {
  // Accept generation by default and one explicit read-only check mode.
  const arguments_ = process.argv.slice(2);
  if (arguments_.length > 1 || (arguments_.length === 1 && arguments_[0] !== '--check')) {
    throw new Error('Usage: node scripts/build-javascript.mjs [--check]');
  }

  // Generate or compare all browser assets using the repository-relative boundary.
  const checkOnly = arguments_.includes('--check');
  const outdated = await generateJavaScript(ASSETS, checkOnly);
  if (outdated.length) {
    throw new Error(`Stale JavaScript: ${outdated.join(', ')}. Run just build-js.`);
  }

  // Report successful generation or a clean freshness check.
  console.log(checkOnly ? 'Minified JavaScript is up to date.' : 'Generated minified JavaScript.');
}

// Run the CLI only for direct execution; imports expose the build operations to tests.
if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  main().catch(error => {
    console.error(`JavaScript build failed: ${error.message}`);
    process.exitCode = 1;
  });
}
