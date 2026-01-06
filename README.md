# JobFlow GenAI (Data Engineer)

A practical, daily-running helper to **find** Data Engineer roles and prepare an **application pack** per job using GenAI.

# JobFlow GenAI (Data Engineer)

**Automated Career Agent** that finds matching Data Engineer roles and generates tailored application packs using GenAI.

## 🏗️ Technical Architecture & Logic

This project implements a **Modern Cloud-Native Data Pipeline**, designed to run completely locally or in the cloud.

### 🔄 Data Flow (The "JobFlow")
1.  **Ingestion Layer**: 
    - **Tool**: `JobSpy` (Scraper)
    - **Logic**: Aggregates jobs from LinkedIn, Indeed, Glassdoor, and ZipRecruiter in parallel.
    - **Outcome**: Raw `pandas.DataFrame` of job postings.

2.  **Storage & State Layer**:
    - **Tool**: `SQLite` (Local embedded DB)
    - **Logic**: Handles de-duplication (UPSERT) to ensure you never process the same job twice. Tracks "New" vs "Applied" status.

3.  **Reasoning Engine (The "Brain")**:
    - **Tool**: LLM (Groq LPU / OpenAI)
    - **Logic**: 
        - **Scoring**: Calculates a 0-1 match score based on *Semantic Skills Overlap*.
        - **Ranking**: Filters out unrelated roles (e.g., "Data Analyst" when you want "Data Engineer").

4.  **Generation Layer**:
    - **Tool**: `RenderCV` + `Jinja2`
    - **Logic**: 
        - Reads your Master CV (`cv.yaml`).
        - **Dynamically rewrites** your "Summary" and "Highlights" to match the specific Job Description.
        - Compiles a high-quality PDF (`cv_tailored.pdf`) using LaTeX under the hood.

5.  **Presentation Layer**:
    - **Outcome**: A structured folder `output/YYYY-MM-DD/job_ID/` containing:
        - `cv_tailored.pdf` (Ready to upload)
        - `cover_letter.txt`
        - `recruiter_message.txt`

---

## 🚀 Full Execution Guide

### 1) Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies (JobSpy, RenderCV, etc.)
pip install -r requirements.txt
```

### 2) Data Preparation
- **Master CV**: I have already populated `data/cv.yaml` with your real experience (Tenmas, Neoris, Indra, Vooxell). This is the source of truth.
- **Matching CV**: The file `data/cv.pdf` is used only for the initial keyword matching score.

### 3) Configuration (Groq Fast-Path)
The project is pre-configured to use **Groq** for extreme speed.
**Set your API Key** (Run this in your terminal):
```bash
# Windows PowerShell
$env:LLM_API_KEY="your_groq_api_key_here"

# Mac/Linux
export LLM_API_KEY="your_groq_api_key_here"
```

### 4) Pipeline Execution
Run the full automated flow (Ingest → Normalize → Score → Generate PDF):
```bash
# Run once to process current jobs
python -m jobflow.run --once
```

### 5) Result Review
Check the `output/YYYY-MM-DD/` folder. You will find a subfolder for each job containing your **Taillored PDF Resume** and specific Cover Letter.

## 🌍 Remote Search Strategy
To optimize for **International Remote Roles**:
1. Check `config/config.yaml`.
2. Ensure `location` is set to global markets (e.g., "USA", "Remote", "Europe").
3. The LLM prompts are optimized to highlight **Autonomy**, **Async Communication**, and **Production Reliability**.

---
**Built for automated Data Engineering career growth** 🚀
