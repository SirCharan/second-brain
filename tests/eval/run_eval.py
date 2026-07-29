#!/usr/bin/env python3
"""Score the recall ranker against a labelled query set. Pure stdlib.

    python3 tests/eval/build_set.py -o ~/.second-brain/eval/queries.jsonl
    python3 tests/eval/run_eval.py  ~/.second-brain/eval/queries.jsonl

Reports hit@1, hit@4 and MRR. hit@4 is the number that matters, because recall injects
four notes per prompt: it is the share of prompts where the note the user was actually
working on made it into the context window.

Nothing measured retrieval before this, so every scoring change was a guess. Record the
baseline, then require any ranking change to move it. `--compare` prints the delta
against a saved run, and `--gate` exits non-zero on a regression so CI can hold the line.
"""

import argparse, json, os, sys

_HOOKS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "hooks")
sys.path.insert(0, os.path.abspath(_HOOKS))
import sb_rank  # noqa: E402

K = 4  # how many notes recall injects per prompt


def load(path):
    rows = []
    with open(path, errors="ignore") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows


def score(rows, k=K, head_gate=sb_rank.HEAD_GATE, project_bias=True):
    """Run every query and return (summary, misses)."""
    hit1 = hitk = 0
    rr_total = 0.0
    empty = 0
    misses = []
    for r in rows:
        got = [
            x["name"]
            for x in sb_rank.rank(
                r["q"],
                project=r.get("project") if project_bias else None,
                limit=k,
                head_gate=head_gate,
            )
        ]
        want = set(r["expect"])
        if not got:
            empty += 1
        rank_of = next((i for i, n in enumerate(got) if n in want), None)
        if rank_of == 0:
            hit1 += 1
        if rank_of is not None:
            hitk += 1
            rr_total += 1.0 / (rank_of + 1)
        else:
            misses.append((r, got))
    n = len(rows) or 1
    return (
        {
            "queries": len(rows),
            "hit@1": hit1 / n,
            "hit@%d" % k: hitk / n,
            "mrr": rr_total / n,
            "empty": empty / n,
        },
        misses,
    )


def _fmt(s, k=K):
    return (
        "queries %d | hit@1 %.3f | hit@%d %.3f | MRR %.3f | returned nothing %.3f"
        % (s["queries"], s["hit@1"], k, s["hit@%d" % k], s["mrr"], s["empty"])
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("queries")
    ap.add_argument(
        "-k", type=int, default=K, help="cut-off (default 4 = what recall injects)"
    )
    ap.add_argument(
        "--show-misses", type=int, default=0, help="print N failing queries"
    )
    ap.add_argument(
        "--head-gate",
        type=int,
        default=None,
        help="override HEAD_GATE to test the ceiling",
    )
    ap.add_argument("--no-project-bias", action="store_true")
    ap.add_argument("--save", help="write this run's summary as JSON")
    ap.add_argument("--compare", help="print the delta against a saved run")
    ap.add_argument(
        "--gate",
        action="store_true",
        help="exit 1 if --compare shows a hit@k regression",
    )
    a = ap.parse_args()

    rows = load(a.queries)
    if not rows:
        sys.exit("no queries in %s" % a.queries)
    gate = sb_rank.HEAD_GATE if a.head_gate is None else a.head_gate
    summary, misses = score(rows, a.k, gate, not a.no_project_bias)

    print("vault      %s" % sb_rank._mem())
    print("notes      %d" % len(sb_rank.all_notes()))
    print(
        "head_gate  %d%s"
        % (gate, "  (shipped default)" if gate == sb_rank.HEAD_GATE else "  (OVERRIDE)")
    )
    print(_fmt(summary, a.k))

    if a.show_misses:
        print("\n--- misses (expected note absent from top %d) ---" % a.k)
        for r, got in misses[: a.show_misses]:
            print("\nQ    %s" % r["q"][:110])
            print("want %s" % ", ".join(r["expect"]))
            print("got  %s" % (", ".join(got) if got else "(nothing)"))

    if a.compare:
        try:
            old = json.load(open(a.compare))
        except Exception as e:
            sys.exit("cannot read %s: %s" % (a.compare, e))
        kk = "hit@%d" % a.k
        d_hit = summary[kk] - old.get(kk, 0.0)
        d_mrr = summary["mrr"] - old.get("mrr", 0.0)
        print(
            "\nvs %s:  %s %+.3f   MRR %+.3f"
            % (os.path.basename(a.compare), kk, d_hit, d_mrr)
        )
        if a.gate and d_hit < 0:
            sys.exit("REGRESSION: %s dropped %+.3f" % (kk, d_hit))

    if a.save:
        os.makedirs(os.path.dirname(os.path.abspath(a.save)), exist_ok=True)
        with open(a.save, "w") as f:
            json.dump(summary, f, indent=2)
        print("saved -> %s" % a.save)


if __name__ == "__main__":
    main()
