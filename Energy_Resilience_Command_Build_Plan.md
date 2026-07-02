# Energy Resilience Command — Full Build Plan
**ET AI Hackathon 2026 | Submission Deadline: July 20, 2026 | Budget: ₹0 (100% free-tier)**

---

## 1. What You're Actually Building (MVP Scope)

Six agents, one working end-to-end flow, one demo. Everything below is scoped to be buildable by a small team in ~18 days of evenings/weekends, using only free tools.

| # | Agent | Job | MVP Version |
|---|-------|-----|--------------|
| 1 | **Watchtower** | Risk signal detection | 3 news sources + LLM extraction → disruption probability score |
| 2 | **Crystal Ball** | Scenario simulation | 3 pre-built scenarios (Hormuz 50%, Red Sea, OPEC+ cut), simple math model, not full Monte Carlo |
| 3 | **Deal Maker** | Procurement recommendation | Matches 3 crude grades to 3 refineries, generates 1 ranked recommendation |
| 4 | **Vault Keeper** | SPR drawdown advice | Simple optimization formula (not full portfolio model) |
| 5 | **Commander** | Conflict resolution | Weighted scoring matrix that arbitrates when agents disagree |
| 6 | **Mirror** | Digital twin | 2D Mapbox map (NOT Three.js/WebGL — too risky for a live demo), 3 refineries, 5 routes, drag-to-disrupt interaction |

**Cut entirely for the hackathon (mention only as "Phase 2" on a roadmap slide):**
- Real-time AIS streaming, Kafka/Airflow pipelines, blockchain hash chaining, Three.js 3D twin, Neo4j graph DB, full production security/auth.

---

## 2. The Commander Agent — Conflict Resolution (Your #1 Fix)

This is the piece the earlier review flagged as a fatal gap. Here's exactly how to build it.

### 2.1 The Problem It Solves
Watchtower says "Hormuz risk is only 30%, don't panic." Deal Maker says "buy from Brazil now." Vault Keeper says "draw down SPR instead." Someone has to arbitrate.

### 2.2 Design: Weighted Scoring Matrix

Each downstream agent (Deal Maker, Vault Keeper) submits a **recommendation object**, not a final decision:

```json
{
  "agent": "deal_maker",
  "action": "buy_brazil_crude",
  "confidence": 0.78,
  "urgency": 0.65,
  "cost_score": 0.55,     // lower cost = higher score
  "risk_score": 0.70,     // lower risk = higher score
  "strategic_priority": 0.60
}
```

The Commander computes a weighted composite score per candidate action:

```
Composite = (0.30 × urgency) + (0.25 × risk_score) + (0.20 × cost_score)
          + (0.15 × strategic_priority) + (0.10 × confidence)
```

Weights are configurable (put them in a JSON config file so judges can see you thought about tunability — this itself is a talking point).

### 2.3 Resolution Logic (pseudocode)

```python
def commander_resolve(recommendations, watchtower_risk_score):
    scored = []
    for rec in recommendations:
        composite = (
            0.30 * rec["urgency"] +
            0.25 * rec["risk_score"] +
            0.20 * rec["cost_score"] +
            0.15 * rec["strategic_priority"] +
            0.10 * rec["confidence"]
        )
        scored.append({**rec, "composite_score": composite})

    scored.sort(key=lambda r: r["composite_score"], reverse=True)
    top = scored[0]
    second = scored[1] if len(scored) > 1 else None

    # Hybrid logic: if two actions are close in score, blend them
    if second and (top["composite_score"] - second["composite_score"]) < 0.08:
        return {
            "decision": "hybrid",
            "primary": top["action"],
            "secondary": second["action"],
            "explanation": f"{top['action']} scored {top['composite_score']:.2f}, "
                            f"{second['action']} scored {second['composite_score']:.2f} — "
                            f"close enough to combine. Recommend {top['action']} first, "
                            f"fall back to {second['action']} if unavailable."
        }
    return {
        "decision": "single",
        "primary": top["action"],
        "explanation": f"{top['action']} wins with composite score {top['composite_score']:.2f} "
                        f"vs next-best {second['composite_score']:.2f}."
    }
```

