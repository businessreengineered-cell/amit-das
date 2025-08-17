# Jarvis Railway PWA (with Tools)

Your personal Jarvis-like assistant running on Railway.

## Features
- Voice & Chat (via OpenAI API)
- Persistent memory (`/app/data`)
- Tools included:
  - ✅ Calculator
  - ✅ Todo manager
  - ✅ Mock device control (lights, fan)
- PWA frontend (add to iPhone Home Screen)

## Deploy on Railway (Free Tier)

1. Push this repo to GitHub.
2. Go to [Railway](https://railway.app) → New Project → Deploy from GitHub.
3. Add Environment Variables:
   - `OPENAI_API_KEY` → your OpenAI key
   - `JARVIS_ADMIN_SECRET` → password you choose
4. Add a Persistent Volume and mount it to `/app/data`.
5. Deploy. In ~2 minutes you’ll get a public HTTPS URL.

## Deploy Button

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=YOUR_GITHUB_REPO_URL&envs=OPENAI_API_KEY,JARVIS_ADMIN_SECRET)
