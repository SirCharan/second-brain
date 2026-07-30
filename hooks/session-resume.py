#!/usr/bin/env python3
"""SessionStart(startup|clear) hook: inject LIVING Obsidian state so a new chat resumes.
Emits (project-aware, via cwd): recent Daily captures + recently-modified notes +
last-session rollup + the _Home map. Read-only; never raises; prints nothing on other sources."""

import os
import sys, os, json, re, glob

import _hooklib as HL

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
    # os.execv does not replace the process on Windows: the parent exits immediately with
    # its own status while the child keeps running, so the caller reads the wrong exit
    # code. Re-run synchronously and pass the child's code up. stdin/stdout are inherited,
    # so a hook still receives its JSON payload.
    import subprocess

    os.environ["SB_UTF8_REEXEC"] = "1"
    try:
        sys.exit(
            subprocess.run(
                [sys.executable, "-X", "utf8", os.path.abspath(__file__), *sys.argv[1:]]
            ).returncode
        )
    except OSError:
        pass  # fall through to the stream guard rather than refusing to run
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

MEM = HL.MEM
DAILY = os.path.join(MEM, "Daily")
EXCLUDE = {"MEMORY.md", "context.md", "_session-log.md", "_Home.md"}

# Character budgets. Sharding MEMORY.md stopped the index itself from overflowing, but
# the overflow moved here: this hook pasted a whole project shard and the whole _Home
# map in verbatim. Measured on a 489-note vault, the largest project injected 25,692
# chars (~6,400 tokens) at every session start, 72% of it one uncapped shard, growing
# with every note added to that project. Anything omitted is still one prompt away via
# recall, so a cap costs reachability nothing.
SHARD_MAX = 6000  # project note index (the section that actually overflowed)
HOME_MAX = 2000  # _Home.md map
TOTAL_MAX = 14000  # backstop across every section (~3,500 tokens)


def _cap(text, limit, what):
    """Trim text to `limit` chars on a line boundary, appending a pointer when cut."""
    if len(text) <= limit:
        return text
    keep = text[:limit].rsplit("\n", 1)[0]
    dropped = text[len(keep) :].count("\n")
    return keep + "\n  … %d more %s omitted — recall surfaces them on demand." % (
        dropped,
        what,
    )


def _cap_index(lines, limit):
    """Fit a project's note index into `limit` chars, preferring COVERAGE over detail:
    descriptions if they fit, otherwise bare links for every note. Truncating the list
    instead would hide notes alphabetically, and a note the model never learns exists is
    one it never asks for — whereas a missing description is one recall away."""
    full = "\n".join(lines)
    if len(full) <= limit:
        return full
    bare = []
    for l in lines:
        m = re.match(r"- \[\[([^\]]+)\]\]", l)
        if m:
            bare.append("- [[%s]]" % m.group(1))
    joined = "\n".join(bare)
    if len(joined) <= limit:
        return (
            joined
            + "\n  (descriptions trimmed to fit — all %d notes listed.)" % len(bare)
        )
    return _cap(joined, limit, "notes in this project")


project_for = HL.project_for  # cwd -> memory folder (shared, git-root fallback)


def _is_junk(ln):
    """Skip raw/undistilled capture lines (auto-appended image/prompt fallbacks)."""
    return "(raw)" in ln or "[Image:" in ln


def desc(path):
    try:
        t = open(path, errors="ignore").read()[:600]
    except Exception:
        return ""
    m = re.search(r"^\s*description:\s*(.+)$", t, re.M)
    return (m.group(1).strip().strip('"').strip("'")[:120]) if m else ""


def _stale_count(days=120):
    """Cheap ambient count of active notes not confirmed in N+ days (frontmatter
    head-read only). Mirrors skills/second-brain/scripts/stale.py. Never raises."""
    from datetime import date

    today = date.today()
    skip = {"Daily", "Weekly", "Sessions", "_system"}
    n, seen = 0, 0
    for p in glob.glob(os.path.join(MEM, "*", "*.md")):
        if seen >= 3000:
            break
        b = os.path.basename(p)
        if b.startswith("_") or os.path.basename(os.path.dirname(p)) in skip:
            continue
        seen += 1
        try:
            head = open(p, errors="ignore").read(1200)
        except Exception:
            continue
        m = re.match(r"^---\n(.*?)\n---", head, re.S)
        if not m:
            continue
        fm = m.group(1)
        st = re.search(r"^status:\s*(.+)$", fm, re.M)
        if st and st.group(1).strip().strip('"').strip("'").lower() in (
            "retired",
            "superseded",
            "deprecated",
            "archived",
        ):
            continue
        dm = re.search(
            r"^last_confirmed:\s*\D*(\d{4})-(\d{2})-(\d{2})", fm, re.M
        ) or re.search(r"^asserted:\s*\D*(\d{4})-(\d{2})-(\d{2})", fm, re.M)
        if not dm:
            continue
        try:
            age = (
                today - date(int(dm.group(1)), int(dm.group(2)), int(dm.group(3)))
            ).days
        except Exception:
            continue
        if age > days:
            n += 1
    return n


