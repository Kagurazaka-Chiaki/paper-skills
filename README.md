# paper-skills

[中文](./README.md) | [English](./README.en.md)

`paper-skills` 是一个面向论文管理工作流的通用 skill 源仓库。

这个仓库刻意使用公开的 `skills/` 目录树，而不是 `.agents/skills/`、`.codex/skills/` 这类厂商隐藏目录。目标是让仓库更容易阅读、复制、分发，并且能被不同 agent 运行时复用，而不用重写核心 skill 内容。

路径和库布局由下游项目决定。需要稳定配置时，在下游仓库根目录提供 `.paper-skills.json`，或在脚本命令中显式传入路径；本 skill 源仓库不假设某个 Obsidian vault、磁盘盘符或操作系统 shell。

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
    paper-bib-clean/
    paper-rename/
    paper-organize/
    paper-ingest/
    paper-notes/
    paper-deep-read/
    paper-missing/
    paper-reconcile/
    paper-index/
  docs/
    conventions.md
    portability.md
  adapters/
    openai/
```

## 包含的技能

- `paper-match`：识别本地 PDF 实际对应哪篇论文，并报告置信度或歧义
- `paper-bibkey`：生成或修复稳定的 bibkey
- `paper-bib-clean`：清洗现有 BibTeX，使其可被 Zotero 正常导入
- `paper-rename`：基于已确认的 bibkey 规范化 PDF 文件名
- `paper-organize`：把论文放到最终归档位置
- `paper-ingest`：编排端到端 ingest 流程
- `paper-notes`：创建或更新结构化论文笔记
- `paper-deep-read`：对已识别论文做精读记录，拆解问题、方法、证据、限制和实现风险
- `paper-missing`：维护 missing-paper 清单
- `paper-reconcile`：维护库级覆盖状态和重复状态
- `paper-index`：维护仓库内最小 `.bib`、`papers.sqlite` 与 `resources.sqlite` 轻量索引

## 下游配置

推荐下游项目使用 `.paper-skills.json` 描述自己的资源目录、索引文件、外部 Zotero BibTeX 和 PDF 根目录。示例字段：

```json
{
  "resource_root": "<resource-root>",
  "paper_notes_dir": "<paper-note-dir>",
  "resource_bibs": {
    "paper": "<papers.bib>",
    "book": "<books.bib>",
    "reference-note": "<reference-notes.bib>"
  },
  "paper_sqlite": "<papers.sqlite>",
  "resource_sqlite": "<resources.sqlite>",
  "external_library_bib": "<external-library.bib>",
  "external_pdf_roots": {
    "paper": "<paper-pdf-root>",
    "book": "<book-pdf-root>",
    "reference-note": "<reference-note-pdf-root>"
  }
}
```

如果没有配置，脚本只使用唯一可发现的默认文件名，例如 `papers.bib`、`books.bib`、`reference-notes.bib`、`papers.sqlite` 和 `resources.sqlite`；出现多个候选时应停止并要求显式配置。

## 设计原则

- 使用可移植、非隐藏的仓库结构
- 规范主键保持 ASCII
- 中文可用于展示文本，但不进入 bibkey
- skill 保持单一职责，而不是做成一个巨大的单体流程
- 优先使用 Markdown 和小型辅助资源，而不是重量级打包方案
- `skills/` 是公开发布的主结构
- `adapters/openai/` 是可选兼容层，不是主 skill 结构

## 文档

- [AGENTS.md](AGENTS.md)
- [docs/conventions.md](docs/conventions.md)
- [docs/portability.md](docs/portability.md)
- [README.en.md](README.en.md)
