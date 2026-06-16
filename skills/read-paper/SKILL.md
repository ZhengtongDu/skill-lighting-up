---
name: read-paper
description: 阅读一篇学术论文（通常为 PDF），提取论文中的关键图片/图表资产，并整理为结构化中文解读文档（Markdown，可用 ReText 编辑）。适用于论文精读、组会/分享班、文献调研；覆盖作者团队、贡献、背景、问题定义、方法、论文例子、实验、局限性与个人评价。不包含 PPT 制作。
---

# 读论文：把一篇论文整理成结构化中文解读

## 用途

输入一篇论文（PDF 或链接），输出一份**结构化的中文解读文档**（Markdown 格式，可直接用 ReText 打开编辑预览）。

目标读者是中文母语者，希望在不读完英文原文的情况下，通过这份文档完整理解论文：作者是谁、为什么做、解决什么问题、怎么做的、效果如何、有什么不足。

> 本 skill **只负责"读 + 整理成文档"**，不负责制作 PPT。如果后续要做分享 PPT，那是另一个独立步骤。

## 何时使用

- 用户给出一篇论文 PDF / arXiv 链接，要求"整理 / 精读 / 翻译 / 解读"
- 组会、论文分享班、文献综述前的论文研读
- 需要快速吃透一篇陌生论文的核心贡献与方法

## 核心原则

1. **图表必须用视觉方式读**。`pdftotext` 提取的纯文本会丢失图、表、公式的版面结构（表格会变成错乱的数字流，公式会乱码）。因此**先用纯文本快速通读，再用 Read 工具按页"看"PDF**，尤其是含架构图、流程图、结果表的页面。
2. **先理解再翻译**。不要逐句直译。先抓住论文的逻辑骨架（问题 → 方法 → 实验 → 结论），再用通顺的中文重述。专业术语保留英文原文并附中文（如"边界框（Bounding Boxes）"）。
3. **结构化输出**。固定的章节模板（见下文），让不同论文的解读文档保持一致风格，便于对比与归档。
4. **区分"论文说的"与"我的评价"**。客观转述论文内容时如实表达；个人评价、质疑、延伸思考要单独成节并明确标注，不要混入论文原意。
5. **保留可追溯的关键数字**。实验结果的核心指标、数据规模、压缩比等关键数字要准确保留，必要时做成 Markdown 表格。
6. **系统整理论文中的例子**。论文里的 illustrative examples、running examples、case studies、toy examples、qualitative examples 往往是理解方法和概念的关键。精读时必须尽可能全量检索并整理原文提到的例子，说明例子想表达什么、对应哪个概念/方法/结论，并把这些例子放进最终文档作为讲解内容的一部分；重要例子详写，次要例子可列表概括。
7. **论文基本信息必须齐全**。论文信息不仅包括标题、作者、单位、发表信息、链接、代码/数据，还必须包括论文自述的主要贡献（Contributions）。优先按原文贡献列表组织；如果原文没有显式 Contributions 小节，则从摘要、引言和结论中归纳，并明确说明是归纳。
8. **图片要带语义进入文档**。不要只把 PDF 里的裸图片堆到附件。优先提取带 Figure caption、页码、裁剪置信度和 placement hint 的图片资产；写 Markdown 时把 pipeline/architecture 图放到方法部分，把 qualitative/example/failure case 图放到论文例子部分，把 result/ablation/comparison 图放到实验部分。
9. **实验设置必须完整保留**。实验设置（experiment setting / setup / implementation details / evaluation protocol）是判断论文可信度和可复现性的关键，最终文档必须单独整理并保留。至少检查数据集与任务、数据划分、评估指标、对比方法、模型规模、训练/推理配置、超参数、计算资源、随机种子/重复次数、实现细节、prompt 或 decoding 设置；论文没写清的字段要标注"论文未说明"，不要省略。

## 工作流程

### 步骤 0：定位论文与环境检查

- 默认最终输出目录：用户 Obsidian Vault 根目录下的 `ReadPaper/`，本文档用 `<Obsidian Vault>/ReadPaper` 表示。
- 不要在 skill 源文件或提交到 GitHub 的内容中硬编码本机绝对路径（例如用户主目录、同步盘目录）。实际执行时再根据用户当前机器解析 `<Obsidian Vault>`。
- 下载的论文 PDF、`pdftotext` 导出的文本、提取/渲染图片等处理过程文件统一放到 `/tmp/read-paper-<英文短标题>/`，不要放进工作目录或 Obsidian Vault。
- 如果输入是链接，先把 PDF 下载到 `/tmp/read-paper-<英文短标题>/paper.pdf`；如果输入是本地 PDF，可直接读取原文件，或复制到该 `/tmp` 目录作为工作副本。
- 在工作目录或用户给定位置中找到 PDF（`find . -name "*.pdf"` 或用搜索工具）。
- 确认工具可用：`pdftotext`（来自 poppler）、Python 的 `PyMuPDF`(fitz)、`Pillow`。
  - 缺失时安装：`pip3 install --user --break-system-packages PyMuPDF Pillow`
  - `pdftotext` 通常随 poppler 提供（macOS: `brew install poppler`）。
