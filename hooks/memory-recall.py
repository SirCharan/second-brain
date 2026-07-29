#!/usr/bin/env python3
"""UserPromptSubmit hook: just-in-time memory recall.
Word-boundary keyword match against the vault; requires >=2 distinct query keywords in a
note's name/description (kills generic-prompt noise). Deduped within session, capped,
project-biased. Silent on trivial/no-match prompts. Never blocks; logs failures."""

import sys, os, re, glob, json, time

import _hooklib as HL
import sb_rank

MEM = HL.MEM
STATE_DIR = os.path.join(MEM, ".recall-state")
TRIVIAL = re.compile(
    r"^\s*(hi|hey|hello|yo|thanks|thank you|ok|okay|k|yep|yes|no|nope|cool|nice|"
    r"got it|sure|great|perfect|done|continue|go on|next|/\w+)\s*[.!]*\s*$",
    re.I,
)


project_for = HL.project_for

# The note walk, the scoring and the index all live in sb_rank, so the MCP tool layer
# and the eval harness rank identically to this hook.
words = sb_rank.words
_all_notes = sb_rank.all_notes
_folder = sb_rank.folder_of
STOP = sb_rank.STOP


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
    notes = _all_notes()
    if notes:
        return os.path.splitext(os.path.basename(max(notes, key=os.path.getmtime)))[0]
    return ""


def _emit_note_debt():
    """Surface unpaid curated-note debt, escalating with age and count. Written by the
    capture-exchange Stop hook; clears itself when a note lands in the folder."""
    try:
        path = os.path.join(MEM, "_infra", "_note-debt.md")
        if not os.path.exists(path):
            return
        rows = [
            l.strip() for l in open(path, errors="ignore") if l.startswith("- [ ] ")
        ]
        if not rows:
            return
        projs, oldest = [], None
        for r in rows:
            # search PAST the "- [ ] " checkbox, or the regex matches "[ ]" not "[proj]"
            m = re.search(r"\[([^\]\s]+)\]", r[6:])
            if m and m.group(1) not in projs:
                projs.append(m.group(1))
            d = re.match(r"- \[ \] (\d{4}-\d{2}-\d{2})", r)
            if d and (oldest is None or d.group(1) < oldest):
                oldest = d.group(1)
        age = 0
        if oldest:
            try:
                age = int(
                    (time.time() - time.mktime(time.strptime(oldest, "%Y-%m-%d")))
                    / 86400
                )
            except Exception:
                age = 0
        lead = "⚠️ NOTE DEBT" if len(rows) < 3 and age < 2 else "\U0001f6a8 NOTE DEBT"
        msg = (
            f"{lead}: {len(rows)} session(s) changed code but left no curated note"
            + (f" (oldest {age}d)" if age else "")
            + f" — {', '.join(projs[:4])}. Write the note now in that project folder "
            "(v2 frontmatter + H1 + status chip + callouts + `## Related` linking "
            "its `_MOC-` hub), then it clears itself. See `_infra/_note-debt.md`."
        )
        sys.stdout.write(msg + "\n")
    except Exception as e:
        HL.log_err("memory-recall.note-debt", e)


def _emit_stats(proj):
    """Print the always-on memory stats line: total notes, count on current topic, latest addition."""
    try:
        notes = _all_notes()
        total = len(notes)
        yclause = ""
        if proj:
            yc = sum(1 for p in notes if _folder(p) == proj)
            yclause = f" · {yc} on {proj}" if yc > 0 else f" · {proj} (new)"
        latest = _latest_addition()
        line = f"\U0001f4ca Obsidian memory: {total} notes{yclause}"
        if latest:
            line += f" · latest: {latest}"
        sys.stdout.write(line + "\n")
    except Exception as e:
        HL.log_err("memory-recall.stats", e)


VENV_PY = HL.EMBED_VENV_PY  # optional semantic-embed venv (built by `sb-embed setup`)
EMBED = HL.EMBED_SCRIPT
RETIRED = sb_rank.RETIRED


def _semantic_fill(prompt, exclude, need):
    """Guarded semantic fallback: shell into the embed venv, return [(name, folder, desc)].
    Only fills `need` slots keyword recall left empty. No-op if venv/index/deps missing."""
    if need <= 0 or not HL.embed_ready():
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
    _emit_note_debt()  # unpaid curated-note debt, if any
    if not prompt or TRIVIAL.match(prompt):
        return
    kw = {w for w in words(prompt) if w not in STOP}
    if len(kw) < 3:
        return

    # Rank everything, then drop what this session already saw — filtering before the
    # cut would return fewer than 4 notes on a repeat topic.
    rows = [
        (r["score"], r["name"], r["folder"], r["description"][:110], r["path"])
        for r in sb_rank.rank(prompt, project=proj, limit=0)
    ]

    os.makedirs(STATE_DIR, exist_ok=True)
    sf = os.path.join(STATE_DIR, re.sub(r"[^A-Za-z0-9_-]", "_", sid) + ".json")
    seen = set(HL.read_json(sf, {}).get("injected", []))
    fresh = [r for r in rows if r[1] not in seen][:4]

    # semantic fallback: fill remaining slots when keyword recall is thin (incl. zero hits)
    need = 4 - len(fresh)
    if need > 0:
        exclude = seen | {r[1] for r in fresh}
        fresh += [
            (0, n, f, d, os.path.join(MEM, f, n + ".md"))
            for (n, f, d) in _semantic_fill(prompt, exclude, need)
        ]
    if not fresh:
        return

    # Head-first injection: the TOP hit gets its full body (only when it respects the 8KB
    # split gate — atomic notes are built to be injectable whole); every other hit gets
    # its head (name + description + up to 3 key callout lines). Budget ~2k tokens.
    BUDGET = 8000
    SPLIT_GATE = 8192
    out = ["=== Relevant memory (auto-recalled for this prompt) ==="]
    total = len(out[0])
    picked = []
    for i, (s, name, folder, desc, p) in enumerate(fresh):
        block = f"- [[{name}]] ({folder or 'root'})" + (f" — {desc}" if desc else "")
        extra = []
        try:
            if i == 0 and os.path.getsize(p) <= SPLIT_GATE:
                body = open(p, errors="ignore").read()
                body = re.sub(r"^---\n.*?\n---\n", "", body, count=1, flags=re.S)
                extra = ["", body.strip(), ""]
            else:
                head = open(p, errors="ignore").read(2048)
                extra = [
                    "  " + l.strip()[:160]
                    for l in head.splitlines()
                    if l.strip().startswith("> [!")
                ][:3]
        except Exception:
            pass
        chunk = "\n".join([block] + extra) if extra else block
        if total + len(chunk) > BUDGET:
            chunk = block  # over budget: fall back to the one-line head
            if total + len(chunk) > BUDGET:
                break
        out.append(chunk)
        total += len(chunk)
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
