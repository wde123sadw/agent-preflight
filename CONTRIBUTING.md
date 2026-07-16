# Contributing

Contributions should improve a measurable behavior: fewer unnecessary questions, fewer missed material questions, better capability reuse, safer tool review, lower context cost, or stronger verification.

## Change process

1. Add or update behavior cases in `evals/cases.jsonl`.
2. Make the smallest skill or reference change that addresses them.
3. Run `python scripts/validate_pack.py`.
4. Run `python scripts/run_evals.py --check`.
5. Run `python -m unittest discover -s tests -v`.
6. For routing changes, run the fast trace regression and attach representative raw outputs.
7. For product-effect claims, run paired control/preflight trials, keep reviewers blind, and attach the unblinded report plus protocol details.
8. Explain the behavior change and any new approval boundary in the pull request.

Keep each `SKILL.md` procedural and concise. Put detailed matrices and examples in its `references/` directory. Do not add a tool recommendation based only on popularity.

Do not tune expected cases, review scores, hard-failure definitions, or release thresholds after seeing which arm won. Negative and inconclusive experiments are valid results and should remain visible.
