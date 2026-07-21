#!/usr/bin/env python3
"""UserPromptSubmit hook: just-in-time memory recall.
Word-boundary keyword match against the vault; requires >=2 distinct query keywords in a
note's name/description (kills generic-prompt noise). Deduped within session, capped,
project-biased. Silent on trivial/no-match prompts. Never blocks; logs failures."""

import sys, os, re, glob, json, time

import _hooklib as HL

MEM = HL.MEM
STATE_DIR = os.path.join(MEM, ".recall-state")
EXCLUDE = {"MEMORY.md", "context.md", "_session-log.md"}
STOP = set(
    "the a an and or of to in on for with is are was were be been this that these those i you "
    "it we they he she how what why when where which who do does did can could should would will "
    "just now then here there my your our their its from into out up down over about as at by so "
    "if not no yes ok okay thanks please help make add use using get got need want like also more "
    "most some any all one two new old via per etc pls better stronger strong full work works".split()
)
TRIVIAL = re.compile(
    r"^\s*(hi|hey|hello|yo|thanks|thank you|ok|okay|k|yep|yes|no|nope|cool|nice|"
    r"got it|sure|great|perfect|done|continue|go on|next|/\w+)\s*[.!]*\s*$",
    re.I,
)


project_for = HL.project_for


def words(s):
    return set(re.findall(r"[a-z0-9]{3,}", s.lower()))


def _age_days(head):
    """Age in days from `last_confirmed` (preferred) or `asserted` frontmatter; None if absent."""
    for key in ("last_confirmed", "asserted"):
        # tolerate both flat v2 (`asserted:`) and nested (`  asserted:` under `metadata:`)
        m = re.search(r"^\s*" + key + r":\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", head, re.M)
        if m:
            try:
                t = time.mktime(time.strptime(m.group(1), "%Y-%m-%d"))
                return (time.time() - t) / 86400.0
            except Exception:
                return None
    return None


def _is_note(p):
    """A real curated note — excludes index/meta files and the Daily/Weekly journals."""
    b = os.path.basename(p)
    if b in EXCLUDE or b.startswith("_"):
        return False
    if os.path.basename(os.path.dirname(p)) in (
        "Daily",
        "Weekly",
        "_system",
        "Sessions",
    ):
        return False
    return True


def _latest_addition():
    """Most recent memory addition = last capture line in the newest Daily note (prefix-stripped),
    else the most-recently-modified note name."""
    dfiles = sorted(glob.glob(os.path.join(MEM, "Daily", "20*.md")))
    for df in reversed(dfiles):
        lines = [l.rstrip() for l in open(df, errors="ignore") if l.startswith("- ")]
        if lines:
            return re.sub(
                r"^- \*\*\d{1,2}:\d{2}\*\*(\s*\[[^\]]*\])?\s*—\s*", "", lines[-1]
            )[:100]
    notes = [p for p in glob.glob(os.path.join(MEM, "*", "*.md")) if _is_note(p)]
    if notes:
        return os.path.splitext(os.path.basename(max(notes, key=os.path.getmtime)))[0]
    return ""


def _emit_stats(proj):
    """Print the always-on memory stats line: total notes, count on current topic, latest addition."""
    try:
        notes = [p for p in glob.glob(os.path.join(MEM, "*", "*.md")) if _is_note(p)]
        total = len(notes)
        yclause = ""
        if proj:
            yc = sum(1 for p in notes if os.path.basename(os.path.dirname(p)) == proj)
            yclause = f" · {yc} on {proj}" if yc > 0 else f" · {proj} (new)"
        latest = _latest_addition()
        line = f"\U0001f4ca Obsidian memory: {total} notes{yclause}"
        if latest:
            line += f" · latest: {latest}"
        sys.stdout.write(line + "\n")
    except Exception as e:
        HL.log_err("memory-recall.stats", e)


VENV_PY = os.path.expanduser("~/.claude/hooks/.venv-embed/bin/python")
EMBED = os.path.expanduser("~/.claude/hooks/memory-embed.py")
RETIRED = ("retired", "deprecated", "archived", "superseded")


