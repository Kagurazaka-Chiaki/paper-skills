# 约定

## 规范目录结构

技能统一发布在：

- `skills/<skill-name>/SKILL.md`
- 可选的 `skills/<skill-name>/templates/`
- 可选的 `skills/<skill-name>/scripts/`
- 可选的 `skills/<skill-name>/references/`

`skills/` 是本仓库的公开主结构，也是默认 source of truth。

## Skill 命名

- 使用小写加连字符的目录名。
- 一个目录只放一个 skill。
- skill 入口文件统一命名为 `SKILL.md`。

## `SKILL.md` 必备部分

每个 skill 都应显式包含：

- `Purpose`
- `Reads`
- `Writes`
- `Source Of Truth`
- `Required Behavior`
- `Non-Goals`
- `Output Contract`

正文应尽量直接、可执行，避免空泛描述。skill 要保持单一职责、便于组合。

## 可选资源目录

- `templates/`：可复用输出模板
- `scripts/`：减少重复劳动的小型辅助脚本
- `references/`：稳定的判断规则或领域说明

只有在目录内有真实内容时才创建，不要为了“看起来完整”而制造空目录。

## 论文命名约定

- 规范 bibkey：`firstauthor_YYYY_shorttopic`
- 规范 PDF 文件名：`{bibkey} - {short_title}.pdf`
- `bibkey` 必须保持 ASCII
- `short_title` 作为展示层时可以使用中文

优先保证标识稳定，而不是为了风格统一频繁改名。

## 技能边界

- `paper-match`：识别论文身份与重复风险
- `paper-bibkey`：生成或修复稳定 bibkey
- `paper-rename`：基于现有 bibkey 规范化文件名
- `paper-organize`：决定最终归档位置
- `paper-ingest`：编排整条 ingest 流程
- `paper-notes`：创建或更新论文笔记
- `paper-missing`：维护 missing-paper 清单
- `paper-reconcile`：维护集合级覆盖状态与重复状态
- `paper-index`：维护仓库级 `papers.bib` 与 `papers.sqlite` 简单索引
