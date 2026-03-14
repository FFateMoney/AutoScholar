# AutoScholar

AutoScholar v2 is a structured scholarly workflow toolkit built for agent-driven research support.

It is designed as:

- an installable Python package
- a unified `autoscholar` CLI
- a skill-oriented repository for LLM agents
- a workspace-based system that keeps task data outside the core repo by default

## Install

```powershell
python -m pip install -e .[test]
```

## Quick Start

Initialize a workspace:

```powershell
autoscholar workspace init D:\workspaces\demo --template citation-paper --reports-lang zh
```

Run the citation workflow:

```powershell
autoscholar citation search --workspace D:\workspaces\demo
autoscholar citation prescreen --workspace D:\workspaces\demo
autoscholar citation correct --workspace D:\workspaces\demo
autoscholar citation shortlist --workspace D:\workspaces\demo
autoscholar citation bib --workspace D:\workspaces\demo
autoscholar report render --workspace D:\workspaces\demo --kind prescreen
autoscholar report render --workspace D:\workspaces\demo --kind shortlist
```

Run the idea-evaluation workflow:

```powershell
autoscholar workspace init D:\workspaces\idea-demo --template idea-evaluation --reports-lang zh
autoscholar citation search --workspace D:\workspaces\idea-demo
autoscholar citation prescreen --workspace D:\workspaces\idea-demo
autoscholar citation correct --workspace D:\workspaces\idea-demo
autoscholar citation shortlist --workspace D:\workspaces\idea-demo
autoscholar idea assess --workspace D:\workspaces\idea-demo
autoscholar report render --workspace D:\workspaces\idea-demo --kind feasibility
autoscholar report render --workspace D:\workspaces\idea-demo --kind deep-dive
```

## Workspace Model

Every workspace is explicit and self-contained. `autoscholar workspace init` creates:

- `workspace.yaml`
- `inputs/`
- `configs/`
- `artifacts/`
- `reports/`

The manifest is the single source of truth for logical paths. AutoScholar no longer depends on repo-local `paper/`, `idea_eval/`, or `old_paper/` directories.

## Skills

AutoScholar ships with four skills:

- `.agents/skills/autoscholar`
- `.agents/skills/citation-workflow`
- `.agents/skills/idea-evaluation`
- `.agents/skills/semantic-scholar-api`

The top-level `autoscholar` skill explains capability routing. The workflow skills explain how to combine commands and structured artifacts. The API skill is for low-level Semantic Scholar operations and debugging.

## Structured Artifacts

Standard machine-readable artifacts include:

- `artifacts/claims.jsonl`
- `artifacts/queries.jsonl`
- `artifacts/search_results.raw.jsonl`
- `artifacts/search_results.deduped.jsonl`
- `artifacts/query_reviews.json`
- `artifacts/recommendation_corrections.jsonl`
- `artifacts/selected_citations.jsonl`
- `artifacts/idea_assessment.json`
- `artifacts/references.bib`

Markdown files in `reports/` are rendered from these structured artifacts and are not treated as the source of truth.

## CLI Surface

Primary commands:

- `autoscholar workspace init`
- `autoscholar workspace doctor`
- `autoscholar citation search`
- `autoscholar citation prescreen`
- `autoscholar citation correct`
- `autoscholar citation shortlist`
- `autoscholar citation bib`
- `autoscholar idea assess`
- `autoscholar report render`
- `autoscholar schema export`

## Example

A small tracked example workspace lives under [`examples/idea-evaluation-demo`](/d:/pythonProject/AutoScholar/examples/idea-evaluation-demo).
