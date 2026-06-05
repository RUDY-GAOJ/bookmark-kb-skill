import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtemp, mkdir, readFile, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { describe, it } from 'node:test';
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
  it('does not run the CLI on dynamic import when argv includes platforms', async () => {
    const temp = await mkdtemp(path.join(os.tmpdir(), 'bookmark-kb-import-'));
    const originalArgv = process.argv;
    const originalCwd = process.cwd();
    const unique = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const rejections = [];
    const onUnhandledRejection = (reason) => {
      rejections.push(reason);
    };

    try {
      process.chdir(temp);
      process.argv = [originalArgv[0], originalArgv[1], '--platforms=codex'];
      process.on('unhandledRejection', onUnhandledRejection);

      await import(`../src/install.mjs?side-effect=${unique}`);

      await new Promise((resolve) => setTimeout(resolve, 100));
      assert.deepEqual(rejections, []);
      await assert.rejects(
        readFile(path.join(temp, '.codex', 'skills', 'bookmark-kb-skill', 'SKILL.md'), 'utf8')
      );
    } finally {
      process.off('unhandledRejection', onUnhandledRejection);
      process.argv = originalArgv;
      process.chdir(originalCwd);
    }
  });

  it('resolves the base directory from the user profile for global scope', () => {
    const cwd = path.join(os.tmpdir(), 'bookmark-kb-cwd');
    const env = {
      USERPROFILE: path.join(os.tmpdir(), 'bookmark-kb-userprofile'),
      HOME: path.join(os.tmpdir(), 'bookmark-kb-home'),
    };
    const originalArgv = process.argv;
    const unique = `${Date.now()}-${Math.random().toString(16).slice(2)}`;

    return (async () => {
      process.argv = [originalArgv[0], originalArgv[1]];
      try {
        const installModule = await import(`../src/install.mjs?base-dir=${unique}`);
        assert.equal(installModule.resolveBaseDir('project', cwd, env), cwd);
        assert.equal(installModule.resolveBaseDir('global', cwd, env), env.USERPROFILE);
      } finally {
        process.argv = originalArgv;
      }
    })();
  });

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
    const originalArgv = process.argv;
    const unique = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    let installModule;

    try {
      process.argv = [originalArgv[0], originalArgv[1]];
      installModule = await import(`../src/install.mjs?install=${unique}`);

      const result = await installModule.installSkill({
        baseDir: temp,
        assetRoot,
        platformIds: ['codex'],
        scope: 'project',
        overwrite: false,
      });

      const installed = path.join(temp, '.codex', 'skills', 'bookmark-kb-skill', 'SKILL.md');
      assert.equal(await readFile(installed, 'utf8'), 'skill body');
      assert.deepEqual(result, [{ platform: 'codex', copied: 1, skipped: 0 }]);
    } finally {
      process.argv = originalArgv;
    }
  });

  it('runs through the bin entrypoint', async () => {
    const temp = await mkdtemp(path.join(os.tmpdir(), 'bookmark-kb-bin-'));
    const bin = path.resolve('bin/bookmark-kb-install.js');

    const result = spawnSync(process.execPath, [bin, '--platforms=codex', '--scope=project'], {
      cwd: temp,
      encoding: 'utf8',
    });

    assert.equal(result.status, 0, result.stderr);
    const payload = JSON.parse(result.stdout);
    assert.deepEqual(payload, [{ platform: 'codex', copied: 3, skipped: 0 }]);

    const installed = path.join(temp, '.codex', 'skills', 'bookmark-kb-skill', 'SKILL.md');
    assert.equal(typeof await readFile(installed, 'utf8'), 'string');
  });
});

describe('skill documentation contract', () => {
  it('keeps the skill instructions platform neutral and environment aware', async () => {
    const skill = await readFile('assets/skills/bookmark-kb-skill/SKILL.md', 'utf8');
    const frontmatter = skill.match(/^---\r?\n(?<body>[\s\S]*?)\r?\n---/);

    assert.ok(frontmatter, 'SKILL.md must include YAML frontmatter');
    const name = frontmatter.groups.body
      .split(/\r?\n/)
      .find((line) => line.startsWith('name:'));

    assert.equal(name, 'name: bookmark-kb-skill');
    assert.match(skill, /Use when/);
    assert.doesNotMatch(skill, /\.codex\/bookmark-kb/);
    assert.match(skill, /BOOKMARK_KB_HOME/);
  });
});
