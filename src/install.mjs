import { copyFile, mkdir, readFile, access } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { PLATFORMS, getPlatform, resolveSkillsDir } from './platforms.mjs';

export function resolveBaseDir(scope, cwd = process.cwd(), env = process.env) {
  if (scope === 'global') {
    return env.USERPROFILE || env.HOME;
  }

  return cwd;
}

export async function installSkill({
  baseDir,
  assetRoot,
  platformIds,
  scope,
  overwrite,
}) {
  const manifestPath = path.join(assetRoot, 'manifest.json');
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  const results = [];

  for (const platformId of platformIds) {
    const platform = getPlatform(platformId);
    const skillsDir = path.join(baseDir, resolveSkillsDir(platform, scope));
    let copied = 0;
    let skipped = 0;

    for (const relPath of manifest.skills ?? []) {
      const sourcePath = path.join(assetRoot, 'skills', relPath);
      const targetPath = path.join(skillsDir, relPath);

      if (!overwrite) {
        try {
          await access(targetPath);
          skipped += 1;
          continue;
        } catch {
          // copy below
        }
      }

      await mkdir(path.dirname(targetPath), { recursive: true });
      await copyFile(sourcePath, targetPath);
      copied += 1;
    }

    results.push({ platform: platform.id, copied, skipped });
  }

  return results;
}

async function main(argv = process.argv.slice(2)) {
  if (argv.length === 0) {
    return;
  }

  const options = {
    platformIds: PLATFORMS.map((platform) => platform.id),
    scope: 'project',
    overwrite: false,
  };

  for (const arg of argv) {
    if (arg.startsWith('--platforms=')) {
      options.platformIds = arg.slice('--platforms='.length).split(',').filter(Boolean);
      continue;
    }

    if (arg.startsWith('--scope=')) {
      options.scope = arg.slice('--scope='.length);
      continue;
    }

    if (arg === '--overwrite') {
      options.overwrite = true;
    }
  }

  const result = await installSkill({
    baseDir: resolveBaseDir(options.scope),
    assetRoot: path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'assets'),
    ...options,
  });

  console.log(JSON.stringify(result));
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  void main();
}
