# Dual-Agent Git Workflow & Branch Synchronization Guide

## 1. Branch Topology

Only 2 active branches are maintained in this repository:
1. `main`: Antigravity's workspace, containing architecture specs, test harness, and verified commits.
2. `vuongdat67-pure-domain-entities` (or `copilot`): Copilot's worktree branch where Copilot generates code.

```
       (Antigravity: specs, tests, verification)
main:   ●─────●─────●─────●─────● [HEAD: ec21df9]
               \                 \ (Merge/Sync)
copilot:        ●─────●───────────● [HEAD: in worktree]
            (Copilot: code edits & commits)
```

---

## 2. Fast Synchronization Commands

### Option A: Antigravity automatically syncs main into Copilot (Done for you!)
Whenever Antigravity adds new task specs or tests to `main`, Antigravity runs:
```powershell
git -C "C:/Users/vuong/scoop/buckets/copilot-worktrees/agent-pentest/vuongdat67-verbose-sniffle" merge main
```
This instantly brings all new test files and task cards into Copilot's editor without any manual action needed by the user.

### Option B: Copilot commits directly
Copilot can commit its own completed batch of tasks directly:
```bash
git add src/
git commit -m "feat(infra): implement EPIC-01 ingestion and storage infrastructure"
```

### Option C: Rebase or Fast-Forward merge
When Copilot finishes:
```powershell
# From the main workspace (Downloads/agent-pentest):
git merge vuongdat67-pure-domain-entities
```
This keeps git history completely linear and clean.
