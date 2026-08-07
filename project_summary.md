# Project Summary

## Repository structure

- `plugins/youzan-toolkit/`: Codex plugin manifest and reusable Youzan Cloud skills.
- `plugins/youzan-toolkit/skills/yzy-knowledge-search/`: Youzan Cloud documentation and knowledge search skill.
- `scripts/`: repository-level maintenance scripts.
- `docs/`: plugin documentation.

## Current work: yzy-knowledge-search runtime integration

- Base commit: `22b1abc3f923bf2225cf8fb54506fc8310dee300` from `origin/main`.
- Branch: `codex/yzy-knowledge-search-runtime`.
- The search script now hydrates the first search result from its downloadable Markdown source and returns a query-relevant `sourceExcerpt`.
- Single-question usage defaults to three search results and recommends `--no-navigation` to reduce latency and irrelevant navigation output.
- Skill guidance limits one question to one normal search, with at most one retry after an empty, failed, or clearly irrelevant result.
- Unit coverage lives in `plugins/youzan-toolkit/skills/yzy-knowledge-search/tests/test_search_knowledge.py`.

## Verification

- `python3 -m unittest discover -s plugins/youzan-toolkit/skills/yzy-knowledge-search/tests -v`
- Exact API query verification confirms the hydrated source contains the `tid` request parameter and marks it optional.

## Release boundary

- The branch must be published as a new AI Infra Skill version and validated in QA before merging to `main` or deploying the Agent to production.