- 若用户要求用 ReText 编辑，确认 `retext` 已安装（`pip3 install --user --break-system-packages retext`），其可执行文件常在 `~/Library/Python/<ver>/bin/retext`。

### 步骤 1：快速通读（纯文本）

```bash
pdftotext "/tmp/read-paper-<英文短标题>/paper.pdf" "/tmp/read-paper-<英文短标题>/paper.txt"
```

目的：快速建立全局印象——标题、作者、摘要、章节结构、贡献点、结论。**不要**依赖此步骤理解图表和公式。

主动检索论文贡献相关表述，例如 `contribution`、`our contributions`、`main contributions`、`we introduce`、`we propose`、`we make the following`、`in summary`、`conclusion`，以及中文论文中的"贡献"、"主要贡献"、"本文提出"、"总结如下"。记录原文贡献点，不要只凭摘要泛泛概括。

同时检索论文中的例子线索，例如 `for example`、`e.g.`、`example`、`case study`、`illustration`、`toy example`、`running example`、`qualitative example`、`failure case`、`as shown in Figure/Table`，以及中文论文中的"例如"、"例子"、"案例"、"示例"、"如图"。记录例子所在章节/页码、原文例子内容、它用来说明的概念，以及最终文档中应放在哪个部分。

同时检索实验设置线索，例如 `experiment setup`、`experimental setup`、`implementation details`、`evaluation protocol`、`datasets`、`metrics`、`baselines`、`hyperparameters`、`training details`、`inference`、`prompt`、`decoding`、`compute`、`GPU`、`random seed`、`split`、`ablation setup`，以及中文论文中的"实验设置"、"数据集"、"评价指标"、"基线方法"、"超参数"、"训练细节"、"实现细节"。把这些内容先做成摘录清单，后续写入"4.1 实验设置"。

### 步骤 2：视觉精读（按页看 PDF）

用 Read 工具分批读取 PDF 页面（每次最多约 10 页），重点看：

- **首页**：标题、完整作者列表、单位、通讯/核心作者标注、摘要。
- **架构图 / 流程图**：方法部分的 pipeline 图，通常是论文最关键的一张图。
- **结果表格**：主实验对比表，准确抄录关键数字。
- **示例图 / 定性结果**：帮助理解方法的实际效果。
- **公式**：核心损失函数、奖励函数等。
- **论文例子**：检索并核对原文中用于解释概念/定义/方法/失败案例的例子。优先搜索 "for example", "e.g.", "example", "case study", "illustration", "toy", "qualitative", "running example" 等线索；对中文论文也搜索"例如"、"例子"、"案例"、"示例"。不要只摘录，要解释这个例子支撑了什么观点。
- **实验设置表 / 附录设置**：许多论文把 dataset split、baseline、metric、hyperparameter、compute 或 prompt template 放在附录。视觉精读时必须扫实验设置相关表格和 appendix，不要只看主结果表。

### 步骤 3：提取图片（供文档/后续引用）

运行 `scripts/extract_pdf_assets.py` 提取 Figure 裁剪图、嵌入位图、可选整页渲染，并生成 manifest：

```bash
python3 scripts/extract_pdf_assets.py "/tmp/read-paper-<英文短标题>/paper.pdf" \
  --out "/tmp/read-paper-<英文短标题>/images" \
  --pages 2,3,8,17 \
  --markdown-prefix "attachments/read-paper-<英文短标题>"
```

- `figures/`：按 `Figure` / `Fig.` caption 自动裁剪的论文图，包含矢量图和嵌入图；优先用于最终 Markdown。
- `embedded/`：PDF 内部嵌入位图，可能是碎片、小图或无语义图片；只在 Figure 裁剪不够时人工筛选。
- `fullpages/`：`--pages` 指定页的整页 PNG，用于复杂表格、跨栏图或低置信度回退。
- `manifest.json`：每张 Figure 的页码、caption、裁剪框、置信度、`placement_hint`、Markdown 路径。
- `markdown_snippets.md`：可复制进正文的图片 Markdown 片段。

读 `manifest.json` 时按 `placement_hint` 决定初始放置：

- `method`：放到"3. 方法"中对应机制旁边，常见于 architecture、pipeline、framework、overview。
- `examples`：放到"论文中的关键例子"，常见于 qualitative example、case study、failure case。
- `experiments`：放到"4. 实验"，常见于 result、comparison、ablation、performance。
- `background`：放到"1. 背景与动机"或"2. 问题定义"。
- `near-related-section`：结合 caption 和正文首次引用位置人工判断。

