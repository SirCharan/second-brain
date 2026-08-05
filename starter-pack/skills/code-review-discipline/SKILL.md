---
name: code-review-discipline
description: >
  High-signal code-review discipline — apply when reviewing a diff/PR or running the built-in /code-review,
  /review, or the code-reviewer agent, and whenever you ask for a review or "check this code". Enforces a
  confidence gate (only report findings you're >80% sure are real bugs) and a false-positive skip list
  (don't flag handled-upstream cases, fixed-cardinality "N+1", pure style nits, or speculative "consider
  adding…"). Goal: zero-noise reviews where every reported item is a real, evidence-backed defect. Adapted
  (not copied) from the ECC code-reviewer protocol. Trigger on: "review this", "code review", "check this
  PR/diff", "find bugs", "is this correct", or before posting review comments.
---

# Code-Review Discipline

Companion to the built-in `/code-review` and `code-reviewer` agent — this governs *what counts as a
finding*. The failure mode of LLM review is **noise**: plausible-but-wrong or low-value comments that
erode trust. Fix it with a gate + a skip list.

## The confidence gate
- **Only report a finding you are >80% confident is a real defect** (a bug, security issue, data loss,
  correctness/logic error, race, resource leak, or a broken contract). State the confidence implicitly by
  only surfacing things you can defend.
- For each reported finding, include **evidence**: the file:line, *why* it breaks (the concrete input/path
  that triggers it), and the fix. No evidence → don't report it.
- If you're <80% but it's high-impact (security/data-loss), report it **explicitly flagged as "unverified
  — needs checking"**, not as a confirmed bug.
- Separate **must-fix** (correctness/security) from **optional** (clarity/perf) and lead with must-fix.
  If there are zero must-fix findings, say so plainly — "no correctness/security issues found" is a valid,
  valuable result. Don't manufacture findings to look thorough.

## False-positive skip list (do NOT flag these)
- **Handled upstream / elsewhere:** "add error handling / null check / validation" when the case is
  already guarded by a caller, middleware, type system, or earlier guard. Trace the call path first.
- **Fixed-cardinality "N+1":** loop-over-query patterns where N is bounded and tiny (e.g. iterating a
  3-asset list). Only flag N+1 when N scales with user/data input.
- **Pure style / taste:** formatting, naming preference, "could be more idiomatic", import ordering —
  the formatter/linter owns these (you auto-format on save). Not review findings.
- **Speculative "consider adding…":** tests/docs/abstraction/logging that aren't required for correctness
  and weren't asked for. Mention at most once, as a single optional note — never as a list.
- **Defended trade-offs:** a deliberate choice the code or a comment already justifies (e.g. a documented
  in-memory cache, an intentional `any` with a reason). Don't re-litigate.
- **Hypotheticals with no trigger:** "this *could* break if X" where X can't actually occur given the
  types/inputs. If you can't name a real triggering input, skip it.
- **Framework/library misreads:** behavior that's actually correct per the framework's contract — verify
  the API before claiming misuse.

## Output shape
For each must-fix: `path:line — <one-line defect> — <triggering input/path> — <fix>`. Then optional notes
(≤3, terse). Then a one-line verdict (ship / fix-then-ship / needs-rework). Match a terse style; no
filler, no praise padding.

## When NOT to use
Trivial diffs (typo, one-line rename), or when you explicitly want a broad/exploratory review rather than
a defect hunt — then widen the lens but keep the evidence requirement.

## Source
Adapted from the ECC (`affaan-m/ECC`, MIT) `agents/code-reviewer.md` confidence-gate + false-positive
skip-list pattern; converges with SuperClaude's evidence-based SelfCheck. Re-implemented for this setup.
