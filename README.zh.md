# paper-skills

`paper-skills` 是一个面向论文管理工作流的通用 skill 源仓库。

这个仓库刻意使用公开的 `skills/` 目录树，而不是 `.agents/skills/`、`.codex/skills/` 这类厂商隐藏目录。目标是让仓库更容易阅读、复制、分发，并且能被不同 agent 运行时复用，而不用重写核心 skill 内容。

## 目录结构

```text
paper-skills/
  README.md
  README.en.md
  README.zh.md
  AGENTS.md
  skills/
    paper-match/
    paper-bibkey/
    paper-rename/
    paper-organize/
    paper-ingest/
    paper-notes/
    paper-missing/
    paper-reconcile/
  docs/
    conventions.md
    portability.md
  adapters/
    openai/
```

## 包含的技能

- `paper-match`：识别本地 PDF 实际对应哪篇论文，并报告置信度或歧义
- `paper-bibkey`：生成或修复稳定的 bibkey
- `paper-rename`：基于已确认的 bibkey 规范化 PDF 文件名
- `paper-organize`：把论文放到最终归档位置
- `paper-ingest`：编排端到端 ingest 流程
- `paper-notes`：创建或更新结构化论文笔记
- `paper-missing`：维护 missing-paper 清单
- `paper-reconcile`：维护库级覆盖状态和重复状态

## 设计原则

- 使用可移植、非隐藏的仓库结构
- 规范主键保持 ASCII
- 中文可用于展示文本，但不进入 bibkey
- skill 保持单一职责，而不是做成一个巨大的单体流程
- 优先使用 Markdown 和小型辅助资源，而不是重量级打包方案
- `skills/` 是公开发布的主结构
- `adapters/openai/` 是可选兼容层，不是主 skill 结构

## 文档

- [`docs/conventions.md`](docs/conventions.md)
- [`docs/portability.md`](docs/portability.md)
