import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { describe, it } from 'node:test';
import { installSkill } from '../src/install.mjs';
import { getPlatform, resolveSkillsDir } from '../src/platforms.mjs';

describe('platform registry', () => {
  it('resolves Codex project skills directory', () => {
    const platform = getPlatform('codex');
    assert.equal(resolveSkillsDir(platform, 'project'), '.codex/skills');
  });

  it('resolves Claude project skills directory', () => {
    const platform = getPlatform('claude');
    assert.equal(resolveSkillsDir(platform, 'project'), '.claude/skills');
  });

  it('resolves OpenCode global skills directory override', () => {
    const platform = getPlatform('opencode');
    assert.equal(resolveSkillsDir(platform, 'global'), '.config/opencode/skills');
  });

  it('rejects unknown platform ids', () => {
    assert.throws(() => getPlatform('unknown-ai'), /Unknown platform/);
  });
});

describe('installer', () => {
  it('copies skill assets into the Codex project skills directory', async () => {
    const temp = await mkdtemp(path.join(os.tmpdir(), 'bookmark-kb-install-'));
    const assetRoot = path.join(temp, 'assets');
    const skillSourceDir = path.join(assetRoot, 'skills', 'bookmark-kb-skill');

    await mkdir(skillSourceDir, { recursive: true });
    await writeFile(
      path.join(assetRoot, 'manifest.json'),
      JSON.stringify({ skills: ['bookmark-kb-skill/SKILL.md'] }, null, 2)
    );
    await writeFile(path.join(skillSourceDir, 'SKILL.md'), 'skill body');

    const result = await installSkill({
      baseDir: temp,
      assetRoot,
      platformIds: ['codex'],
      scope: 'project',
      overwrite: false,
    });

    const installed = path.join(temp, '.codex', 'skills', 'bookmark-kb-skill', 'SKILL.md');
    assert.equal(await readFile(installed, 'utf8'), 'skill body');
    assert.deepEqual(result, [{ platform: 'codex', copied: 1, skipped: 0 }]);
  });
});
