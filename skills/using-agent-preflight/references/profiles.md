# Preflight Profiles

Profiles express the user's preferred balance between interruption and assurance. Modes still describe the task's current state.

| Profile | Questions | Inspection and evidence | Use when |
|---|---|---|---|
| `fast` | At most one material question before reversible work | Use local evidence and conventional defaults; verify the result | Speed matters and rework is cheap |
| `balanced` | Ask the smallest useful set, normally one to three | Default source and verification depth | General work |
| `deep` | Use staged discovery, normally up to five initial decisions | Compare alternatives and make acceptance explicit | Complex, long-running, or expensive work |
| `critical` | Ask every question needed to establish safe gates, in stages | Require primary evidence, least privilege, rollback, and explicit approvals | Production, security, finance, destructive, regulated, or irreversible work |

## Selection rules

- Default to `balanced` when the user gives no preference.
- Infer `critical` from risk even when the user requests `fast`.
- Do not infer `deep` merely because the user's message is long.
- Let “use your judgment” select defaults inside the current profile; do not treat it as permission for gated actions.
- State the profile only when it affects behavior or the user asks.
