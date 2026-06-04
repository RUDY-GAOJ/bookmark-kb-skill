import assert from 'node:assert/strict';
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