# Curation backlog thresholds. Nothing runs consolidation unattended, so the only thing
# standing between a captured finding and a retrievable note is this signal. Recall ranks
# curated notes and ignores Daily/ and Sessions/ entirely, so an un-consolidated vault
# keeps capturing and stops retrieving — while still reporting a healthy note count.
BACKLOG_MIN = 5  # unchecked promote-queue entries before we say anything
BACKLOG_AGE = 7  # or this many days since the oldest unchecked entry
BACKLOG_LOUD = 15  # past here it stops being a footnote


def _consolidation_backlog():
    """(count, oldest_age_days) of unchecked promote-queue entries. (0, 0) when the file
    is absent or clean. Never raises."""
    try:
        q = os.path.join(MEM, "_infra", "_promote-queue.md")
        if not os.path.exists(q):
            return 0, 0
        rows = [l for l in open(q, errors="ignore") if l.startswith("- [ ] ")]
        if not rows:
            return 0, 0
        from datetime import date

        oldest = None
        for r in rows:
            m = re.match(r"- \[ \] (\d{4})-(\d{2})-(\d{2})", r)
            if not m:
                continue
            try:
                d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                continue
            if oldest is None or d < oldest:
                oldest = d
        age = (date.today() - oldest).days if oldest else 0
        return len(rows), age
    except Exception as e:
        HL.log_err("session-resume.backlog", e)
        return 0, 0


def _backlog_notice():
    """One line when the curation backlog crosses a threshold, else None."""
    count, age = _consolidation_backlog()
    if count < BACKLOG_MIN and age < BACKLOG_AGE:
        return None
    loud = count >= BACKLOG_LOUD or age >= BACKLOG_AGE * 4
    return (
        "\n%s CURATION BACKLOG: %d finding%s still uncurated%s. Run `/second-brain consolidate` — until then recall cannot return any of them, because it ranks curated notes and ignores the journal."
        % (
            "🚨" if loud else "📥",
            count,
            "" if count == 1 else "s",
            ", oldest %dd old" % age if age else "",
        )
    )


