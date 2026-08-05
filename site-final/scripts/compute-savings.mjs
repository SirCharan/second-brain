/**
 * Recompute app/data/savings.json — the measured token/cost savings shown in
 * the SavingsDashboard section. Runs on ck's machine (launchd, daily); reads
 * only local Claude Code state and writes aggregate numbers. No note content,
 * no transcript content, ever leaves this script.
 *
 * Method (every constant disclosed on the page):
 *   gross  = rediscovery + resume + compaction savings, estimated per session
 *   cost   = tokens the memory system itself injects, discounted by cache reads
 *   net    = gross − cost;  usd = net × Opus input rate ($5/MTok)
 */

import fs from "node:fs";
import path from "node:path";
import os from "node:os";

// ── assumptions (the whole formula, in one block) ──────────────────────────
const SINCE = "2026-07-06"; // vault epoch — first day the memory system ran
const BYTES_PER_TOKEN = 4; // transcript bytes → tokens
const HIT_RATE = 0.25; // sessions where recall replaces a cold re-discovery
const TOKENS_PER_HIT = 20_000; // exploration a hit avoids (greps, reads, retries)
const RESUME_RATE = 0.175; // sessions resumed via the last-session digest
const TOKENS_PER_RESUME = 10_000; // re-establishing context the digest avoids
const COMPACTION_RATE = 0.045; // sessions where /clear+recall replaced compaction
const TOKENS_PER_COMPACTION = 30_000; // summarize pass + bloated-transcript re-pay
const INJECT_PER_SESSION = 7_000; // session-start payload (context, resume, indexes)
const INJECT_PER_TURN = 2_000; // per-prompt JIT recall
const CACHE_MULT = 0.2; // injected tokens ride the cached prefix (~0.1×–0.5×)
const USD_PER_MTOK = 5; // Claude Opus input, matches the TokenTax section

const HOME = os.homedir();
const PROJECTS = process.env.CLAUDE_PROJECTS_DIR || path.join(HOME, ".claude", "projects");
const VAULT = process.env.CLAUDE_MEMORY_DIR || path.join(PROJECTS, "-Users-ck", "memory");
const OUT = path.join(import.meta.dirname, "..", "app", "data", "savings.json");

// ── measure ─────────────────────────────────────────────────────────────────
const sinceMs = Date.parse(`${SINCE}T00:00:00Z`);

function* walk(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* walk(p);
    else yield p;
  }
}

let sessions = 0;
let transcriptBytes = 0;
for (const p of walk(PROJECTS)) {
  if (!p.endsWith(".jsonl")) continue;
  const st = fs.statSync(p);
  if (st.mtimeMs < sinceMs) continue;
  sessions += 1;
  transcriptBytes += st.size;
}

let notes = 0;
let turns = 0;
for (const p of walk(VAULT)) {
  if (!p.endsWith(".md")) continue;
  notes += 1;
  if (path.dirname(p).endsWith("Daily")) {
    const body = fs.readFileSync(p, "utf8");
    turns += (body.match(/^- \*\*/gm) || []).length;
  }
}

// ── formula ─────────────────────────────────────────────────────────────────
const throughput = Math.round(transcriptBytes / BYTES_PER_TOKEN);
const gross = Math.round(
  sessions * HIT_RATE * TOKENS_PER_HIT +
    sessions * RESUME_RATE * TOKENS_PER_RESUME +
    sessions * COMPACTION_RATE * TOKENS_PER_COMPACTION
);
const injectionRaw = sessions * INJECT_PER_SESSION + turns * INJECT_PER_TURN;
const injection = Math.round(injectionRaw * CACHE_MULT);
const net = gross - injection;
const usd = (net / 1e6) * USD_PER_MTOK;

// IST date for the daily history point
const ist = new Date(Date.now() + 5.5 * 3600 * 1000);
const today = ist.toISOString().slice(0, 10);

let history = [];
try {
  history = JSON.parse(fs.readFileSync(OUT, "utf8")).history || [];
} catch {
  /* first run */
}
history = history.filter((h) => h.date !== today);
history.push({ date: today, net_tokens: net, usd: Math.round(usd * 100) / 100 });
history.sort((a, b) => a.date.localeCompare(b.date));

const out = {
  computed_at: new Date().toISOString(),
  since: SINCE,
  sessions,
  turns,
  notes,
  throughput_tokens: throughput,
  gross_saved_tokens: gross,
  injection_cost_tokens: injection,
  net_saved_tokens: net,
  usd_saved: Math.round(usd * 100) / 100,
  pct_of_throughput: Math.round((net / throughput) * 1000) / 10,
  assumptions: {
    bytes_per_token: BYTES_PER_TOKEN,
    hit_rate: HIT_RATE,
    tokens_per_hit: TOKENS_PER_HIT,
    resume_rate: RESUME_RATE,
    tokens_per_resume: TOKENS_PER_RESUME,
    compaction_rate: COMPACTION_RATE,
    tokens_per_compaction: TOKENS_PER_COMPACTION,
    inject_per_session: INJECT_PER_SESSION,
    inject_per_turn: INJECT_PER_TURN,
    cache_mult: CACHE_MULT,
    usd_per_mtok: USD_PER_MTOK,
  },
  history,
};

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(out, null, 2) + "\n");
console.log(
  `savings.json: ${sessions} sessions · net ${(net / 1e6).toFixed(2)}M tok · $${out.usd_saved} · ${out.pct_of_throughput}% of throughput`
);
