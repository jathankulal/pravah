# PRAVAH — Causal Risk Intelligence Engine MVP

Build a desktop-first (1440×900) dark enterprise intelligence dashboard using **Streamlit + Python + FastAPI** that processes safety reports through the causal chain: **Activity → Hazardous Energy → Barrier Failure → Potential Consequence**, and surfaces SIF potential, Life-Saving Rule mapping, and recurring precursor patterns.

---

## Proposed Changes

### Phase 1: Project Foundation & Data Layer

#### [NEW] [requirements.txt](file:///d:/pravah/requirements.txt)
Pin all locked dependencies:
- `streamlit`, `fastapi`, `pydantic`, `uvicorn`
- `spacy`, `transformers`, `sentence-transformers`, `scikit-learn`
- `plotly` (for interactive charts)
- `torch` (HF runtime dependency)
- `python-dotenv`

#### [NEW] [.env.example](file:///d:/pravah/.env.example)
Template for environment variables (no secrets committed).

#### [NEW] [.streamlit/config.toml](file:///d:/pravah/.streamlit/config.toml)
Dark theme configuration:
- `primaryColor = "#7C6CFF"` (PRAVAH accent)
- `backgroundColor = "#0B1020"` (app background)
- `secondaryBackgroundColor = "#121826"` (card background)
- `textColor = "#F4F6FB"`

---

### Phase 2: Data & Knowledge Layer

#### [NEW] [data/rules/life_saving_rules.json](file:///d:/pravah/data/rules/life_saving_rules.json)
IOGP Life-Saving Rules reference data (9 rules: Confined Space, Driving, Energy Isolation, Hot Work, Line of Fire, Safe Mechanical Lifting, Work at Height, Working with Chemicals, Bypassing Safety Controls). Each rule with: id, name, description, hazard keywords, barrier keywords.

#### [NEW] [data/taxonomy/dekra_eei.json](file:///d:/pravah/data/taxonomy/dekra_eei.json)
DEKRA/EEI safety taxonomy: hazardous energy types (kinetic, chemical, electrical, thermal, gravitational, pressure, radiation), barrier categories, consequence severity levels.

#### [NEW] [data/sample_reports/reports.json](file:///d:/pravah/data/sample_reports/reports.json)
15-20 realistic sample oil & gas UA/UC/near-miss/incident reports. Each report with: id, site, date, type, severity, free-text description. Reports will include deliberately varied wording for the same failure modes to demonstrate semantic matching.

---

### Phase 3: Database Layer

#### [NEW] [db/models.py](file:///d:/pravah/db/models.py)
Pydantic models for:
- `SafetyReport` — raw report with metadata
- `CausalAnalysis` — extracted Activity, Hazardous Energy, Barrier Failure, Potential Consequence + confidence scores
- `SIFAssessment` — SIF potential flag + evidence
- `LSRMapping` — matched Life-Saving Rule + relevance score
- `PrecursorPattern` — recurring pattern cluster
- `ExpertReview` — human feedback record

#### [NEW] [db/database.py](file:///d:/pravah/db/database.py)
SQLite database manager:
- Table creation for reports, analyses, reviews
- CRUD operations
- Seed function to load sample reports
- Query functions for dashboard aggregations

---

### Phase 4: Core Causal Engine

#### [NEW] [core/causal_engine.py](file:///d:/pravah/core/causal_engine.py)
Central causal reconstruction engine:
- Takes NLP-extracted entities and maps them to the 4-node chain
- Deterministic rules for causal chain validation
- Confidence scoring per node
- Single shared engine instance (cached)

#### [NEW] [core/sif_logic.py](file:///d:/pravah/core/sif_logic.py)
SIF Potential detection:
- Deterministic scoring based on hazardous energy type + barrier failure severity + potential consequence
- Thresholds: Low / Medium / High / Critical
- Evidence generation explaining why SIF was flagged

#### [NEW] [core/lsr_logic.py](file:///d:/pravah/core/lsr_logic.py)
Life-Saving Rule mapping:
- Match hazards/barriers against IOGP LSR keyword sets
- Return matched rule with relevance score and evidence
- Support multiple LSR matches per report

#### [NEW] [core/precursor_engine.py](file:///d:/pravah/core/precursor_engine.py)
Recurring precursor detection:
- Cluster reports by semantic similarity of barrier failures
- Track frequency and recency of similar failure modes
- Surface emerging and recurring patterns
- Uses Sentence-Transformers embeddings + scikit-learn clustering

#### [NEW] [core/scoring.py](file:///d:/pravah/core/scoring.py)
Centralized scoring and thresholds:
- Overall risk score computation
- Exposure-weighted SIF density
- Confidence calibration
- Centralized threshold constants

---

### Phase 5: NLP Pipeline

#### [NEW] [nlp/preprocessing.py](file:///d:/pravah/nlp/preprocessing.py)
Text preprocessing using spaCy:
- Tokenization, lemmatization
- Stop-word removal
- Domain-specific term normalization (oil & gas safety vocabulary)

