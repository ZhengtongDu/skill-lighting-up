---
name: knowledge-crystallizer
description: 将最近几轮关于机器学习、深度学习、检索、优化、概率建模或相关计算概念的聊天内容沉淀为偏硬核的中文 Obsidian 概念笔记。Use when the user says "知识结晶", invokes "$knowledge-crystallizer", asks to turn prior Codex answers into a concept note, asks for a first-step plan/outline, or asks for the second-step writing of a sourced ML concept note with mathematical derivations, Python examples, references, and final humanizer polishing.
---

# Knowledge Crystallizer

## Goal

Turn useful ML-related chat into a reviewable Chinese concept note for the user's configured Obsidian Knowledge Crystals output directory.

Resolve the output directory at runtime in this order:

1. An explicit path in the current user request.
2. A local-only config file at `${CODEX_HOME:-$HOME/.codex}/knowledge-crystallizer-output-dir`.
3. An environment/config value such as `KNOWLEDGE_CRYSTALS_DIR` or `CONCEPT_COLLECTIONS_DIR`.
4. Existing project conventions.

If no destination can be inferred, ask the user for the target Obsidian Knowledge Crystals path before writing files.

Default reader profile: strong in linear algebra, mathematical analysis, and algorithms; weaker in practical CS/ML engineering. Write mainly in Chinese, give first-use English terms, and keep the final result technically dense.

## Load references

Before producing a plan or final note, read:

- `references/concept-note-template.md` for the target note structure.
- `references/source-and-image-policy.md` for web source, citation, and image redraw rules.

## Stage selection

- If the user explicitly says `plan`, `第一步`, `只要大纲`, `先别写文档`, or asks only what should be written, run the **Plan stage** and do not write a file.
- Otherwise, run the **Write stage**. Direct invocations such as `知识结晶：{concept}` or `$knowledge-crystallizer {concept}` must create a Markdown file automatically.
- If no accepted plan is available during Write stage, build a compact internal plan first, then continue writing without stopping unless the concept or output directory is genuinely unknown.

## Plan stage

Produce a decision-ready writing plan, not the final article.

1. Extract the concept, user confusion points, useful explanations, formulas, examples, and terminology from recent chat context.
2. Use web research. Search Chinese learning sources such as Zhihu, personal blogs, technical communities, and course notes, plus authoritative sources such as papers, official docs, textbooks, and university materials. If browsing or network access is blocked, report that limitation and do not fabricate sources.
3. Use as many independent agents as practical. In Codex, if sub-agent tools are not already active and `tool_search` is available, search for multi-agent tools first. If multi-agent tools are available, parallelize these roles; if not, perform the same roles sequentially:
   - Chat extraction agent: summarize the relevant conversation and unresolved questions.
   - Mathematical derivation agent: design the path from definition to objective, matrix/probability form, gradient, or algorithm.
   - Prerequisite agent: identify missing CS/ML background and where to insert it without weakening the math.
   - Chinese source agent: collect Chinese articles, Zhihu posts, blogs, tutorials, and reusable explanations.
   - Authoritative source agent: collect papers, official docs, course notes, textbooks, and canonical references.
   - Python demo agent: design a minimal runnable NumPy or PyTorch example with inputs, shapes, outputs, and expected behavior.
   - Example and figure agent: find strong examples and candidate diagrams to cite and redraw.
4. Output the plan with:
   - proposed title and filename;
   - final outline;
   - mathematical derivation route;
   - Python example design;
   - source package with URLs and credibility notes;
   - figure/image redraw plan;
   - Write-stage agent assignment;
   - risks, missing facts, and questions only if truly blocking.

## Write stage

Write the final Markdown note using the accepted plan.

1. Read the plan and references. If no plan is available, run a compact internal Plan stage first and continue writing.
2. Use independent agents where practical:
   - definition and problem background;
   - mathematical derivation;
   - Python implementation;
   - intuition and real ML examples;
   - source integration and citations;
   - fact checking.
3. Keep the mathematical layer substantial:
   - define symbols and tensor shapes before formulas;
   - derive objectives, updates, gradients, probability identities, or matrix forms when relevant;
   - connect each formula to an algorithm step;
   - state assumptions and edge cases.
4. Include a minimal Python example for ML topics:
   - prefer NumPy for core math;
   - use PyTorch when autograd, neural networks, tensors, or training loops are central;
   - do not install packages;
   - verify runnable code with the user's configured Python environment in a temporary working directory outside the repository;
   - if code cannot be run, label it as `示意代码` and explain why.
5. Follow the source and image policy:
   - cite every factual claim that depends on web or paper sources;
   - do not copy long passages;
   - cite original articles when borrowing an example;
   - redraw useful diagrams or create equivalent original figures instead of copying copyright-unclear images.
6. Final polish:
   - invoke `$humanizer` if available, asking it to preserve formulas, code, citations, and technical density;
   - if `$humanizer` is unavailable, do a final anti-AI pass manually;
   - remove generic motivational conclusions, empty signposting, over-bolded list headers, and padded prose.
7. Write the final file directly under the resolved Obsidian Knowledge Crystals output directory:

```text
{Knowledge Crystals}/{概念中文名} ({English Name}).md
```

8. Handle images with stable relative paths:
   - derive a filesystem-safe `{slug}` from the concept title;
   - create `{Knowledge Crystals}/attachments/{slug}/` before saving any image;
   - place self-made or redrawn images in that directory;
   - use only relative Markdown links in the note, never absolute local paths.

```text
{Knowledge Crystals}/attachments/{slug}/
```

Use relative paths such as `attachments/{slug}/figure-name.png`.

After writing, verify every Markdown image link points to an existing file under `{Knowledge Crystals}`. Fix broken links before delivery.

## Output quality checklist

Before delivery, verify:

- The note is Chinese-first and technically dense.
- Terms have Chinese and English names on first use.
- The math notation is consistent.
- Tensor shapes are explicit where helpful.
- At least one core derivation is present unless the concept is non-mathematical.
- ML topics include a minimal Python example or a clear reason why not.
- Code blocks are tested or explicitly marked as illustrative.
- Web sources include URLs and source notes.
- Borrowed figures are cited and redrawn rather than copied.
- The final Markdown can be read naturally after humanizer polishing.

## Do not

- Do not invent citations, examples, numbers, dates, benchmark results, formulas, or paper claims.
- Do not download or embed copyright-unclear images directly.
- Do not install packages, change Conda environments, delete files, or alter global Codex config without explicit user approval.
- Do not weaken formulas, code, or precise technical terms during humanizer polishing.
