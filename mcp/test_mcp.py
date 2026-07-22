#!/usr/bin/env python3
"""Stdlib self-test for the second-brain MCP layer. No framework.
Runs against a throwaway CLAUDE_MEMORY_DIR so it never touches the real vault.
Exits nonzero on any failure."""

import os, sys, json, re, tempfile, subprocess, importlib

_THIS = os.path.dirname(os.path.abspath(__file__))


def _fixture_vault():
    d = tempfile.mkdtemp(prefix="sb-mcp-test-")
    os.makedirs(os.path.join(d, "drishti"))
    os.makedirs(os.path.join(d, "tatkaal"))
    # a note that should win a "drishti signal cadence" query
    open(os.path.join(d, "drishti", "drishti-cadence.md"), "w").write(
        "---\nname: drishti-cadence\ndescription: Drishti signal cadence is a 5-minute cycle.\n"
        "last_confirmed: %s\nstatus: active\n---\n# Drishti cadence\n\nBody about signal cadence.\n"
        % _today()
    )
    # an unrelated note that should not win
    open(os.path.join(d, "tatkaal", "tatkaal-assets.md"), "w").write(
        "---\nname: tatkaal-assets\ndescription: Tatkaal covers three crypto assets.\n"
        "last_confirmed: 2020-01-01\nstatus: active\n---\n# Tatkaal assets\n\nBTC ETH PAXG.\n"
    )
    return d


def _today():
    import time

    return time.strftime("%Y-%m-%d")


def load_core(mem):
    os.environ["CLAUDE_MEMORY_DIR"] = mem
    sys.path.insert(0, _THIS)
    import sb_core

    importlib.reload(
        sb_core.HL
    )  # recompute _hooklib.MEM from env (it caches at import)
    importlib.reload(sb_core)  # recompute sb_core.MEM from HL.MEM
    return sb_core


def demo():
    fails = []

    # 1. write_note round-trips a parseable v2 note
    mem = tempfile.mkdtemp(prefix="sb-mcp-write-")
    C = load_core(mem)
    path = C.write_note(
        "Test Fact One",
        "This is the body of a test fact.",
        description="a short desc",
        note_type="fact",
    )
    assert os.path.isfile(path), "write_note did not create a file"
    raw = open(path).read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    assert m, "note has no parseable frontmatter"
    fm = dict(re.findall(r"^(\w[\w.]*):\s*(.*)$", m.group(1), re.M))
    for k in ("name", "title", "description", "status", "source"):
        if k not in fm:
            fails.append("frontmatter missing %s" % k)
    assert fm.get("name") == "test-fact-one", "bad slug: %s" % fm.get("name")
    assert "🟢 **active**" in raw, "missing status chip"
    assert "## Related" in raw, "missing Related section"
    # secret scrubbing on input
    p2 = C.write_note("Secret Note", "token=abcdef0123456789ABCDEF secret here")
    assert "[REDACTED]" in open(p2).read(), "secret not scrubbed"
    # no clobber: re-writing appends an Update section
    C.write_note("Test Fact One", "second body")
    assert "## Update" in open(path).read(), "existing note was not enriched"

    # 2. rank() returns the relevant note first on a fixture vault
    fmem = _fixture_vault()
    C = load_core(fmem)
    hits = C.rank("drishti signal cadence cycle", limit=3)
    assert hits, "rank returned nothing"
    assert hits[0]["name"] == "drishti-cadence", "wrong top hit: %r" % (hits[:1])

    # 3. JSON-RPC handshake against server_stdio via subprocess pipe
    frames = (
        "\n".join(
            json.dumps(f)
            for f in [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "recall",
                        "arguments": {"query": "drishti signal cadence"},
                    },
                },
            ]
        )
        + "\n"
    )
    env = dict(os.environ, CLAUDE_MEMORY_DIR=fmem)
    r = subprocess.run(
        ["/usr/bin/python3", os.path.join(_THIS, "server_stdio.py")],
        input=frames,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    resps = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    assert len(resps) == 3, "expected 3 responses, got %d (stderr: %s)" % (
        len(resps),
        r.stderr,
    )
    assert resps[0]["result"]["protocolVersion"] == "2024-11-05", "bad protocolVersion"
    assert resps[0]["result"]["serverInfo"]["name"] == "second-brain"
    names = {t["name"] for t in resps[1]["result"]["tools"]}
    assert {
        "recall",
        "capture",
        "learn",
        "pull",
        "export",
        "health",
        "stale",
        "graph",
    } <= names, "tools/list missing tools: %r" % names
    text = resps[2]["result"]["content"][0]["text"]
    assert "drishti-cadence" in text, "recall tool did not surface the note: %r" % text

    if fails:
        print("FAIL:\n  " + "\n  ".join(fails))
        sys.exit(1)
    print("ok — write_note, rank, and the stdio JSON-RPC handshake all pass")


if __name__ == "__main__":
    demo()
