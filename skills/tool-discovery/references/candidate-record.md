# Candidate Record

Use one record per candidate.

```text
CANDIDATE: <name>
Type: Skill | Plugin | MCP | CLI | Library | API | Application
Canonical source: <URL>
Publisher: <owner and identity evidence>
Version / freshness: <current evidence>
License / price: <terms and expected cost>

Capability fit:
- Solves: <exact proven gap>
- Does not solve: <relevant limits>
- Verification path: <test, preview, doctor, dry-run, or evidence>

Environment fit:
- Platforms/runtimes: <requirements>
- Install scope: <project/user/system/service>
- Authentication: <none or method>
- Permissions: <filesystem/network/account scopes>
- Data path: <local, external endpoints, retention if known>
- Removal/rollback: <method>

Unknowns:
- <facts the review must resolve>

Why shortlisted:
<one decision-focused sentence>
```

Do not include an install command as a recommendation until `$tool-review-gate` has completed. A command may be quoted as evidence and must be labeled “not executed.”
