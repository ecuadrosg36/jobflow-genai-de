# JobFlow GenAI (Data Engineer)

A small pipeline that finds Data Engineer job posts every day, ranks them against my CV, and drafts an
application pack for the best ones with an LLM.

## How it works

```text
JobSpy scrape ─▶ normalize ─▶ SQLite (dedupe) ─▶ keyword score ─▶ top N ─▶ LLM pack per job ─▶ output/
```

1. **Ingest** (`jobflow/ingest/`): `python-jobspy` searches the sites, keywords and location in
   `config/config.yaml` (LinkedIn, Indeed, Google Jobs, ZipRecruiter; posts from the last 72 hours).
2. **Normalize** (`jobflow/transform/`): trims whitespace, drops posts with no title, company or URL, and
   guesses the language (English or Spanish).
3. **Store** (`jobflow/storage/`): SQLite at `data/jobflow.db`. A unique key on title + company + location
   keeps the same job from two boards once. Jobs already turned into packs are not scored again.
4. **Score** (`jobflow/rank/`): keyword matching, no LLM. `0.55 × CV word overlap + 0.30 × must-have skills
   + 0.15 × nice-to-have skills`. Posts under `min_match_score` are dropped; the top `daily_top_n` go on.
5. **Generate** (`jobflow/generate/`): for each top job, an OpenAI-compatible chat API (Groq by default)
   writes a cover letter, a LinkedIn message and a tailored CV summary. RenderCV turns the tailored CV
   into a PDF; if that fails, a Markdown resume is written instead.
6. **Publish** (`jobflow/publish/`): writes the top jobs to `../enmacuadroswork/public/data/latest_jobs.json`
   for the job board on my portfolio site.

Output for one run:

```text
output/YYYY-MM-DD/
├── top_jobs.csv
└── job_<id>_pack/
    ├── job.json, score.json
    ├── cover_letter_EN.txt (or _ES)
    ├── linkedin_message.txt
    ├── cv_tailored.yaml + the RenderCV PDF   (or resume_EN.md if rendering failed)
```

## Safety

Job posts are scraped web text, so they are treated as untrusted:

- The prompt tells the model to treat the posting as information only and ignore instructions inside it.
- The tailored summary must come back as a short list of strings (max 6 lines, 400 characters each);
  anything else is discarded and the base summary is kept.
- RenderCV is called with an argument list, never through a shell, because folder names contain the
  scraped job ID.
- Contact details are not in the repo: they live in `data/cv.local.yaml`, which is git-ignored.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export LLM_API_KEY="your_groq_api_key"   # or OPENAI_API_KEY; not needed for a local Ollama URL
# optional: LLM_BASE_URL (default https://api.groq.com/openai/v1), LLM_MODEL (default llama-3.1-8b-instant)

python -m jobflow.run --once
```

**Your CV.** `data/cv.yaml` is the CV in RenderCV format, without email or phone. Copy it to
`data/cv.local.yaml` and add your contact details there; JobFlow uses the local file when it exists.
`data/cv.pdf` is optional and only used for scoring; without it, the CV YAML text is used.

**Scheduling.** `scripts/setup_schedule.ps1` registers an hourly Windows Task Scheduler job. The GitHub
workflow `daily.yml` runs only on demand: add an `LLM_API_KEY` secret first. `scripts/publish_existing.py`
republishes the top 20 scored jobs from the database without scraping.

## Tests

```bash
pip install pytest
python -m pytest -q
```

CI runs a syntax-level `ruff` check and the tests on every push. Tests cover cleaning, deduplication,
scoring, the LLM reply check, CV handling between jobs, network retries and the RenderCV call. The LLM and
the scraper are replaced with fakes, so tests need no network or API key.

## Limits

- Scoring is keyword overlap, so a post that describes the same skills in other words scores low.
- Scraping depends on JobSpy and the job boards' pages; results vary and can break when a site changes.
- The publish path points at a sibling folder and is created if missing.