#### [NEW] [nlp/extraction.py](file:///d:/pravah/nlp/extraction.py)
Safety concept extraction:
- Activity identification (what was being done)
- Hazardous energy detection (what energy source was involved)
- Barrier failure identification (what control failed or was absent)
- Consequence extraction (what happened or could have happened)
- Uses spaCy NER + keyword matching + transformer-based classification

#### [NEW] [nlp/embeddings.py](file:///d:/pravah/nlp/embeddings.py)
Semantic embeddings manager:
- Load and cache Sentence-Transformers model (`all-MiniLM-L6-v2`)
- Generate report embeddings
- Store and retrieve embeddings for similarity operations

#### [NEW] [nlp/similarity.py](file:///d:/pravah/nlp/similarity.py)
Semantic similarity operations:
- Cosine similarity between report embeddings
- Find similar reports
- Support failure-mode matching across differently-worded reports

---

### Phase 6: Reusable UI Components

#### [NEW] [components/cards.py](file:///d:/pravah/components/cards.py)
Streamlit components with custom CSS:
- `kpi_card(title, value, trend, color)` — top-row metric cards
- `risk_score_gauge(score)` — semicircular gauge for Overall Risk Score
- `ai_insight_card(finding, severity, evidence_count)` — AI Risk Brief items
- All cards follow the dark design: `#121826` background, `#2B3242` border, 14px radius

#### [NEW] [components/causal_chain.py](file:///d:/pravah/components/causal_chain.py)
Horizontal causal chain visualization:
- 4 connected nodes: Activity → Hazardous Energy → Barrier Failure → Consequence
- Color-coded: default → cyan → amber → red (for severe)
- Shows extracted phrase, confidence per node
- SIF badge + LSR badge below the chain
- Rendered as styled HTML/CSS within Streamlit

#### [NEW] [components/badges.py](file:///d:/pravah/components/badges.py)
Status and severity badges:
- SIF level pills (Low/Medium/High/Critical)
- Review status badges (Pending/Confirmed/Corrected)
- LSR rule badges
- Confidence progress bars

#### [NEW] [components/tables.py](file:///d:/pravah/components/tables.py)
Styled report tables:
- Priority reports table with dark rows, compact 48px height
- Sortable columns with severity badges
- Search and filter integration
- Click-to-select row behavior

#### [NEW] [components/charts.py](file:///d:/pravah/components/charts.py)
Chart components using Plotly:
- Risk trend line/area chart with time period tabs
- Hotspot heatmap / risk matrix
- Precursor frequency chart
- All charts use the PRAVAH dark color palette

---

### Phase 7: Streamlit Pages

#### [NEW] [app.py](file:///d:/pravah/app.py)
Main Streamlit application entry point:
- Page configuration (wide layout, dark theme, page icon)
- Sidebar navigation with PRAVAH branding
- Route to appropriate page
- Database initialization on first run
- Model caching setup

#### [NEW] [pages/1_📊_Overview.py](file:///d:/pravah/pages/1_📊_Overview.py)
**Overview Dashboard** — the primary hackathon demo screen:
- **Row 1**: 4 KPI cards (SIF Potential count, High-Risk Reports, Recurring Precursors, Overall Risk Score gauge)
- **Row 2**: Risk Trend chart (left 65%) + AI Risk Brief (right 35%)
- **Row 3**: Featured Causal Chain visualization (PRAVAH differentiator)
- **Row 4**: Priority Reports table (full-width, 6-8 rows)

#### [NEW] [pages/2_📋_Reports.py](file:///d:/pravah/pages/2_📋_Reports.py)
**Reports Page** — high-density report management:
- Full-width filter bar (site, type, SIF level, LSR, review state, date)
- Full-width report table
- Click to navigate to detail view
- Report ingestion form (submit new UA/UC/near-miss/incident text)

#### [NEW] [pages/3_🔍_Causal_Analysis.py](file:///d:/pravah/pages/3_🔍_Causal_Analysis.py)
**Causal Analysis / Report Detail** — 60/40 split layout:
- **Left 60%**: Original report text, metadata, highlighted extracted phrases, evidence markers, related reports
- **Right 40%**: AI Causal Analysis — Activity, Hazardous Energy, Barrier Failure, Consequence, SIF Potential, LSR, Confidence, Confirm/Correct buttons

#### [NEW] [pages/4_🔄_Precursors.py](file:///d:/pravah/pages/4_🔄_Precursors.py)
**Recurring Precursors Page**:
- Top KPI row: total active patterns, newly emerging, sites affected
- Left: ranked recurring precursor pattern cards
- Right: selected pattern summary + causal explanation
- Bottom: linked reports table

#### [NEW] [pages/5_🗺️_Hotspots.py](file:///d:/pravah/pages/5_🗺️_Hotspots.py)
**Hotspots Page**:
- Top controls: site + time period + activity filters
- Main: risk matrix visualization
- Side panel: top hotspot list with SIF density, report count, dominant barrier failure
- Bottom: hotspot trend chart
- Separate display for raw report volume vs. SIF density

