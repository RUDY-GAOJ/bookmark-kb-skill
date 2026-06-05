import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { main as installMain } from './install.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CLI_SCRIPT = path.resolve(
  __dirname,
  '..',
  'assets',
  'skills',
  'bookmark-kb-skill',
  'scripts',
  'bookmark_kb.py'
);

const BOOKMARK_COMMANDS = new Set(['refresh', 'search', 'context', 'organize']);

export function usage() {
  return `bookmark-kb-skill

Usage:
  bookmark-kb-skill install --platforms=codex --scope=project --overwrite
  bookmark-kb-skill refresh --json
  bookmark-kb-skill search "openai docs" --json
  bookmark-kb-skill context "openai docs" --json
  bookmark-kb-skill organize --mode all --json

Aliases:
  bookmark-kb <command>
  bookmark-kb-install --platforms=codex --scope=project

Environment:
  BOOKMARK_KB_HOME     Override the local bookmark cache directory.
  BOOKMARK_KB_PYTHON   Override the Python executable used internally.
`;
}

function candidatePythons(env = process.env) {
  const candidates = [];
  if (env.BOOKMARK_KB_PYTHON) {
    candidates.push(env.BOOKMARK_KB_PYTHON);
  }
  candidates.push(process.platform === 'win32' ? 'python' : 'python3');
  candidates.push('python');
  return [...new Set(candidates)];
}

export function resolvePython(env = process.env) {
  for (const candidate of candidatePythons(env)) {
    const result = spawnSync(candidate, ['--version'], { encoding: 'utf8' });
    if (result.status === 0) {
      return candidate;
    }
  }
  throw new Error('Python is required internally, but no python executable was found. Set BOOKMARK_KB_PYTHON to the Python path.');
}

export function runBookmarkCommand(command, args, options = {}) {
  const python = options.python ?? resolvePython(options.env ?? process.env);
  return spawnSync(python, [CLI_SCRIPT, command, ...args], {
    cwd: options.cwd ?? process.cwd(),
    env: options.env ?? process.env,
    encoding: 'utf8',
    stdio: options.stdio ?? 'inherit',
  });
}

export async function main(argv = process.argv.slice(2)) {
  const [command, ...args] = argv;

  if (!command || command === '--help' || command === '-h' || command === 'help') {
    console.log(usage());
    return 0;
  }

  if (command === 'install') {
    await installMain(args);
    return 0;
  }

  if (BOOKMARK_COMMANDS.has(command)) {
    const result = runBookmarkCommand(command, args);
    return result.status ?? 1;
  }

  console.error(`Unknown command: ${command}\n`);
  console.error(usage());
  return 1;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = await main();
}
