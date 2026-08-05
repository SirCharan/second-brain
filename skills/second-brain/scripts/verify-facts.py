#!/usr/bin/env python3
"""Set-based fact-token verifier for vault restructures.

Extracts fact tokens from every .md inside a backup tarball and checks each one still
exists SOMEWHERE in the current vault. Facts legitimately move between notes during a
split/merge, so this compares vault-wide sets, not per-file diffs.

Fact tokens: URLs, UPPER_SNAKE flags, hex ids (7-40 chars), numbers with a unit
(%/KB/MB/s/d/x/$), and bare numbers of 3+ digits.

Usage: verify-facts.py <backup.tar.gz> [vault_dir]
Exit 0 = no facts lost. Exit 1 = missing tokens (printed with their source note).
"""

import io
import os
import re
import sys
import glob
import tarfile

# Windows defaults to cp1252 for console output AND for open(, encoding="utf-8"), so both printing a status
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

SKIP_SEGS = ("Daily", "Weekly", "Sessions", "_system")
TOKEN_RE = re.compile(
    r"https?://[^\s)\]>\"']+"  # URLs
    r"|\b[A-Z][A-Z0-9_]{3,}\b"  # UPPER_SNAKE flags / env vars
    r"|\b[0-9a-f]{7,40}\b"  # commit ids / hex
    r"|\b\d+(?:\.\d+)?\s?(?:%|KB|MB|GB|ms|s|d|x|\$)"  # numbers with unit
    r"|\b\d{3,}\b"  # bare numbers 3+ digits
)


def _skip(relpath):
    parts = relpath.split("/")
    if parts[-1].startswith("._"):  # macOS AppleDouble resource forks in tars
        return True
    return any(p in SKIP_SEGS or p.startswith(("_backup", ".")) for p in parts[:-1])


def tokens(text):
    return set(TOKEN_RE.findall(text))


def backup_tokens(tar_path):
    """token -> first source member that carried it."""
    out = {}
    with tarfile.open(tar_path, encoding="utf-8") as tf:
        for m in tf.getmembers():
            if not m.name.endswith(".md") or _skip(m.name):
                continue
            f = tf.extractfile(m)
            if not f:
                continue
            text = io.TextIOWrapper(f, errors="ignore").read()
            for t in tokens(text):
                out.setdefault(t, m.name)
    return out


def current_tokens(vault):
    out = set()
    for p in glob.glob(os.path.join(vault, "**", "*.md"), recursive=True):
        rel = os.path.relpath(p, vault)
        if any(seg.startswith(("_backup", ".")) for seg in rel.split(os.sep)[:-1]):
            continue  # backups moved out don't count as "still present"
        try:
            out |= tokens(open(p, errors="ignore", encoding="utf-8").read())
        except Exception:
            pass
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    tar_path = sys.argv[1]
    vault = (
        sys.argv[2]
        if len(sys.argv) > 2
        else (
            os.environ.get("CLAUDE_MEMORY_DIR")
            or os.path.expanduser("~/.claude/second-brain-vault")
        )
    )
    bt = backup_tokens(tar_path)
    ct = current_tokens(vault)
    missing = sorted((t, src) for t, src in bt.items() if t not in ct)
    print(
        f"backup tokens: {len(bt)} · current tokens: {len(ct)} · missing: {len(missing)}"
    )
    for t, src in missing[:50]:
        print(f"  MISSING {t!r}  (was in {src})")
    if len(missing) > 50:
        print(f"  ... and {len(missing) - 50} more")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