#### [NEW] [pages/6_✅_Expert_Review.py](file:///d:/pravah/pages/6_✅_Expert_Review.py)
**Expert Review Page**:
- Left: pending review queue
- Center/right: selected report's causal analysis
- Sticky actions: Confirm, Correct, Escalate, Add Note
- Correction edits individual causal nodes
- Success toast + auto-advance to next pending item

---

### Phase 8: Backend API (Optional Layer)

#### [NEW] [backend/api.py](file:///d:/pravah/backend/api.py)
FastAPI REST endpoints:
- `POST /api/reports` — submit a new safety report
- `GET /api/reports` — list reports with filters
- `GET /api/reports/{id}` — get report with causal analysis
- `GET /api/overview/stats` — dashboard KPIs
- `POST /api/reports/{id}/review` — submit expert feedback
- `GET /api/precursors` — recurring patterns
- `GET /api/hotspots` — risk hotspots

#### [NEW] [backend/schemas.py](file:///d:/pravah/backend/schemas.py)
Pydantic request/response schemas for all API endpoints.

---

### Phase 9: Utilities & Config

#### [NEW] [utils/config.py](file:///d:/pravah/utils/config.py)
Centralized configuration:
- Color tokens (matching design doc)
- Thresholds for SIF/LSR/scoring
- Model names and paths
- Database path

#### [NEW] [utils/helpers.py](file:///d:/pravah/utils/helpers.py)
Utility functions: date formatting, text truncation, session state helpers.

#### [NEW] [README.md](file:///d:/pravah/README.md)
Project documentation with setup instructions, architecture overview, and demo guide.

---

## Implementation Strategy

> [!IMPORTANT]
> **Build order matters.** The approach is bottom-up: data → core engine → NLP → components → pages. This ensures each page consumes fully-working structured data from the shared causal engine, rather than reimplementing logic per page.

### Build Sequence

| Step | What | Files | Est. Complexity |
|------|------|-------|-----------------|
| 1 | Project setup + deps + theme | `requirements.txt`, `.streamlit/config.toml`, `.env.example` | Low |
| 2 | Data files + DB layer | `data/`, `db/` | Medium |
| 3 | Core causal engine + scoring | `core/` (5 files) | High |
| 4 | NLP pipeline | `nlp/` (4 files) | High |
| 5 | UI components | `components/` (5 files) | Medium |
| 6 | App shell + Overview page | `app.py`, `pages/1_Overview.py` | Medium |
| 7 | Reports + Causal Analysis pages | `pages/2_Reports.py`, `pages/3_Causal_Analysis.py` | Medium |
| 8 | Precursors + Hotspots pages | `pages/4_Precursors.py`, `pages/5_Hotspots.py` | Medium |
| 9 | Expert Review page | `pages/6_Expert_Review.py` | Medium |
| 10 | Backend API | `backend/` | Low-Medium |
| 11 | Polish + README | Final pass | Low |

---

## Open Questions

> [!IMPORTANT]
> **NLP Model Strategy**: The NLP pipeline requires downloading transformer models (e.g., `all-MiniLM-L6-v2` ~80MB, spaCy `en_core_web_sm` ~12MB). For the hackathon MVP, I will use **lightweight models** that work offline after first download. Should I:
> - Use **rule-based extraction** (faster, no model downloads, simpler) for the causal chain, with sentence-transformers only for semantic similarity?
> - Use **full transformer pipeline** (more accurate but heavier, slower first load)?
> 
> **My recommendation**: Start with a **hybrid approach** — rule-based keyword extraction for causal chain nodes + sentence-transformers for similarity/clustering. This keeps the demo fast while still showcasing AI capabilities.

> [!NOTE]
> **Sample Data**: I will create 15-20 realistic oil & gas safety reports covering scenarios like confined space entry, hot work violations, fall hazards, chemical exposure, energy isolation failures, etc. These will include deliberately similar reports worded differently to demonstrate PRAVAH's semantic matching capability.

> [!NOTE]
> **Python version**: Your system has Python 3.14. I'll ensure all dependencies are compatible. If any locked dependency doesn't support 3.14 yet, I'll flag it and we can use a virtual environment with a compatible version.

---

## Verification Plan

### Automated Tests
```bash
# Run the Streamlit app
streamlit run app.py

# Run the FastAPI backend (separate terminal)
uvicorn backend.api:app --reload
```

### Manual Verification
- Launch the app and verify all 6 pages render correctly
- Verify the dark theme matches the design specification
- Submit a new report and confirm causal chain generation
- Check that similar reports are semantically connected
- Verify SIF and LSR flags appear with evidence
- Test expert review confirm/correct workflow
- Verify responsive behavior at 1280px minimum width

### Hackathon Demo Route
1. Open Overview Dashboard → KPIs visible
2. Select highest-priority report from table
3. View 60/40 Causal Analysis detail
4. Show Activity → Hazardous Energy → Barrier Failure → Consequence chain
5. Show mapped Life-Saving Rule with evidence
6. Navigate to Precursors → demonstrate cross-report pattern
7. Expert Review → confirm/correct AI output
