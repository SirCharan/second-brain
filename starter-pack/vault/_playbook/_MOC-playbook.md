---
name: _MOC-playbook
title: "Playbook — map of content"
description: "Hub for the working rules the starter-pack skills expect: the memory loop, phase discipline, and which skill routes what."
tags: [meta, project/playbook, type/moc]
asserted: 2026-07-29
last_confirmed: 2026-07-29
source: user
confidence: high
status: active
supersedes: []
metadata:
  type: moc
---

# 📔 Playbook — map of content

🟢 **active**

The working rules the starter-pack skills assume. Three notes, each pointing at the skill that owns
it. Edit them — they are your rules now, not a fixed spec.

> [!info] Where these came from
> The starter pack installed them. Delete any note you disagree with; nothing reads this folder
> automatically, so the only cost of keeping it is a few nodes in your graph.

```mermaid
graph TD
  hub["📔 playbook"] --> habits["session-habits"]
  hub --> phase["phase-discipline"]
  hub --> route["routing-rules"]
  habits --> route
  phase --> route
```

## Notes
- [[session-habits]] — search before guessing, consolidate on a rhythm, publish before done
- [[phase-discipline]] — one phase at a time, tests every phase, reflect before replanning
- [[routing-rules]] — which skill to load first for prose and for UI

## Related
- [[_Home]]
- [[how-memory-works]]
