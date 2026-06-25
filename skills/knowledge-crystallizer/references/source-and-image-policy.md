# Source and image policy

## Source collection

During the Plan stage, collect sources before finalizing the outline. Prefer a mix of:

- Chinese learning sources: Zhihu, personal blogs, technical communities, course notes, Juejin, CSDN only when the article is concrete and source-backed.
- Authoritative sources: papers, official docs, textbooks, university course notes, reputable lecture videos/slides, canonical library docs.
- Implementation sources: official examples, library docs, well-maintained repositories, reproducible notebooks.

For each useful source, record:

| Field | Requirement |
|-------|-------------|
| title | Article, paper, docs page, or post title |
| author / org | Author, institution, account, or unknown |
| URL | Direct link |
| date | Published date if visible, otherwise access date |
| source type | Zhihu / blog / paper / docs / course / repo |
| credibility | high / medium / low with one short reason |
| reusable content | example, formula, image idea, code idea, warning, citation |

## Source quality

- Prefer primary sources for definitions, formulas, benchmark numbers, model claims, APIs, and dates.
- Use blogs and Zhihu mainly for intuition, alternative examples, common confusions, and diagrams to redraw.
- If a Chinese article is useful but source quality is weak, mark it as inspiration rather than authority.
- If sources disagree, explain the disagreement instead of forcing a single conclusion.
- Do not cite search snippets as if the article was read. If access fails, mark it as `unread / inaccessible`.

## Copyright and quoting

- Do not copy long passages from any article.
- Use short quotes only when wording matters, and keep them brief.
- Paraphrase in original Chinese prose and cite the source.
- Never present a blog author's example as if it were invented by Codex. Say it is adapted from that source.

## Image policy: cite and redraw

Default strategy: **引用 + 重画**.

1. When an online diagram is useful, save its source URL and describe what it teaches.
2. Do not download or embed copyright-unclear images directly.
3. Redraw an equivalent original diagram when it materially helps the note.
4. Keep the redrawn diagram simpler than the source, focused on the concept.
5. Caption the image with wording like:

```markdown
图：{diagram description}。结构参考自 {source title}，已重新绘制。
```

6. Store generated or redrawn assets under:

```text
Concept Collections/attachments/{slug}/
```

## Python examples from sources

- Prefer writing a fresh minimal example over copying code.
- If adapting code from docs or a blog, cite the source near the code block.
- Verify the example locally when possible.
- If exact library versions matter, mention them.

## Final reference section

Use simple Markdown references:

```markdown
## 参考资料

- Author / Org. Title. URL. Published or accessed date. 用途：定义 / 公式 / 例子 / 图示灵感 / 实现参考。
```
