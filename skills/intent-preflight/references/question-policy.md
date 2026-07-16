# Question Policy

## Question budgets

Use these as ceilings, not quotas:

| Situation | Initial budget |
|---|---:|
| Clear and reversible | 0 |
| One material ambiguity | 1 |
| Medium feature or deliverable | 2–3 |
| Complex multi-stage work | 3–5 |
| High-risk or irreversible work | Ask the minimum required to establish safe gates; continue in stages |

Do not dump a complete discovery questionnaire into one message.

## Ask about decisions, not categories

Weak: “What are your technical requirements?”

Strong: “Should existing API clients continue working unchanged? I recommend treating backward compatibility as required unless this is a private prototype.”

Weak: “Who is the user?”

Strong: “Is the first release for internal operators or paying customers? That changes the permission model and the amount of UX polish.”

## Attach useful defaults

Use this form when a safe default exists:

```text
Question: <decision>
Recommended default: <choice>
Why it matters: <one sentence>
```

Avoid leading guesses when the topic is sensitive, the user may be vulnerable, or agreement bias would hide true preferences.

## Skip a question when

- the answer is in the workspace or authoritative source;
- either answer leads to the same implementation;
- the choice is reversible and a conventional default is safe;
- the user explicitly delegated the choice;
- the question is merely an opportunity to display expertise;
- the task can be safely prototyped to produce better evidence.

## Escalate a question when

- different answers change data, permissions, external behavior, or compatibility;
- the action consumes money or scarce generation credits;
- the action is destructive or difficult to roll back;
- legal, policy, safety, or brand responsibility belongs to the user;
- the agent sees conflicting authoritative evidence.