### 2.4 The Demo-Ready Example
This is the exact line to say to judges:

> "Deal Maker scored the Brazil purchase at 78/100. Vault Keeper scored SPR drawdown at 65/100. The Commander doesn't just pick a winner — it recommends a hybrid: draw SPR for 7 days to cover the immediate gap, then switch to Brazilian crude once it lands on day 8. Human policymakers retain final veto power — the Commander produces a recommendation, not an autonomous action."

**Always end conflict-resolution explanations with "human retains veto power."** Judges in a national-energy-security context will specifically probe whether you're proposing full autonomy over strategic reserves — you want an explicit human-in-the-loop answer ready.

---

## 3. Full Tech Stack — 100% Free Tier

| Layer | Original (paid/complex) | **Free Replacement** | Why |
|---|---|---|---|
| LLM | GPT-4o / Claude 3.5 (paid API) | **Groq API (free tier, Llama 3.1/3.3)** or **Google Gemini 1.5 Flash (free tier)** or **Claude free-tier via console credits** | Groq is extremely fast and has a generous free tier — good for live demos where latency matters |
| Data ingestion | Kafka + Airflow | **Python `schedule` / cron + simple polling scripts** | Kafka/Airflow are massive overkill and hard to demo live; a scheduled Python job hitting free APIs every N minutes does the same job for a hackathon |
| Multi-agent orchestration | LangGraph / CrewAI | **LangGraph (free, open-source)** — keep this, it's free and genuinely useful | No paid dependency here |
| Knowledge graph | Neo4j (paid at scale) | **Neo4j AuraDB Free tier** (1 free instance) or just a **Python dict / SQLite** for MVP | AuraDB free tier is enough for hackathon scale; SQLite is the zero-risk fallback |
| Scenario/simulation | PyMC + Prophet + Monte Carlo | **NumPy + simple weighted formulas**, optionally `scipy.stats` for a lightweight Monte Carlo (1,000 iterations, runs in <1s) | Full Bayesian modeling (PyMC) is unnecessary risk; a transparent formula is *more* demo-friendly because you can show the math on screen |
| Maps / geospatial | PostGIS + Mapbox GL + Three.js/WebGL | **Mapbox GL JS (free tier: 50,000 loads/month)** or **Leaflet.js (fully free, no API key)** | Drop Three.js entirely — 2D map with animated markers is faster to build and won't crash during demo |
| Backend | FastAPI + PostgreSQL | **FastAPI + SQLite** (upgrade to free Supabase Postgres if you want hosted persistence) | SQLite needs zero setup; Supabase free tier (500MB) if you want a real hosted DB |
| Frontend | React + Three.js + WebGL | **React + Leaflet + Recharts** (or plain HTML/CSS/JS if team isn't strong in React) | Simpler stack = fewer failure points |
| Hosting (backend) | — | **Render.com free tier** or **Railway free tier** or run locally for demo | Free tier can sleep after inactivity — for a live demo, run locally + have a hosted backup link |
| Hosting (frontend) | — | **Vercel (free)** or **Netlify (free)** | Both have generous free tiers, deploy from GitHub in one click |
| News/data sources | Reuters/Bloomberg (paid) | **NewsAPI.org free tier (100 req/day)**, **GDELT Project (100% free, no key)**, **RSS feeds from Reuters/Al Jazeera/Gulf News** | GDELT is the best-kept secret here — free, real-time global news event database, built for exactly this kind of geopolitical risk signal |
| Shipping/AIS data | Commercial AIS feeds | **MarineTraffic free tier (very limited)** → for MVP, **use mocked/historical vessel data** (defensible: say "production would use Kpler/Vortexa") | Don't burn hackathon time fighting AIS rate limits |
| Oil price data | Bloomberg terminal | **EIA API (100% free, official US gov data)**, **Alpha Vantage free tier** for Brent/WTI | EIA is authoritative and free — use this, cite it explicitly to judges |
| Sanctions data | — | **OFAC SDN list (free, public, downloadable CSV)** | Real, free, and instantly credible |
| Version control / repo | — | **GitHub (free)** | Required deliverable anyway |
| Design/diagrams | — | **Excalidraw (free)** or **draw.io (free)** | For the architecture diagram |
| Pitch deck | — | **Google Slides (free)** or **Canva free tier** | — |
| Video backup | — | **OBS Studio (free, open source)** screen recorder | Record your working demo as insurance against live-demo failure |

**Total cost: ₹0.** Every single component above has a genuinely free tier sufficient for a hackathon build and live demo.

---

## 4. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES (free)                        │
│  GDELT | NewsAPI | EIA API | OFAC SDN List | Mock AIS data          │
└───────────────────────────────┬───────────────────────────────────┘
                                 │  (Python polling script, every 5 min)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AGENT 1: WATCHTOWER                             │
│  LLM (Groq/Gemini) extracts risk signals from headlines             │
│  → Outputs: {corridor: "Hormuz", disruption_probability: 0.73}      │
└───────────────────────────────┬───────────────────────────────────┘
                                 │  triggers if probability > threshold
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AGENT 2: CRYSTAL BALL                           │
│  Applies scenario formula → cascading impact estimate               │
│  → Outputs: refinery run-rate drop %, price impact, city risk list  │
└───────────────────────────────┬───────────────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
┌────────────────────────────┐   ┌────────────────────────────┐
│  AGENT 3: DEAL MAKER        │   │  AGENT 4: VAULT KEEPER      │
│  Ranks alternative crude    │   │  Models SPR drawdown        │
│  sources vs refinery match  │   │  schedule                   │
│  → recommendation object    │   │  → recommendation object    │
└──────────────┬───────────────┘   └──────────────┬──────────────┘
               │                                   │
               └───────────────┬───────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AGENT 5: COMMANDER                               │
│  Weighted scoring matrix arbitrates conflicting recommendations      │
│  → Final decision: single action OR hybrid plan                      │
│  → Human-in-the-loop veto checkpoint                                 │
└───────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AGENT 6: MIRROR (Digital Twin)                   │
│  React + Leaflet map: refineries, routes, disruption zones           │
│  Drag disruption zone → calls backend → agents re-run → map updates  │
└─────────────────────────────────────────────────────────────────────┘

              Backend: FastAPI (orchestrates LangGraph agent graph)
              Storage: SQLite (or Supabase free Postgres)
```

---

## 5. Day-by-Day Build Plan (July 2 → July 20)

Assuming a team of 3–4 people working evenings/weekends. Adjust ratios to your team size.

| Dates | Phase | Deliverable |
|---|---|---|
| **Jul 2–3** | Setup | GitHub repo scaffolded, all free API keys registered (Groq, EIA, NewsAPI, Mapbox), team roles assigned |
| **Jul 4–6** | Agent 1 + data pipeline | Watchtower working: pulls GDELT + NewsAPI headlines, LLM extracts risk signal, outputs disruption probability for Hormuz/Red Sea/US Gulf |
| **Jul 7–9** | Agent 2 + 3 | Crystal Ball scenario formulas built and tested against 2025 US-Iran and 2021 Suez historical data; Deal Maker crude-refinery matching logic + recommendation JSON |
| **Jul 10–11** | Agent 4 | Vault Keeper SPR drawdown formula |
| **Jul 12–13** | Agent 5 (Commander) | Weighted scoring matrix, hybrid decision logic, test with conflicting mock inputs |
| **Jul 14–16** | Agent 6 (Mirror) + integration | React/Leaflet map, 3 refineries + 5 routes plotted, drag-to-disrupt triggers full agent pipeline via FastAPI |
| **Jul 17** | End-to-end test | Full flow: headline → risk score → scenario → recommendation → Commander decision → map update. Run 10+ times, fix breakages |
| **Jul 18** | Demo polish | Build "DEMO MODE" with pre-loaded data (no live API calls during the actual demo — eliminates network failure risk), record OBS video backup |
| **Jul 19** | Deck + docs | Finish pitch deck, architecture diagram, README, rehearse demo 15–20 times |
| **Jul 20** | Submit | Submit repo + deck + demo video before deadline; buffer hours for last-minute upload issues |

---

## 6. Real Data Integration (Optional, as Requested)

Since you said real data is optional for now, here's the minimum-effort way to add credibility without extra engineering risk:

1. **Historical backtesting only** — pull real Brent price data around the 2025 US-Iran standoff from the **EIA API** (free), and real 2021 Suez blockage shipping delay figures from public reporting. Use these to validate your Crystal Ball formulas ("our model predicts a price move within 12% of the actual 2025 spike").
2. **Static real reference data** — hardcode real Indian refinery configurations (Reliance Jamnagar, IOC Panipat, BPCL Kochi — API gravity and sulfur tolerance are publicly published in refinery spec sheets) instead of live feeds. This is "real data" without needing a live pipeline.
3. **Live only for Watchtower** — this is the one agent worth making genuinely live, since GDELT and NewsAPI are free, low-effort, and it's the most demo-impressive part ("this is a real headline from this morning").

Everything else (AIS ship positions, satellite imagery) — mock it and say so openly. Judges respect honesty about what's mocked vs. real far more than they respect fake precision.

---

## 7. Judge Q&A Prep (Updated with Commander Answer)

| Question | Your Answer |
|---|---|
| How do the agents resolve conflicts? | "The Commander Agent scores every recommendation on urgency, risk, cost, strategic priority, and confidence using a weighted matrix. If two options are close, it proposes a hybrid plan. Human policymakers retain final veto power — this is decision support, not autonomous execution." |
| How do you handle LLM hallucination? | "RAG with source attribution — every signal links to its source article. We cross-validate across 3+ sources before elevating confidence." |
| Where's your real-time AIS data? | "For the hackathon we use historical/mocked vessel data; production would integrate Kpler or Vortexa commercial feeds." |
| How did you validate the scenario model? | "Backtested against the 2025 US-Iran standoff and 2021 Suez blockage using free EIA price data — our model landed within [X]% of the actual price movement." |
| What's your moat? | "Refinery-grade compatibility knowledge, the Commander's arbitration logic, and eventual data network effects as more agencies plug in." |

---

## 8. Repo Structure

```
energy-resilience-command/
├── README.md
├── docker-compose.yml          # optional, one-command local run
├── requirements.txt
├── /docs/
│   ├── architecture.md
│   ├── commander-logic.md
│   └── demo-script.md
├── /agents/
│   ├── watchtower.py
│   ├── crystal_ball.py
│   ├── deal_maker.py
│   ├── vault_keeper.py
│   └── commander.py
├── /backend/
│   ├── main.py                 # FastAPI app
│   └── db.py                   # SQLite/Supabase connection
├── /frontend/
│   ├── src/
│   │   └── components/DigitalTwin.jsx
├── /data/
│   ├── refinery_specs.json     # real refinery data
│   └── historical_backtests/
└── /demo/
    ├── demo_mode_data.json
    └── backup_video.mp4
```

---

## 9. The One Rule That Matters Most

Build **one** working end-to-end flow before touching anything else:

> Headline → risk score → scenario trigger → two competing recommendations → Commander resolves → map updates.

Get that loop solid and rehearsed first. Everything else in this plan is enhancement on top of that spine — if you run out of time, cut features, never cut the spine.
