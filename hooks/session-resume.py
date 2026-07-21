#!/usr/bin/env python3
"""SessionStart(startup|clear) hook: inject LIVING Obsidian state so a new chat resumes.
Emits (project-aware, via cwd): recent Daily captures + recently-modified notes +
last-session rollup + the _Home map. Read-only; never raises; prints nothing on other sources."""

import sys, os, json, re, glob

import _hooklib as HL

MEM = HL.MEM
DAILY = os.path.join(MEM, "Daily")
EXCLUDE = {"MEMORY.md", "context.md", "_session-log.md", "_Home.md"}


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

    # --- Current project's note index (folder-bounded — grows with folders, not notes) ---
    # Only the shard for the current repo is loaded; every OTHER folder is a one-line
    # [[_index-<folder>]] pointer in the thin MEMORY.md, and its notes come via recall.
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
                out += lines

    # --- _Home map ---
    home = os.path.join(MEM, "_Home.md")
    if os.path.exists(home):
        out.append("\n## Home map")
        out.append(open(home, errors="ignore").read())

    out.append("=== end Obsidian resume ===")
    sys.stdout.write("\n".join(out) + "\n")

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
        venv = os.path.expanduser("~/.claude/hooks/.venv-embed/bin/python")
        embed = os.path.expanduser("~/.claude/hooks/memory-embed.py")
        if os.path.exists(venv) and os.path.exists(embed):
            import subprocess

            subprocess.Popen(
                [venv, embed, "build"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
    except Exception as e:
        HL.log_err("session-resume.embed", e)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        HL.log_err("session-resume", e)
