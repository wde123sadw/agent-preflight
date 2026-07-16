# Agent Preflight

**先把任务想清楚，再把能力配齐，审核后再执行。**

Agent Preflight 是一套面向 AI Agent 的自适应预检技能包。它帮助 Agent 判断什么时候该直接执行、什么时候先检查环境、什么时候需要澄清需求、是否真的缺少能力、应该去哪里寻找工具、哪些新增能力必须交给用户审核，以及如何在不丢失关键证据的前提下节省上下文 Token。

## 六个 Skill

- `using-agent-preflight`：元路由，根据任务选择最小必要流程。
- `intent-preflight`：从相关专业视角澄清真正影响方案的问题。
- `capability-gap-analysis`：先盘点现有能力，再确认缺口。
- `tool-discovery`：针对明确能力缺口，从可信来源寻找候选工具。
- `tool-review-gate`：审核来源、权限、数据路径、费用、维护和回滚。
- `context-budget`：先过滤和选择，再按需摘要、压缩和取回原文。

## 关键原则

- 简单任务不提问、不展示繁琐流程。
- 能从代码、文档、配置或已安装工具中找到的信息，先自行检查。
- 没有证明存在能力缺口之前，不搜索新工具。
- 只读发现不等于安装授权。
- 安装、认证、发送数据、全局配置、付费、发布、部署、删除和迁移必须得到明确批准。
- 工具出现在注册表或拥有很多 Star，不代表已经通过安全审核。
- 节省 Token 时先减少无关输出，再考虑压缩；关键决策必须能够取回原始证据。

## 安装与验证

Windows Codex：

```powershell
./scripts/install.ps1
```

验证技能包：

```bash
python scripts/validate_pack.py
python scripts/run_evals.py --check
```

当前版本为 `v0.1.0`，重点验证“该问才问、缺什么才找、审核后才装”。
