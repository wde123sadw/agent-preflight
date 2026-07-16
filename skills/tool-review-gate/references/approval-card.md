# Approval Card

```text
TOOL APPROVAL CARD

Candidate: <name and exact version/source>
Purpose: <proven capability gap>
Recommendation: APPROVE | APPROVE WITH CONDITIONS | FALLBACK | DO NOT APPROVE

What will change:
- Install/enable: <scope and files/config>
- Access: <permissions/accounts>
- Data: <what leaves the machine and destination>
- Cost: <price/quota exposure>
- External effects: <resources/messages/deployments/etc.>

Risk review:
- Source/supply chain: LOW/MEDIUM/HIGH/UNKNOWN — <evidence>
- Permissions/execution: LOW/MEDIUM/HIGH/UNKNOWN — <evidence>
- Secrets/data: LOW/MEDIUM/HIGH/UNKNOWN — <evidence>
- Cost/operations: LOW/MEDIUM/HIGH/UNKNOWN — <evidence>
- Reversibility: LOW/MEDIUM/HIGH/UNKNOWN — <evidence>

Verification plan:
1. <dry-run or isolated check>
2. <capability test>
3. <evidence of success>

Rollback:
- <uninstall, revoke, restore, and cleanup>

Alternatives:
- <existing or no-install fallback and tradeoff>

Choose one:
1. Approve exactly as described
2. Approve with these conditions: <conditions>
3. Use the fallback
4. Gather more evidence
5. Reject
```

Never hide a material unknown below the recommendation. Put it in the relevant risk line and explain what evidence would resolve it.
