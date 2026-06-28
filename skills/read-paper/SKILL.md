---
name: read-paper
description: 阅读学术论文 PDF、arXiv 链接或本地论文文件，提取关键图片/图表资产，并生成结构化中文 Markdown 论文解读。用于论文精读、整理、翻译式解读、组会准备和文献调研；必须覆盖论文信息、贡献、背景、问题定义、方法、原文例子、实验设置、结果、局限性和个人评价。
---

# Read Paper

## 目标

输入论文 PDF 或链接，输出结构化中文 Markdown 解读文档。写作时读取 `references/document_template.md` 作为最终文档结构，不要在 `SKILL.md` 内复述完整模板。

每篇论文只使用一个最终输出目录，固定为：

```text
~/Library/Mobile Documents/com~apple~CloudDocs/同步文档/Obsidian Vault/ReadPaper/read-paper-{slug}/
```

该目录内固定放：

- `论文解读_{slug}.md`
- `attachments/`

临时处理目录固定为 `/tmp/read-paper-{slug}/`，只放 PDF、纯文本、提取图片和中间文件。

## 工作流

1. **准备论文与工作目录**
   - 链接输入：下载到 `/tmp/read-paper-{slug}/paper.pdf`。
   - 本地 PDF：可直接读取，或复制为 `/tmp/read-paper-{slug}/paper.pdf`。
   - Bash 命令默认使用 Conda 环境 `dzt`：`conda run -n dzt ...`。若项目另有环境说明，则按项目环境覆盖。
   - 需要依赖：`pdftotext`、Python `PyMuPDF`。缺依赖时先询问用户再安装。

2. **确认标题并重命名会话**
   - 从 PDF 首页、arXiv/DOI 页面或文件元数据确认论文标题后，立即将当前 Codex 会话标题改为 `{论文标题或通用缩写} 阅读总结`。
   - 标题过长时用论文常用缩写或 3-6 个关键词，保留可识别性，例如 `SPECTER 阅读总结`、`MLFMF 阅读总结`、`Attention Is All You Need 阅读总结`。
   - 如果当前运行环境没有会话标题工具，则跳过改名并在交付说明里提示。

3. **快速通读文本**
   ```bash
   conda run -n dzt pdftotext "/tmp/read-paper-{slug}/paper.pdf" "/tmp/read-paper-{slug}/paper.txt"
   ```
   - 用纯文本建立标题、作者、摘要、章节、贡献和结论的全局结构。
   - 主动检索：`contribution`、`we propose`、`we introduce`、`conclusion`。
   - 主动检索例子：`example`、`case study`、`toy`、`qualitative`、`failure case`。
   - 主动检索实验设置：`experiment setup`、`implementation details`、`datasets`、`metrics`、`baselines`、`hyperparameters`、`training details`、`inference`、`prompt`、`compute`、`random seed`、`split`。

4. **视觉精读 PDF**
   - 必须看首页、方法图、pipeline/architecture 图、结果表、示例图、定性结果、核心公式。
   - 必须扫实验设置表和附录设置；dataset split、baseline、metric、hyperparameter、compute、prompt template 经常在附录。
   - 不要只依赖 `pdftotext` 理解图、表、公式。

5. **提取图片资产**
   ```bash
   conda run -n dzt python scripts/extract_pdf_assets.py "/tmp/read-paper-{slug}/paper.pdf" \
     --out "/tmp/read-paper-{slug}/images" \
     --pages 2,3,8,17 \
     --markdown-prefix "attachments"
   ```
   - `figures/`：按 Figure caption 裁剪的论文图，优先用于正文。
   - `embedded/`：PDF 内嵌位图，可能是碎片，必要时人工筛选。
   - `fullpages/`：指定页整页渲染，用于复杂表格或裁剪失败回退。
   - `manifest.json`：每张图的页码、caption、裁剪框、置信度、`placement_hint`。
   - `markdown_snippets.md`：可复制的图片 Markdown 片段。
   - 插图前打开关键图片复核；`confidence=low` 或明显错裁时改用整页图或重渲染关键页。

6. **写 Markdown 解读**
   - 写作前读取 `references/document_template.md`。
   - 必备内容：论文信息、摘要、主要贡献、图表索引、背景、问题定义、方法、论文关键例子、实验设置、实验结果、局限性、总结与个人评价。
   - 图片放置：method 图放方法；qualitative/example/failure 图放关键例子；result/ablation/comparison 图放实验；不确定的图按 caption 和正文首次引用位置判断。
   - 在最终输出目录中写 Markdown；只复制最终文档需要长期引用的精选图到 `attachments/`，并在正文中使用 `attachments/...` 相对路径。
   - 用户要求全量保留图片时，复制全部 `figures/` 到 `attachments/figures/`，并在图表索引中列出。

7. **交付说明**
   - 告知最终输出目录和临时处理目录；Markdown 文件和 `attachments/` 都在最终输出目录内。
   - 如有低置信度图片、未插入正文的 Figure、论文未说明的实验设置字段，交付时说明。

## 必须做

- 用视觉方式读图表和公式，关键数字回到 PDF 原页核对。
- 区分论文原意与个人评价；主观判断放到个人评价或局限性中。
- 完整保留论文自述或归纳的 Contributions。
- 系统整理原文例子，说明例子支撑的概念、方法或结论。
- 完整保留 experiment setting：任务、数据集、数据划分、指标、baselines、模型规模、训练/推理配置、超参数、计算资源、随机种子/重复次数、实现与复现细节。
- 识别论文标题后更新当前会话标题，格式为 `{论文标题或通用缩写} 阅读总结`。
- 最终 Markdown 的行内公式使用 `$...$`，独立公式使用 `$$...$$`。
- 术语首次出现给中英文，后文保持一致。

## 禁止做

- 不臆造数字、例子、实验设置或代码/数据链接；缺失信息写“论文未说明”。
- 不把自己补充的类比标成论文例子；如需补充，明确写“我的补充例子”。
- 不盲插 `manifest.json` 候选图；插入前至少复核关键图。
- 不在最终 Markdown 中使用 `\(...\)` 或 `\[...\]` 作为公式定界符；交付前搜索确认正文无残留。
- 不把临时 PDF、提取中间文件或无关图片放进 Obsidian Vault 或仓库。

## 资源

- `scripts/extract_pdf_assets.py`：提取 Figure 裁剪图、嵌入图、整页渲染、manifest 和 Markdown snippets。
- `references/document_template.md`：最终中文论文解读文档模板。
