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

你是否还在为乱糟糟的收藏夹而头疼不已？常常想不起自己收藏的内容放到了哪里？想要整理庞大的收藏夹又无从下手？本 Skill 可以直接将你的收藏夹变成即插即用的 AI 知识库。

`bookmark-kb-skill` 的核心目标不是做一个 Skill 管理平台，而是让 Agent 像使用本地知识库一样使用你的 Chrome 收藏夹：找回忘记放在哪里的资料、把某一主题的收藏内容整理成任务上下文、导出可审阅的整理报告、发现重复链接和混乱文件夹。多平台安装能力只是为了降低使用门槛，让你可以快速把这项收藏夹知识库能力装进自己正在使用的 AI 工具里。

它优先复用本地缓存和精简索引，不会在每次搜索时把大量网页内容塞进对话，也不会默认修改你的 Chrome 收藏夹。用户入口是 npm/npx；包内部会使用一个很小的 Python 标准库脚本处理本地书签，但人类用户和 Agent 都不需要直接调用 Python 文件。

## 适合这些场景

- 只记得主题，不记得链接收藏在哪个文件夹。
- 想让 Agent 把某个主题的收藏夹内容作为后续写作、调研、编码或方案设计的上下文。
- 收藏夹太大，需要先看到重复链接、可疑混乱项和整理建议。
- 不想每次都导出整份书签，也不想把一大堆网页内容直接倒进聊天窗口。

## 给 Agent

复制下面这一段给你的 AI 编程 Agent。Agent 应该知道自己运行在哪个平台；它只需要从支持的平台 id 里选择匹配项，然后按命令格式安装。

```text
请把 bookmark-kb-skill 安装到当前项目。

1. 识别你当前所在的 AI Agent 平台。
2. 从这些平台 id 里选择匹配项：codex, claude, gemini, cursor, opencode, openclaw, hermes。
3. 执行：
   npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=<platform-id> --scope=project --overwrite
4. 安装后，当我要求搜索、引用或整理 Chrome 收藏夹时，请使用 bookmark-kb-skill。
```

如果我明确要求你同时安装到多个平台，请把 platform id 用英文逗号连接，例如：

```text
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=codex,claude,openclaw,hermes --scope=project --overwrite
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

同时安装到 Codex、Claude、OpenClaw 和 Hermes：

```sh
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=codex,claude,openclaw,hermes --scope=project --overwrite
```

### npm 发布后安装

```sh
npx bookmark-kb-skill install --platforms=codex --scope=project --overwrite
```

安装到多个平台：

```sh
npx bookmark-kb-skill install --platforms=codex,claude,openclaw,hermes --scope=project --overwrite
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
- `openclaw`
- `hermes`

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

## Star 趋势

<p align="center">
  <a href="https://star-history.com/#RUDY-GAOJ/bookmark-kb-skill&Date">
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=RUDY-GAOJ/bookmark-kb-skill&type=Date" />
  </a>
</p>
