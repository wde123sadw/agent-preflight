# Contributing

Contributions should improve a measurable behavior: fewer unnecessary questions, fewer missed material questions, better capability reuse, safer tool review, lower context cost, or stronger verification.

## Change process

1. Add or update behavior cases in `evals/cases.jsonl`.
2. Make the smallest skill or reference change that addresses them.
3. Run `python scripts/validate_pack.py`.
4. Run `python scripts/run_evals.py --check`.
5. Explain the behavior change and any new approval boundary in the pull request.

Keep each `SKILL.md` procedural and concise. Put detailed matrices and examples in its `references/` directory. Do not add a tool recommendation based only on popularity.
