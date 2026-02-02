# OriginChain (NewsTrace AI)

> **OriginChain** is a GenAI-powered multi-source news intelligence system that finds the **root origin of any news**, reconstructs a **timeline of events**, detects **contradictions**, and generates an evidence-grounded **impact analysis** on a chosen entity (company/person/sector/country).

---

## 🚀 What Problem Are We Solving?

News today spreads fast, mutates quickly, and often gets misreported or reshaped by narratives.

Most tools only **summarize** news.

✅ OriginChain instead:
- traces the **first credible trigger**
- reconstructs the **event chain**
- highlights contradictions across sources
- explains **impact causality** with confidence

---

## ✨ Key Features

### ✅ 1. Root Source Detection
- Identifies the earliest credible trigger (press release / govt order / first report / tweet)
- Gives **source link + why it's root + confidence score**

### ✅ 2. Timeline Reconstruction
Produces a structured timeline:
- timestamp → event summary → sources → confidence
Event tags:
- `initial_claim`
- `amplification`
- `official_response`
- `correction`
- `counter_claim`
- `consequence`

### ✅ 3. Contradiction Detection
Highlights conflicting reporting:
- “Source A says X, Source B says Y”

### ✅ 4. Impact Analysis Engine
For a chosen instance (e.g. Tesla, Bitcoin, India, IT sector), generates:
- direct impact
- second-order effects
- polarity (positive/negative/mixed)
- uncertainty notes

### ✅ 5. Case Management + UI
- Runs as a local demo product
- Save sessions (cases)
- Export report (JSON/PDF)

---

## 🧠 Why this is a GenAI Project?

OriginChain uses LLMs for:
- clustering articles into events (not just sorting by time)
- identifying the true root trigger (not just earliest article)
- extracting claims and detecting contradictions
- reasoning about causal impacts on a target entity

This is **retrieval + reasoning + generation** → proper GenAI pipeline.

---

## 🏗️ Architecture (Microservices)

The system is split into 4 independent microservices:

### 1️⃣ News Ingestion Service (Collector)
- Fetches articles using free sources (RSS/GDELT)
- Cleans and normalizes text
- Deduplicates sources
- Output: `articles.json`

### 2️⃣ Origin + Timeline Builder
- Clusters sources into timeline events
- Detects root origin
- Detects contradictions
- Output: `timeline.json`

### 3️⃣ Impact Analysis Engine
- Takes timeline + target instance
- Produces direct + indirect impact reasoning with confidence
- Output: `impact.json`

### 4️⃣ Case Manager + UI
- Streamlit/React based demo UI
- Integrates all modules
- Exports report

---

## 👥 Team Work Distribution

| Member | Role | Main Deliverable |
|--------|------|------------------|
| Sriyansh | Ingestion Service | `ingestor.py` → `articles.json` |
| Shivansh | Timeline Builder | `timeline_builder.py` → `timeline.json` |
| Anurag | Impact Engine | `impact_engine.py` → `impact.json` |
| Paras | UI + Integration | `app.py` (Streamlit) + report export |

---

## ✅ Build Order (Recommended)

1. **Ingestion (Sriyansh)** → produce `articles.json`
2. **Timeline Builder (Shivansh)** → `timeline.json`
3. **Impact Engine (Anurag)** → `impact.json`
4. **UI + Integration (Paras)** → final demo product

---

## 📁 Suggested Folder Structure