必须打开并视觉复核重要图片，尤其是 `confidence=low` 的图片。若裁剪不准，用 `fullpages/` 整页图或重新指定 `--pages` 渲染关键页；不要把明显错裁、空白、只含正文的图塞进最终文档。

### 步骤 4：撰写结构化中文文档

按下面的模板写成一个 `.md` 文件。命名建议：`论文解读_<英文短标题>.md`，保存到：

```text
<Obsidian Vault>/ReadPaper/论文解读_<英文短标题>.md
```

如果最终文档需要长期引用图片，只把精选图片复制到 `<Obsidian Vault>/ReadPaper/attachments/read-paper-<英文短标题>/`，并在 Markdown 中用 `attachments/read-paper-<英文短标题>/...` 这样的相对路径引用；其余临时图片继续留在 `/tmp`。

优先把 `figures/` 中与正文讲解相关的图片复制到附件目录。若论文 Figure 很多，正文只插入理解所必需的图，其余在"论文图表索引"中列出；若用户明确要求全量保留，则把全部 `figures/` 复制到附件目录，并在索引中逐张列出。

```markdown
# <中文标题> —— <英文原标题>

## 论文信息
- 标题 / 团队 / 核心贡献者 / 其他作者 / 发表信息 / 链接 / 代码与数据

## 摘要
（通顺的中文重述，不逐句直译）

## 主要贡献（Contributions）
- 按论文原文的贡献列表整理；如果原文没有显式列表，则基于摘要、引言和结论归纳，并标注为"我归纳的贡献"。
- 每条贡献写清：做了什么、相对已有工作的新增点是什么、用什么数据/方法/实验支撑。

## 论文图表索引
- Figure 1（page x，method）：caption 摘要；正文放置位置：3.x。
- Figure 2（page y，examples）：caption 摘要；正文放置位置：3.x 论文中的关键例子。

## 1. 背景与动机
- 领域现状
- 现有方法的局限

## 2. 问题定义
- 论文要解决的核心问题（用具体场景说明）

## 3. 方法
- 核心思想（一句话能讲清的 idea）
- 关键技术点（分小节，重点部分加强说明）
- 必要的公式与流程

（在首次解释 pipeline / architecture / framework 时插入对应 Figure。）

## 3.x 论文中的关键例子
（整理原文用于解释概念/方法/实验现象的例子。每个例子写清：原文例子是什么、它说明什么、为什么有助于理解论文。若例子很多，按"定义例子 / 方法例子 / 失败案例 / 定性结果"分类，并插入 qualitative / example / failure case 图片。）

## 4. 实验
- 实验设置（数据集、任务、划分、指标、对比模型、训练/推理配置、超参数、计算资源、复现细节）
- 主要结果（关键数字做成表格）
- 分析与发现

## 5. 局限性
（论文自述 + 你观察到的）

## 6. 总结与个人评价
- 论文贡献总结
- 创新性 / 技术亮点 / 可讨论的问题（明确标注为个人观点）
- 未来方向
```

### 步骤 5：交付与可编辑性

- 文档为标准 Markdown，可直接用 ReText 打开：
  ```bash
  retext "<Obsidian Vault>/ReadPaper/论文解读_xxx.md"
  ```
- 告知用户最终文档路径、持久图片附件目录、临时 PDF 与处理文件目录。若有低置信度图片或未插入正文的 Figure，也要说明。

## 注意事项

- **术语一致性**：同一术语全文用法统一（首次出现给中英文，之后可只用其一）。
- **不臆造数字**：拿不准的指标回到 PDF 原页核对，不要凭印象写。
- **不臆造例子**：只把论文中实际出现的例子标为"论文例子"；如果为了帮助理解额外补充自己的类比，必须明确标注为"我的补充例子"，不要和原文例子混在一起。
- **例子要讲清用途**：不要只摘录例子本身，还要说明它在论文中用于定义概念、解释方法、展示能力、支撑结论，还是暴露失败模式。
- **实验设置不能省略**：即使用户主要关心方法，也要在最终文档保留实验设置。没找到的信息写"论文未说明"或"未在主文中找到，可能在附录/代码中"，不要留空。
- **图片不要盲插**：`manifest.json` 是候选放置建议，不是最终判断。插入正文前至少打开关键 Figure 看一眼，确认裁剪包含完整视觉内容且与 caption 一致。
- **中文标点**：正文用中文标点；代码、公式、特殊 token（如 `<|box|>`）保持原样。
- **避免 Python 字符串里嵌套引号的坑**：若后续写脚本处理中文文本，注意中文引号 `"" `与 ASCII `"` 的冲突，正文里建议用「」避免歧义。
- **大文件 / 长论文**：超过 20 页的论文，分批读取 PDF，并优先聚焦方法与实验两章。

## 文件清单

- `SKILL.md`：本说明。
- `scripts/extract_pdf_assets.py`：从 PDF 提取嵌入图 + 渲染指定页面为 PNG。
- `references/document_template.md`：可直接复制的中文解读文档模板。