def main():
    raw = sys.stdin.read()
    try:
        hook = json.loads(raw)
    except Exception:
        hook = {}
    if hook.get("source") not in ("startup", "clear"):
        return
    if not HL.vault_ok():
        return
    proj = project_for(hook.get("cwd", ""))
    out = []
    out.append("=== Obsidian resume: living state (read from the vault) ===")
    out.append(
        f"Project context: {proj if proj else 'global (cwd not a known repo)'}. "
        "This is recent activity to resume from; the vault is the source of truth. "
        "Write back via the CAPTURE footer (see CLAUDE.md)."
    )

    # Curation backlog — emitted HERE, before the long sections, because the tail is what
    # the TOTAL_MAX backstop trims and this is the one signal that must survive.
    notice = _backlog_notice()
    if notice:
        out.append(notice)

    # --- Distilled last-session digest (written by capture-exchange Stop hook) ---
    ls = os.path.join(MEM, "_infra", "_last-session.md")
    if os.path.exists(ls):
        try:
            body = open(ls, errors="ignore").read()
            body = re.sub(r"^---.*?---\s*", "", body, count=1, flags=re.S).strip()
            if body:
                out.append("\n" + body)
        except Exception as e:
            HL.log_err("session-resume.last-session", e)

    # --- Recent Daily captures (last ~2 dated files) ---
    dfiles = sorted(glob.glob(os.path.join(DAILY, "20*.md")))[-2:]
    proj_lines, glob_lines = [], []
    for df in dfiles:
        day = os.path.splitext(os.path.basename(df))[0]
        for ln in open(df, errors="ignore"):
            ln = ln.rstrip()
            if not ln.startswith("- ") or _is_junk(ln):
                continue
            # capture lines look like: - **HH:MM** [<cwd-basename>@branch] — ...
            mtag = re.search(r"\[([^@\]]+)", ln)
            line_proj = project_for(mtag.group(1)) if mtag else None
            tagged = proj and line_proj == proj
            (proj_lines if tagged else glob_lines).append(f"{day} {ln}")
    if proj_lines or glob_lines:
        out.append("\n## Recent captures")
        if proj and proj_lines:
            out.append(f"### {proj} (this project)")
            out += proj_lines[-20:]
        out.append("### recent (all projects)")
        out += glob_lines[-20:]

    # --- Recently-modified notes (~10 by mtime) ---
    notes = []
    for p in glob.glob(os.path.join(MEM, "*", "*.md")):
        b = os.path.basename(p)
        if b in EXCLUDE or b.startswith("_MOC-"):
            continue
        if os.path.basename(os.path.dirname(p)) in (
            "Daily",
            "Weekly",
            "_system",
            "Sessions",
        ):
            continue
        notes.append(p)
    notes.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    if proj:
        notes.sort(
            key=lambda p: 0 if os.path.basename(os.path.dirname(p)) == proj else 1
        )
    injected = []
    if notes:
        out.append("\n## Recently-touched notes")
        for p in notes[:10]:
            b = os.path.splitext(os.path.basename(p))[0]
            fdr = os.path.basename(os.path.dirname(p))
            d = desc(p)
            out.append(f"- [[{b}]] ({fdr})" + (f" — {d}" if d else ""))
            injected.append(b)

    # --- Last-session rollup (tail of most-recent Daily) ---
    if dfiles:
        last = dfiles[-1]
        tail = [
            l.rstrip()
            for l in open(last, errors="ignore")
            if l.startswith("- ") and not _is_junk(l)
        ][-8:]
        if tail:
            out.append(
                f"\n## Most recent activity ({os.path.splitext(os.path.basename(last))[0]})"
            )
            out += tail

    # --- Current project's note index (one folder only, and capped) ---
    # Only the shard for the current repo is loaded; every OTHER folder is a one-line
    # [[_index-<folder>]] pointer in the thin MEMORY.md, and its notes come via recall.
    # The shard still grows with the notes in THIS folder, hence SHARD_MAX.
    if proj:
        shard = os.path.join(MEM, f"_index-{proj}.md")
        if os.path.exists(shard):
            body = re.sub(
                r"^---\n.*?\n---\n",
                "",
                open(shard, errors="ignore").read(),
                count=1,
                flags=re.S,
            )
            lines = [l for l in body.split("\n") if l.startswith("- [[")]
            if lines:
                out.append(f"\n## Note index — {proj} (this project)")
                out.append(_cap_index(lines, SHARD_MAX))

    # --- _Home map ---
    home = os.path.join(MEM, "_Home.md")
    if os.path.exists(home):
        out.append("\n## Home map")
        out.append(_cap(open(home, errors="ignore").read(), HOME_MAX, "map lines"))

    # --- Passive stale nudge (ambient; only when there's something to nudge) ---
    try:
        n = _stale_count(120)
        if n > 0:
            out.append(
                f"\n🕰 {n} notes not confirmed in 120+ days · run /second-brain stale"
            )
    except Exception as e:
        HL.log_err("session-resume.stale", e)

    out.append("=== end Obsidian resume ===")
    # Backstop: per-section caps bound the known offenders, this bounds the total in case
    # a future section (or an unusually large digest) grows past them.
    payload = "\n".join(out)
    if len(payload) > TOTAL_MAX:
        payload = (
            _cap(payload, TOTAL_MAX, "resume lines") + "\n=== end Obsidian resume ==="
        )
    sys.stdout.write(payload + "\n")

    # Dedup handshake: tell memory-recall (UserPromptSubmit) what we already surfaced,
    # so the first prompts don't re-inject the same notes.
    try:
        sid = hook.get("session_id") or "nosession"
        sdir = os.path.join(MEM, ".recall-state")
        os.makedirs(sdir, exist_ok=True)
        sf = os.path.join(sdir, re.sub(r"[^A-Za-z0-9_-]", "_", sid) + ".json")
        prev = set(HL.read_json(sf, {}).get("injected", []))
        HL.write_json(sf, {"injected": sorted(prev | set(injected))})
    except Exception as e:
        HL.log_err("session-resume.state", e)

    # Refresh the semantic index in the background (incremental; no-op if venv absent).
    # Detached so it never blocks session start.
    try:
        venv = HL.EMBED_VENV_PY
        embed = HL.EMBED_SCRIPT
        if HL.embed_ready():
            import subprocess

            subprocess.Popen(
                [venv, embed, "build"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **(HL.detach_kwargs() if HL else {}),
            )
    except Exception as e:
        HL.log_err("session-resume.embed", e)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        HL.log_err("session-resume", e)
