---
name: semantic-scholar-api
description: Use when the user needs low-level Semantic Scholar Graph API operations inside AutoScholar, such as paper lookup, search, recommendations, citations, references, or author inspection.
---

# Semantic Scholar API

Use this skill when the task is lower-level than the full AutoScholar workflow.

## Use Cases

- inspect one paper or author directly
- debug search behavior
- debug recommendation behavior
- inspect citations and references
- fetch raw metadata before it enters a workspace workflow

## Implementation Surface

The client lives in `src/autoscholar/integrations/semantic_scholar.py`.

It supports:

- paper lookup
- batch paper lookup
- relevance search
- bulk search
- recommendations
- citations
- references
- author search
- author papers
- open-access PDF download

## CLI Surface

Use the `autoscholar semantic` command group for direct inspection and debugging:

- `autoscholar semantic paper <paper_id>`
- `autoscholar semantic search <query>`
- `autoscholar semantic recommend <paper_id>`
- `autoscholar semantic citations <paper_id>`
- `autoscholar semantic references <paper_id>`
- `autoscholar semantic author-search <query>`
- `autoscholar semantic author <author_id>`
- `autoscholar semantic author-papers <author_id>`
- `autoscholar semantic download-pdf <paper_id>`
- `autoscholar semantic smoke`

## Notes

- The client reads `S2_API_KEY` when present.
- Without an API key, expect lower rate limits.
- Prefer explicit `fields` to keep responses small.
- `autoscholar semantic smoke` skips cleanly when `S2_API_KEY` is unset.
