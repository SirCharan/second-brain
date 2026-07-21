# second-brain — final landing (`site-final`)

Greenfield marketing page. Separate Vercel project from `site/` and `site-v2/`.

## Stack

Next.js 16 · Tailwind v4 · App Router · Gambarino display

## Dev

```bash
cd site-final
npm install
npm run dev
```

## Deploy

```bash
# new project only — never point at second-brain / second-brain-cinema / second-brain-web
vercel --prod --yes --name second-brain-final \
  --scope team_QUgI2tENi0Wo8L7m2s2GoATi \
  --token $VERCEL_TOKEN_CKDELTA
```
