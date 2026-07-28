#!/usr/bin/env python3
"""UserPromptSubmit hook: interview-first nudge, but ONLY on a detected larger task.

Replaces the old always-on static reminder (which fired on every prompt = noise). This scores the
prompt for larger-task signals (build/create verbs, scale nouns, multi-step, length, vague ambition)
and injects a strong, specific "interview me first" nudge only when the score clears a threshold.
Stays silent on questions, trivial asks, slash commands, and short replies. stdout = additionalContext.
Never blocks; fails silent.
"""

import sys, json, re

BUILD_VERBS = re.compile(
    r"\b(build|create|implement|add|design|refactor|migrate|set ?up|ship|redesign|rewrite|"
    r"integrate|overhaul|scaffold|develop|architect|automate|revamp|rebuild|port|generate)\b",
    re.I,
)
SCALE_NOUNS = re.compile(
    r"\b(app|site|website|dashboard|feature|system|pipeline|service|platform|bot|report|landing|"
    r"page|api|workflow|integration|executor|microsite|deck|tool|calculator|skill|plugin|hook|"
    r"agent|schema|database|migration|redesign)\b",
    re.I,
)
VAGUE = re.compile(
    r"\b(better|improve|optimi[sz]e|clean up|revamp|overhaul|nicer|polish|moderni[sz]e)\b",
    re.I,
)
# quiet on: slash cmds, pure short questions, confirmations/replies
SKIP = re.compile(
    r"^\s*(/|\?|yes\b|no\b|yep|yeah|ok\b|okay|go ahead|do it|proceed|continue|sounds good|"
    r"option \d|the first|the second|thanks|thank you|cool|nice|perfect|got it|sure)\b",
    re.I,
)
QUESTION = re.compile(
    r"^\s*(what|how|why|when|who|where|which|is|are|does|do|can|should|could|will|did)\b",
    re.I,
)


def score(p):
    s = 0
    verbs = len(set(m.lower() for m in BUILD_VERBS.findall(p)))
    s += min(verbs, 2) * 2  # build/create verbs (strong signal)
    s += min(len(set(m.lower() for m in SCALE_NOUNS.findall(p))), 2)  # scale nouns
    words = len(p.split())
    if words > 40:
        s += 1
    if words > 100:
        s += 2
    if (
        re.search(r"(^|\n)\s*\d+[.)]\s", p)
        or p.count(" and ") >= 2
        or p.count(".") >= 3
    ):
        s += 1  # multi-step
    if VAGUE.search(p):
        s += 1
    return s


def main():
    try:
        hook = json.loads(sys.stdin.read())
    except Exception:
        return
    p = (hook.get("prompt") or "").strip()
    if not p or SKIP.match(p):
        return
    words = len(p.split())
    # a short pure question is a lookup, not a build task
    if QUESTION.match(p) and words < 25 and "?" in p:
        return
    s = score(p)
    if s < 4:
        return
    out = [
        "=== Larger task detected — INTERVIEW, THEN PLAN ===",
        "Do these in order before writing code:",
        "1. **Interview first** with AskUserQuestion (2–4 questions, multiSelect where apt) "
        "across: scope (in/out) · target env · output shape · tradeoffs (speed vs "
        "thoroughness / cost) · done-criteria. Recommend a default in every option so it "
        "is a confirmation, not a blank. Do not start building on assumptions.",
        "2. **Enter plan mode** to agree the shape before editing — explore read-only, then "
        "present the plan for approval.",
    ]
    if s >= 7:
        out.append(
            "3. **This looks large: offer multi-agent orchestration** (the Workflow tool, "
            "'ultracode') and let the user opt in. Fan out research and review across "
            "agents; keep the main thread for synthesis."
        )
    else:
        out.append(
            "3. Then track the plan as tasks and execute step-by-step, marking each one "
            "complete inline. For a big build, offer multi-agent orchestration."
        )
    out.append(
        "Skip ONLY if the user already answered these this turn, it is a continuation, or "
        "it is genuinely trivial."
    )
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
