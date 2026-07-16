# Professional Lenses

Use lenses to generate distinct decisions, not theatrical personas.

## Core lenses

| Lens | Look for |
|---|---|
| User | job to be done, context, pain, frequency, recovery, comprehension |
| Product | outcome, priority, scope, success metric, adoption, exclusions |
| Engineering | architecture, contracts, compatibility, failure behavior, maintainability |
| Design | flow, information hierarchy, states, feedback, responsive behavior |
| Testing | happy path, boundaries, failure paths, regression surface, evidence |
| Security and privacy | identity, authorization, secrets, data classification, abuse, audit |
| Operations | deployment, observability, capacity, rollback, recovery, ownership |
| Data | source, quality, schema, lineage, retention, accuracy, interpretation |
| Business | cost, revenue, licensing, vendor dependency, operational burden |
| Accessibility | keyboard, screen reader, contrast, motion, language, cognitive load |
| Domain expert | regulations, professional conventions, safety limits, terminology |

## Suggested bundles

### Software feature

Start with user, product, engineering, and testing. Add security for auth, input, storage, payments, or integrations. Add operations for production services.

### Bug diagnosis

Start with user impact, engineering reproduction, testing evidence, and operations telemetry. Ask product questions only when expected behavior is unclear.

### Content or creative work

Start with audience, product goal, creative direction, delivery constraints, rights, and acceptance. Add tool capability only after format and quality are clear.

### Research or data analysis

Start with decision purpose, data/source quality, method, uncertainty, reproducibility, and output format.

### Automation

Start with operator, trigger, inputs, permissions, idempotency, failure recovery, observability, and external effects.

### High-risk operation

Always include owner, authorization, blast radius, backup, rollback, audit evidence, and stop conditions.

## Deduplication rule

Merge questions that seek the same decision. For example, “What does success look like?” from product and “How will we test it?” from QA should become one acceptance question when the answers are equivalent.