def _semantic_fill(prompt, exclude, need):
    """Guarded semantic fallback: shell into the embed venv, return [(name, folder, desc)].
    Only fills `need` slots keyword recall left empty. No-op if venv/index/deps missing."""
    if need <= 0 or not os.path.exists(VENV_PY) or not os.path.exists(EMBED):
        return []
    try:
        import subprocess

        r = subprocess.run(
            [VENV_PY, EMBED, "query", prompt, "12"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return []
    picks = []
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        score, name, folder = parts
        try:
            if float(score) < 0.5:  # relevance floor for bge-small cosine
                continue
        except ValueError:
            continue
        if name in exclude:
            continue
        d = ""
        try:
            head = open(os.path.join(MEM, folder, name + ".md"), errors="ignore").read(
                2048
            )
            sm = re.search(r"^\s*status:\s*(.+)$", head, re.M)
            if sm and sm.group(1).strip().strip("\"'").lower() in RETIRED:
                continue  # honor the retired filter
            m = re.search(r"^description:\s*(.+)$", head, re.M)
            d = (m.group(1).strip().strip("\"'"))[:110] if m else ""
        except Exception:
            pass
        picks.append((name, folder, d))
        if len(picks) >= need:
            break
    return picks


def main():
    if not HL.vault_ok():
        return
    try:
        hook = json.loads(sys.stdin.read())
    except Exception:
        return
    prompt = (hook.get("prompt") or "").strip()
    sid = hook.get("session_id") or "nosession"
    proj = project_for(hook.get("cwd", ""))
    _emit_stats(proj)  # always-on memory stats line (before the gate)
    if not prompt or TRIVIAL.match(prompt):
        return
    kw = {w for w in words(prompt) if w not in STOP}
    if len(kw) < 3:
        return

    rows = []
    for p in glob.glob(os.path.join(MEM, "*", "*.md")):
        b = os.path.basename(p)
        if b in EXCLUDE or b.startswith("_"):
            continue
        folder = os.path.basename(os.path.dirname(p))
        if folder in ("Daily", "Weekly", "_system", "Sessions"):
            continue
        name = os.path.splitext(b)[0]
        try:
            head = open(p, errors="ignore").read(
                6144
            )  # cap read — hot path; covers most bodies
        except Exception:
            continue
        m = re.search(r"^description:\s*(.+)$", head, re.M)
        desc = (m.group(1).strip().strip("\"'")) if m else ""
        nwords, dwords = words(name), words(desc)
        # DISTINCT query keywords matched as whole words in the high-signal head
        hit_name = kw & nwords
        hit_desc = kw & dwords
        head_hits = hit_name | hit_desc
        if len(head_hits) < 2:  # gate: kills generic single-word noise (name/desc only)
            continue
        # low-weight body signal: keywords found in the body but not already in name/desc
        body_extra = (kw & words(head)) - hit_name - hit_desc
        sm = re.search(r"^\s*status:\s*(.+)$", head, re.M)
        status = (sm.group(1).strip().strip("\"'").lower()) if sm else ""
        if status in ("retired", "deprecated", "archived", "superseded"):
            continue  # never auto-inject facts that were explicitly retired
        score = 5 * len(hit_name) + 3 * len(hit_desc) + 1 * len(body_extra)
        if proj and folder == proj:
            score = int(score * 1.5)
        # decay/freshness: boost recently-confirmed notes, penalize stale ones
        age = _age_days(head)
        if age is not None:
            if age <= 30:
                score = int(score * 1.25)
            elif age > 365:
                score = int(score * 0.6)
            elif age > 180:
                score = int(score * 0.8)
        rows.append((score, name, folder, desc[:110]))
    rows.sort(reverse=True)

    os.makedirs(STATE_DIR, exist_ok=True)
    sf = os.path.join(STATE_DIR, re.sub(r"[^A-Za-z0-9_-]", "_", sid) + ".json")
    seen = set(HL.read_json(sf, {}).get("injected", []))
    fresh = [r for r in rows if r[1] not in seen][:4]

    # semantic fallback: fill remaining slots when keyword recall is thin (incl. zero hits)
    need = 4 - len(fresh)
    if need > 0:
        exclude = seen | {r[1] for r in fresh}
        fresh += [(0, n, f, d) for (n, f, d) in _semantic_fill(prompt, exclude, need)]
    if not fresh:
        return

    out = ["=== Relevant memory (auto-recalled for this prompt) ==="]
    total = len(out[0])
    picked = []
    for s, name, folder, desc in fresh:
        line = f"- [[{name}]] ({folder})" + (f" — {desc}" if desc else "")
        if total + len(line) > 1400:
            break
        out.append(line)
        total += len(line)
        picked.append(name)
    if not picked:
        return
    out.append(
        "(Open a note or `/second-brain find <term>` for more. Recalled once per session.)"
    )
    sys.stdout.write("\n".join(out) + "\n")

    try:
        HL.write_json(
            sf, {"injected": sorted(seen | set(picked)), "ts": int(time.time())}
        )
        cutoff = time.time() - 7 * 86400
        for f in glob.glob(os.path.join(STATE_DIR, "*.json")):
            if os.path.getmtime(f) < cutoff:
                os.remove(f)
    except Exception as e:
        HL.log_err("memory-recall.state", e)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        HL.log_err("memory-recall", e)
