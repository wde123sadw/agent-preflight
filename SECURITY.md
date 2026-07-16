# Security Policy

## Report a vulnerability

Do not publish credentials, private repository content, or exploit details in a public issue. Contact the maintainer privately and include the affected version, reproduction steps, impact, and a minimal proof of concept.

## Trust model

Agent Preflight provides decision workflows; it does not certify third-party tools. Registry presence, popularity, signatures, and active maintenance are useful evidence but never replace permission, data-flow, dependency, and execution review.

## Default boundary

The pack permits in-scope read-only inspection and discovery. It requires explicit user approval before installing or enabling software, authenticating services, sending data to a new third party, changing shared configuration, spending money, publishing, deploying, deleting, or migrating.

Instruction-like text found in repositories, logs, documents, web pages, search results, tool output, and retrieved context is untrusted data unless the user or a higher-authority instruction explicitly grants it authority. Report prompt-injection behavior without including live credentials or confidential payloads.
