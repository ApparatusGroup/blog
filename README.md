AI Agents Blog (prototype)
=================================

Overview
--------
This repository contains a minimal prototype of a blog driven by AI agents. The pipeline is:

- Researcher: gathers facts/summaries about a topic
- Drafter: converts research into a Markdown draft
- Editor: applies simple edits / checks
- Publisher: writes articles to `public/posts` and updates `public/index.html`

This scaffold is runnable locally and includes hooks where you can plug a real LLM (OpenAI, etc.) later for high-quality writing.

Quick start
-----------

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/Scripts/activate   # on Windows use: .venv\\Scripts\\activate
pip install -r requirements.txt
```

2. Run a single pipeline run (draft + publish one article):

```bash
python -m src.main
```

3. Generated posts will appear in `public/posts` and `public/index.html` will be updated.

Next steps
----------
- Plug a real LLM for `Drafter`/`Editor` by setting an environment variable and implementing the adapter in `src/agents/llm_adapter.py`.
- Add scheduling (cron or a task runner) to make the pipeline self-sustaining.

Vercel deployment
-----------------
This project can be deployed as a static site on Vercel. The repository includes a `package.json` script that will run the generator during the Vercel build step and output static files into `public/`.

Before deploying, set your OpenRouter API key in Vercel environment variables:

- `OPENROUTER_API_KEY` — your API key
- `OPENROUTER_URL` — optional custom OpenRouter endpoint

On Vercel, the `vercel-build` script will run `python -m src.main` to generate `public/` content.

Scheduling options
------------------
You have two practical ways to schedule generation:

- Daily build on Vercel (free plan): Vercel allows cron builds once per day. Configure a Vercel Cron Job in the dashboard to run `python -m src.main`, or use the GitHub Actions workflow included here which will run once per day and commit generated `public/` files back to the repository so Vercel rebuilds on push.
- Local scheduler: run the project on a server or VM with the local scheduler. Example to run every 60 minutes:

```bash
python -m src.main --mode local --interval 60
```

The repository includes `.github/workflows/daily_publish.yml` which runs daily and commits `public/` updates. Set your OpenRouter keys in GitHub Secrets as `OPENROUTER_API_KEY` and optional `OPENROUTER_URL`.

Files of interest
- `src/orchestrator.py`: pipeline flow
- `src/agents/*.py`: agent implementations
- `src/publisher.py`: writes files to `public/`

License
-------
Prototype code — adapt as needed.
