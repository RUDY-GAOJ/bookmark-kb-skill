export const PLATFORMS = [
  { id: 'claude', name: 'Claude Code', skillsDir: '.claude/skills' },
  { id: 'codex', name: 'Codex', skillsDir: '.codex/skills' },
  { id: 'gemini', name: 'Gemini CLI', skillsDir: '.gemini/skills' },
  { id: 'cursor', name: 'Cursor', skillsDir: '.cursor/skills' },
  {
    id: 'opencode',
    name: 'OpenCode',
    skillsDir: '.opencode/skills',
    globalSkillsDir: '.config/opencode/skills',
  },
];

export function getPlatform(id) {
  const platform = PLATFORMS.find((candidate) => candidate.id === id);
  if (!platform) {
    throw new Error(`Unknown platform: ${id}`);
  }
  return platform;
}

export function resolveSkillsDir(platform, scope) {
  if (scope === 'global' && platform.globalSkillsDir) {
    return platform.globalSkillsDir;
  }
  return platform.skillsDir;
}
