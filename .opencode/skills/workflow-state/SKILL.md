---
name: workflow-state
description: Track multi-agent workflow state in WORKFLOW_STATE.md
---

## WORKFLOW_STATE.md format
```markdown
# Workflow State

## Task: [description]

### Planning (@planner)
**Date:** [timestamp]
**Plan:** ...

### Implementation (@implementor)
**Date:** [timestamp]
**Changes made:** ...
**Test results:** ...

### Review (@reviewer)
**Date:** [timestamp]
**Verdict:** ...
```
Update this file after each agent completes its step.
