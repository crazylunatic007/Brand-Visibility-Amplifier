# Query Fan-Out & Content Recommendation Tool

## Overview

This tool helps content creators optimize existing articles by generating **search query fan-outs** — the same way Google AI Overviews, ChatGPT Search, and Perplexity internally decompose a user query into multiple sub-queries. You enter a keyword, the tool generates related queries across 8 fan-out categories, you select which ones to target, provide a URL to your existing content, and the tool analyzes where each query should be added. The final output is a Google Docs file with placement recommendations and ready-to-publish content.

---

## Prerequisites

| Requirement | Required? | Where to get it |
|-------------|-----------|-----------------|
| **Python 3.10+** | Yes | [python.org/downloads](https://www.python.org/downloads/) |
| **Gemini API Key** | Yes | [Google AI Studio](https://aistudio.google.com/apikey) |
| **Semrush API Key** | Optional | [Semrush](https://www.semrush.com/) — for validating queries with real search volume data |
| **Google Cloud Project** | Optional | [Google Cloud Console](https://console.cloud.google.com/) — only needed for Step 5 (exporting to Google Docs) |

---

## Installation & Starting the App

### 1. Install dependencies

Open a terminal in the project folder and run:

```
cd "C:\Users\faizr\OneDrive\Desktop\Query generator and contetn writer tool"
pip install -r requirements.txt
```

### 2. Start the app

```
py -m streamlit run app.py
```

> **Windows PATH note:** If `py` is not recognized, use the full path:
> ```
> "C:\Users\faizr\AppData\Local\Programs\Python\Python314\python.exe" -m streamlit run app.py
> ```

The app will open in your browser at `http://localhost:8501`.

---

## Google Drive Setup (Optional — for Step 5 Export)

This is only needed if you want to export recommendations to Google Docs. Steps 1-4 work without it.

### One-time setup in Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. **Enable 2 APIs:**
   - Google Drive API
   - Google Docs API
4. **Configure OAuth Consent Screen:**
   - Go to APIs & Services > OAuth consent screen
   - Choose "External"
   - Fill in: App name (`Query Fan-Out Tool`), your email for support and developer contact
   - Add scopes: `drive.file` and `documents`
   - Add your Gmail address as a **test user**
   - Save
5. **Create OAuth Client ID:**
   - Go to APIs & Services > Credentials
   - Create Credentials > OAuth Client ID
   - Application type: **Desktop App**
   - Download the JSON file
   - Rename it to `client_secret.json`
   - Place it in: `credentials/client_secret.json`

After this, clicking "Connect Google Account" in the app sidebar will open a browser for Google sign-in.

> **Note:** When signing in, you'll see "Google hasn't verified this app" — click **Continue** (it's your own app, this is safe).

---

## How to Use the Tool

### Sidebar (configure first)

Before starting, set up the sidebar:

| Setting | What it does |
|---------|-------------|
| **Gemini API Key** | Required. Enter your key and click "Validate Gemini Key". A green checkmark confirms it's working. |
| **Semrush API Key** | Optional. If provided, you can validate generated queries against real search volume data. |
| **Brand Guidelines** | Optional. Upload a PDF, DOCX, or TXT brand guidelines document. The tool extracts your brand's tone, voice, terminology, and rules, then applies them to all generated content. |
| **Google Drive** | Optional. Click "Connect Google Account" to enable Step 5 (Google Docs export). Requires `client_secret.json` setup (see above). |

### Step 1: Enter Keyword

- Type your **seed keyword** (e.g., "content marketing strategy")
- Optionally select an **industry/niche** for more relevant queries
- Choose your **query source:**
  - **Generate with Gemini** — AI generates queries using the fan-out pipeline
  - **Upload my own queries** — Upload a CSV, TXT, or XLSX file with your own queries
  - **Both** — Generate with Gemini AND upload your own, merged and deduplicated
- Click the action button to proceed

### Step 2: Select Queries

- Queries are displayed **grouped by fan-out type** (Equivalent, Follow-Up, Generalization, Specification, Canonicalization, Language Translation, Entailment, Clarification)
- Each query shows: **checkbox**, query text, **intent badge** (Informational/Transactional/Navigational/Commercial), and rationale
- If Semrush is configured, click **"Validate with Semrush"** to see search volume and keyword difficulty for each query
- Use **Select All / Deselect All** buttons per category
- A running count shows how many queries you've selected
- Click **"Continue with Selected Queries"**

### Step 3: Enter URL

- Enter the **URL of your existing content** (the article you want to optimize)
- Click **"Fetch & Analyze Content"**
- The tool scrapes the page and extracts its heading structure (H1-H6), body text, word counts
- Review the **content preview** showing title, section count, total words, and heading hierarchy
- Click **"Proceed to Analysis"**

### Step 4: Review Analysis

- Gemini analyzes where each selected query fits best in your existing content
- **Two-column layout:**
  - Left: **Content Outline** — your article's headings with red badges showing how many queries target each section
  - Right: **Placement Cards** — for each query:
    - Target section
    - Placement type (New Subsection / Expand Existing / New Paragraph)
    - Suggested heading (for new subsections)
    - Content brief (what to write)
    - **Generated Content** (expandable — full ready-to-use paragraphs)
    - Reasoning (expandable)
- **Remove** any placements you don't want
- Click **"Export to Google Docs"**

### Step 5: Export to Google Docs

- Requires Google account connection (sidebar)
- Click **"Create Google Doc"**
- A formatted Google Doc is created in your Drive with:
  - Header with source URL and article title
  - Recommendations grouped by content section
  - For each placement: target query, placement type, intent, content brief, full generated content, and reasoning
- A clickable **link to the Google Doc** is shown
- Click **"Start Over"** to begin a new analysis

---

## How Query Fan-Out Works

The tool uses a **3-stage pipeline** that mirrors how Google AI Overviews, ChatGPT Search, and Perplexity internally decompose queries. This is based on the architecture documented in **Google Patent US12158907B1 ("Thematic Search")** and industry research on LLM-driven query decomposition.

### Stage 1: Query Analysis

Gemini analyzes the seed query to determine:
- User intent (informational, transactional, navigational, commercial investigation)
- Query complexity (simple factual vs. complex multi-faceted)
- Key entities and attributes

### Stage 2: Generate 8 Fan-Out Types

The seed query is decomposed into sub-queries across **8 categories**:

| Fan-Out Type | What it does | Example (seed: "content marketing strategy") |
|-------------|-------------|----------------------------------------------|
| **Equivalent** | Same question, different words | "content marketing plan", "content strategy approach" |
| **Follow-Up** | Logical next questions | "how to measure content marketing ROI" |
| **Generalization** | Broader versions | "digital marketing strategy", "marketing strategy" |
| **Specification** | Narrower, more detailed | "B2B content marketing strategy for SaaS startups" |
| **Canonicalization** | Standardized phrasing | "content marketing strategy definition" |
| **Language Translation** | Different languages or jargon levels | "estrategia de marketing de contenidos", "content strategy for beginners" |
| **Entailment** | Logically implied questions | "what content types perform best", "how often to publish content" |
| **Clarification** | Disambiguation | "content marketing strategy vs content strategy", "content marketing for B2B vs B2C" |

### Stage 3: Self-Critique

Gemini acts as a **critic model** and evaluates each generated query:
- Is it genuinely distinct from others? (removes duplicates)
- Would a real search engine generate this? (removes implausible ones)
- Does it add unique retrieval coverage? (removes redundant ones)

Only queries that pass all 3 checks are included.

---

## Query Upload Format

When uploading your own queries, the tool supports 3 file formats:

### TXT (one query per line)
```
best content marketing tools
how to measure content ROI
content marketing vs paid ads
```

### CSV (with optional columns)
```csv
query,intent,query_type,rationale
best content marketing tools,commercial_investigation,specification,Targets tool evaluation queries
how to measure content ROI,informational,follow_up,Captures measurement intent
```

Only the `query` column is required. Recognized column names: `query`, `query_text`, `keyword`, `search_query`, `queries`.

### XLSX
Same columns as CSV, in an Excel spreadsheet.

If no recognized headers are found, the tool treats the first column as query text and assigns default values.

---

## Brand Guidelines

Upload your brand guidelines document (PDF, DOCX, or TXT) in the sidebar to ensure all generated content matches your brand's voice.

### How it works:

1. **Upload** — Drop your brand guidelines file in the sidebar uploader
2. **Process** — Click "Process Guidelines". Gemini extracts a structured brand voice profile covering:
   - Voice & tone (formal/casual, first/second/third person, emotional register)
   - Writing style (sentence structure, paragraph length, formatting preferences)
   - Terminology (preferred terms, banned words, jargon stance)
   - Audience & persona (who you're writing for, knowledge level)
   - Content rules (dos/don'ts, CTA style, citation handling)
3. **Apply** — The brand profile is automatically injected into every content generation call. Generated content follows your brand guidelines exactly.
4. **Review** — Click "View Brand Profile" in the sidebar to see the extracted profile

Brand guidelines are **optional** — if none are uploaded, the tool matches the tone of the existing article instead.

---

## Project Structure

```
query-fanout-tool/
├── app.py                      # Main Streamlit entry point (5-step wizard)
├── config.py                   # Model name, temperatures, token limits
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
├── DOCUMENTATION.md            # This file
├── .gitignore                  # Ignores credentials/, .env, __pycache__
├── .streamlit/
│   └── config.toml             # Streamlit theme configuration
├── auth/
│   ├── gemini_auth.py          # Gemini API key validation + model init
│   └── google_oauth.py         # Google OAuth2 flow for Drive/Docs
├── core/
│   ├── query_fanout.py         # Gemini-powered query fan-out generation
│   ├── query_uploader.py       # Parse uploaded CSV/TXT/XLSX query files
│   ├── query_validator.py      # Optional Semrush validation
│   ├── content_parser.py       # URL fetching + HTML structure extraction
│   ├── content_analyzer.py     # Query-to-content mapping + content generation
│   ├── brand_parser.py         # Brand guidelines extraction from uploaded docs
│   └── docs_builder.py         # Google Docs creation with formatted output
├── prompts/
│   └── templates.py            # All Gemini prompt templates (4 prompts)
├── models/
│   └── schemas.py              # Pydantic data models
├── ui/
│   ├── sidebar.py              # Sidebar: API keys, brand upload, Google OAuth
│   ├── step_keyword.py         # Step 1: Keyword input + query source selection
│   ├── step_fanout.py          # Step 2: Query selection with grouping
│   ├── step_url.py             # Step 3: URL input + content preview
│   ├── step_analysis.py        # Step 4: Placement review + content generation
│   └── step_export.py          # Step 5: Google Docs export
└── credentials/                # gitignored — OAuth tokens + client_secret.json
```

---

## Technical Details

| Setting | Value | File |
|---------|-------|------|
| **AI Model** | Gemini 2.5 Flash | `config.py` |
| **Fan-out generation temperature** | 0.9 (high diversity) | `config.py` |
| **Content analysis temperature** | 0.4 (analytical accuracy) | `config.py` |
| **Content generation temperature** | 0.7 (balanced) | `core/content_analyzer.py` |
| **Max output tokens** | 8192 | `config.py` |
| **URL fetch timeout** | 15 seconds | `config.py` |
| **Max content length** | 50,000 characters | `config.py` |
| **JSON response mode** | `response_mime_type: "application/json"` | `core/query_fanout.py` |
| **JSON repair** | Regex extraction of complete objects from truncated responses | `core/query_fanout.py` |
| **Pydantic validation** | Invalid queries silently skipped, not crashed | `core/query_fanout.py` |
| **Brand text truncation** | 30,000 characters max | `core/brand_parser.py` |

### Gemini Prompts Used

| Prompt | Purpose | File |
|--------|---------|------|
| `QUERY_FANOUT_PROMPT` | 3-stage pipeline: Query Analysis → Generate 8 fan-out types → Self-Critique | `prompts/templates.py` |
| `CONTENT_ANALYSIS_PROMPT` | Map selected queries to optimal content sections | `prompts/templates.py` |
| `CONTENT_GENERATION_PROMPT` | Write full paragraphs for each placement (with brand guidelines injection) | `prompts/templates.py` |
| `BRAND_EXTRACTION_PROMPT` | Extract structured brand voice profile from raw guidelines text | `prompts/templates.py` |
