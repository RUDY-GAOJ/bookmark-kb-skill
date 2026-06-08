<p align="center">
  <img src="hero.svg" alt="Bookmark KB Skill - Chrome bookmarks to local AI context" width="100%" />
</p>

<p align="center">
  <a href="../README.md">English</a>
  ·
  <a href="#给-agent">给 Agent</a>
  ·
  <a href="#给人类">给人类</a>
</p>

<p align="center">
  <a href="https://github.com/RUDY-GAOJ/bookmark-kb-skill/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/RUDY-GAOJ/bookmark-kb-skill/actions/workflows/ci.yml/badge.svg" /></a>
  <a href="https://github.com/RUDY-GAOJ/bookmark-kb-skill/releases/tag/v0.1.0"><img alt="Release" src="https://img.shields.io/github/v/release/RUDY-GAOJ/bookmark-kb-skill?display_name=tag" /></a>
  <a href="https://github.com/RUDY-GAOJ/bookmark-kb-skill/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/RUDY-GAOJ/bookmark-kb-skill" /></a>
</p>

# Bookmark KB Skill

把 Chrome 收藏夹变成本地、低 token 消耗的 AI 知识库。

`bookmark-kb-skill` 可以把同一份平台中立 Skill 安装到常见 AI 工具的 `skills/` 目录，并提供 npm CLI 来刷新收藏夹、搜索链接、生成上下文包、导出整理报告。

用户入口是 npm/npx。包内部会使用一个很小的 Python 标准库脚本处理本地书签，但人类用户和 Agent 都不需要直接调用 Python 文件。

## 给 Agent

复制下面这一段给你的 AI 编程 Agent，让它替你安装：

```text
请把 bookmark-kb-skill 安装到当前项目的 Codex skill 目录。请执行：
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=codex --scope=project --overwrite
安装后，当我要求搜索、引用或整理 Chrome 收藏夹时，请使用 bookmark-kb-skill。
```

如果你同时使用 Codex 和 Claude，复制这一段：

```text
请把 bookmark-kb-skill 安装到当前项目的 Codex 和 Claude skill 目录。请执行：
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=codex,claude --scope=project --overwrite
安装后，当我要求搜索、引用或整理 Chrome 收藏夹时，请使用 bookmark-kb-skill。
```

安装后，你可以这样对 Agent 说：

```text
使用 bookmark-kb-skill 搜索我的 Chrome 收藏夹里关于 AI agent 的内容。
```

```text
把我的收藏夹里关于 OpenAI API 的内容整理成上下文，供我后面写方案使用。
```

```text
整理我的 Chrome 收藏夹，找出重复链接和需要整理的内容。
```

## 给人类

### 从 GitHub 安装

在 npm 发布前，可以直接从 GitHub 安装：

```sh
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=codex --scope=project --overwrite
```

同时安装到 Codex 和 Claude：

```sh
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=codex,claude --scope=project --overwrite
```

### npm 发布后安装

```sh
npx bookmark-kb-skill install --platforms=codex --scope=project --overwrite
```

安装到多个平台：

```sh
npx bookmark-kb-skill install --platforms=codex,claude --scope=project --overwrite
```

全局安装到用户目录：

```sh
npx bookmark-kb-skill install --platforms=codex --scope=global --overwrite
```

### 支持的平台

- `codex`
- `claude`
- `gemini`
- `cursor`
- `opencode`

### 本地 CLI

刷新本地收藏夹缓存：

```sh
bookmark-kb refresh --json
```

搜索收藏夹：

```sh
bookmark-kb search "openai docs" --json
```

生成上下文包：

```sh
bookmark-kb context "openai docs" --json
```

导出整理报告：

```sh
bookmark-kb organize --mode all --json
```

测试时使用临时缓存目录：

```sh
BOOKMARK_KB_HOME=.tmp-bookmark-kb bookmark-kb refresh --json
```

指定另一个 Chrome Profile 的 `Bookmarks` 文件：

```sh
bookmark-kb refresh --bookmarks-file "/path/to/Chrome/User Data/Default/Bookmarks" --json
```

## 能力边界

- 第一版读取 Chrome 本地 `Bookmarks` 文件中的标题、URL、文件夹路径。
- 第一版不会修改 Chrome 收藏夹。
- 普通搜索不会每次爬网页。
- 整理功能只导出报告，默认不执行移动、删除或合并操作。
- 运行时缓存默认保存在 `~/.bookmark-kb`，可通过 `BOOKMARK_KB_HOME` 覆盖。

## Star

<p align="center">
  <a href="https://github.com/RUDY-GAOJ/bookmark-kb-skill/stargazers">
    <img alt="GitHub stars" src="https://img.shields.io/github/stars/RUDY-GAOJ/bookmark-kb-skill?style=social" />
  </a>
</p>
