#!/bin/zsh
# Daily savings refresh: recompute → commit → push → deploy.
# Driven by launchd (com.ck.secondbrain-savings), 09:00 IST. Log: refresh-savings.log
set -euo pipefail

SITE="$HOME/second-brain/site-final"
LOG="$SITE/scripts/refresh-savings.log"
exec >>"$LOG" 2>&1
echo "── $(date '+%Y-%m-%d %H:%M:%S') refresh start"

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
cd "$SITE"

# Vercel token from lakshmi (credentials source of truth)
export VERCEL_TOKEN_CKDELTA="$(grep '^VERCEL_TOKEN_CKDELTA=' "$HOME/claude/lakshmi/.env" | cut -d= -f2-)"

node scripts/compute-savings.mjs

if git -C "$HOME/second-brain" diff --quiet -- site-final/app/data/savings.json; then
  echo "no change — skip"
  exit 0
fi

git -C "$HOME/second-brain" pull --rebase --autostash origin main
git -C "$HOME/second-brain" add site-final/app/data/savings.json
git -C "$HOME/second-brain" commit -m "data: daily savings point $(date '+%Y-%m-%d')"
git -C "$HOME/second-brain" push origin main

# ck-delta Vercel git auto-deploy is flaky — always deploy explicitly.
npx vercel --prod --yes --token "$VERCEL_TOKEN_CKDELTA" --scope team_QUgI2tENi0Wo8L7m2s2GoATi
echo "done $(date '+%H:%M:%S')"
