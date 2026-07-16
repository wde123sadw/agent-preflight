# Source Ladder

## Route by capability type

| Need | Start here |
|---|---|
| Existing agent action or connected data | Active tool and connector catalog |
| Agent workflow instructions | Platform skill/plugin marketplace and canonical repository |
| MCP server | Official MCP Registry: https://registry.modelcontextprotocol.io and publisher repository |
| Professional GUI software automation | Official CLI/API, then CLI-Hub: https://clianything.cc |
| Language library | Official package registry plus project documentation and repository |
| Framework implementation guidance | Documentation for the exact installed version |
| Cloud or SaaS integration | Vendor API, official SDK, official connector or marketplace |
| OS capability | Vendor-supported package manager or native utility |
| Context compression | Existing selective-read features first; then documented compression/retrieval tools |

## Evidence hierarchy

1. Official documentation for the exact version.
2. Official repository, release notes, security policy, and signed packages.
3. Official protocol registry or marketplace entry.
4. Independent reproducible benchmark or audit.
5. Maintainer discussion and issue history.
6. Community tutorial, list, social post, or star count.

Use levels 5–6 to discover questions, not to settle security or compatibility claims.

## Registry caution

Publisher identity, namespace verification, signatures, or registry inclusion reduce some supply-chain ambiguity. They do not prove that permissions are minimal, data stays local, dependencies are safe, or the tool fits the task.

## Search stop rule

Stop when one candidate meets the required capability and constraints, one meaningfully different fallback has been considered, and additional search is unlikely to change the user decision.
