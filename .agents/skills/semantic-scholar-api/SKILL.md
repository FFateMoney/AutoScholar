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
- author search
- author papers

## Notes

- The client reads `S2_API_KEY` when present.
- Without an API key, expect lower rate limits.
- Prefer explicit `fields` to keep responses small.
