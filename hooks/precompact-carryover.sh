#!/usr/bin/env bash
# PreCompact carry-over: nudge compaction to preserve the high-signal state instead of summarizing it away.
# Adapted from ECC (affaan-m/ECC, MIT) memory-persistence + Anthropic's "customize compaction" guidance.
printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreCompact","additionalContext":"Compaction carry-over — preserve VERBATIM: the active task/plan, files modified this session, unresolved bugs/errors, key decisions and their rationale, and exact test/build/deploy commands. Drop resolved tool output and stale exploration before any of these."}}'
exit 0
