# 可移植性

## 目标

这个仓库是一个面向论文管理 skill 的厂商中立源仓库。

主内容应当能够适配不同下游运行时，例如它们可能期望：

- `skills/<name>/`
- `.agents/skills/<name>/`
- `.codex/skills/<name>/`
- 其他自定义安装路径

## 主结构

公开的 source of truth 是可见的 `skills/` 目录树。

不要把隐藏厂商目录当成主要发布结构。

## 适配层

厂商相关元数据应放在可选适配层，例如：

- `adapters/openai/<skill-name>/openai.yaml`

这些文件是兼容层，不是 skill 本体的权威内容。

## 内部引用规则

- 所有引用尽量相对于 skill 目录本身。
- 不要在 `SKILL.md` 中硬编码某一种厂商路径约定。
- 不要在 skill 文档或脚本中写死某个下游 vault 布局、磁盘盘符、用户目录、同步盘目录或操作系统 shell。
- 路径应来自用户输入、CLI 参数、下游 `.paper-skills.json`，或唯一可发现的默认文件名。
- 示例命令优先使用跨平台形式，例如 `python scripts/<name>.py --config <workspace>/.paper-skills.json`。
- 优先使用可移植的 Markdown 和小型辅助脚本，而不是运行时绑定很强的打包形式。

## 下游配置约定

下游项目可以在 workspace root 提供 `.paper-skills.json`。常用字段包括：

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

这个文件属于下游项目，不属于 `paper-skills` 源仓库本体。

## 脚本约定

如果 skill 内带有辅助脚本，应满足：

- 职责单一、易于检查
- 优先使用标准库依赖
- 接收 `--config` 或明确路径参数，而不是内置特定仓库路径
- 无配置时只能使用唯一可发现的文件名；如果有多个候选，应停止并要求用户提供配置
- 如果依赖 `pdfinfo`、`pdftotext` 之类可选外部工具，要清晰失败并说明缺失原因

## 下游消费建议

下游工具可以重定位 skill 目录，但不应需要重写这些主文件：

- `SKILL.md`
- `templates/*`
- `scripts/*`
- `references/*`

理论上只有可选的 adapter 元数据会随着目标运行时变化。
