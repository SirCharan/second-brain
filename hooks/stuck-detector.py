#!/usr/bin/env python3
"""PostToolUse(Bash) hook: if the SAME command fails ≥2× in a row, nudge to query memory.
Failure = clear markers in the tool output (not bare 'error', not grep/test exit-1). Never blocks."""

import os
import sys, os, re, json

# Windows defaults to cp1252 for console output AND for open(), so both printing a status
# glyph and reading a note containing an emoji raise. Interpreter UTF-8 mode fixes both, and
# can only be set at startup, so re-exec into it once when we were not started that way.
if (
    __name__ == "__main__"  # never re-exec when imported as a library
    and os.name == "nt"
    and not sys.flags.utf8_mode
    and not os.environ.get("SB_UTF8_REEXEC")
    and getattr(sys, "frozen", None) is None
):
    os.environ["SB_UTF8_REEXEC"] = "1"
    try:
        os.execv(
            sys.executable,
            [sys.executable, "-X", "utf8", os.path.abspath(__file__), *sys.argv[1:]],
        )
    except Exception:
        pass  # fall through to the stream guard below rather than refusing to run
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

try:
    import _hooklib as HL
except Exception:
    HL = None

STATE_DIR = (
    os.path.join(HL.STATE_DIR, ".stuck-state")
    if HL
    else os.path.expanduser("~/.second-brain/.stuck-state")
)
THRESHOLD = 2
FAIL = re.compile(
    r"command not found|No such file or directory|Traceback \(most recent call last\)|"
    r"^fatal:|Permission denied|npm ERR!|returned non-zero|exit code [1-9]|exit status [1-9]|"
    r"ModuleNotFoundError|SyntaxError:|ImportError|not recognized as|cannot access|Cannot find module",
    re.M,
)


def main():
    try:
        hook = json.loads(sys.stdin.read())
    except Exception:
        return
    if hook.get("tool_name") not in (None, "Bash"):
        return
    cmd = ((hook.get("tool_input") or {}).get("command") or "").strip()
    if not cmd:
        return
    resp = hook.get("tool_response")
    resp = (
        resp if isinstance(resp, str) else json.dumps(resp) if resp is not None else ""
    )
    sid = hook.get("session_id") or "nosession"
    sig = re.sub(r"\s+", " ", cmd)[:60]
    os.makedirs(STATE_DIR, exist_ok=True)
    sf = os.path.join(STATE_DIR, re.sub(r"[^A-Za-z0-9_-]", "_", sid) + ".json")
    try:
        st = json.load(open(sf))
    except Exception:
        st = {}

    failed = bool(FAIL.search(resp))
    if not failed:
        if st.pop(sig, None) is not None:
            _save(sf, st)
        return
    st[sig] = st.get(sig, 0) + 1
    n = st[sig]
    _save(sf, st)
    if n == THRESHOLD or (n > THRESHOLD and n % 2 == 0):  # nudge at 2, then 4, 6…
        kws = [t for t in re.split(r"\s+", cmd) if t and not t.startswith("-")][:3]
        kws = " ".join(re.sub(r"[^\w./-]", "", k) for k in kws) or cmd[:30]
        print(
            f"⚠ stuck-check: `{sig}` has failed {n}× in a row. "
            f"Before retrying, pull prior context from memory: `/second-brain pull {kws}` "
            f"(check for a known gotcha / past fix)."
        )


def _save(sf, st):
    try:
        if HL:
            HL.write_json(sf, st)
        else:
            json.dump(st, open(sf, "w"))
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if HL:
            HL.log_err("stuck-detector", e)
