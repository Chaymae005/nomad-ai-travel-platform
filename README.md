# Nomad: AI-Powered Travel Platform

A travel platform combining **personalized destination recommendations** with a **conversational agent** built on RAG and tool calling. Built during a 2-month internship at SQLI (EMSI, 2025–2026).

The architecture is deliberately generic: adapting it to another domain only requires changing the data and the tools.

![Home page](screenshots/home.png)

## Features

- **Destination pages**: practical info, live weather, images, best time to travel, popular cities
- **Browse by season and traveler profile** (family, couple, friends, solo)
- **Favorites**, map and route between two points, global search
- **Conversational travel assistant** available from any page
- **User accounts** with JWT authentication
- **Two recommendation systems**:
  - *Precomputed*: each destination scored by season and traveler profile
  - *Personalized*: content similarity between the user's favorites and the knowledge base (vector search, favorites excluded, best score kept per country, no LLM call at recommendation time)

![Country page](screenshots/country.png)

## How the agent works

1. The question and conversation history are sent to Gemini with the list of available tools.
2. Gemini decides whether tools are needed; the orchestrator runs them and returns the results.
3. The loop repeats until the model has enough information, then it writes the final answer.

| Tool | Purpose | Source |
|---|---|---|
| `get_weather` | Real-time weather | Open-Meteo |
| `get_country_info` | Capital, languages, currency, timezone | countries.dev |
| `search_rag` | Travel knowledge base | Wikivoyage (FR/EN) via Chroma |
| `get_wikipedia_summary` | General fallback | Wikipedia |

![Agent](screenshots/agent.png)

## Architecture

```
React (Vite)  ──►  FastAPI  ──►  Services (countries, cities, seasons, travelers, map, search)
                      │
                      ├──►  Agent orchestrator ──► Gemini + tools
                      └──►  Chroma vector store (RAG)  ◄──  Wikivoyage pipeline
```

**RAG pipeline** (`backend/pipeline/`, run once): Wikimedia API extraction → cleaning → chunking → embeddings → Chroma. Gemini is also used offline to generate country presentations, seasonal scores and traveler-profile tags (`backend/data/curated/`).

## Tech stack

Python · FastAPI · SQLAlchemy · Gemini (`google-genai`) · Chroma · React · Vite · Open-Meteo · OpenRouteService · Pexels

## Getting started

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # fill in your own API keys
```

The vector store is not included in the repository. The cleaned data is in `backend/data/processed/`, so to rebuild the vector store, run:

```bash
python -m pipeline.chunk_and_embed
```

Then start the API:

```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment variables

See `backend/.env.example` (Gemini keys, JWT secret, Pexels, OpenRouteService). Never commit your `.env`.

## Data and credits

- Destination content comes from **Wikivoyage** (CC BY-SA), retrieved through the Wikimedia API.
- Images come from **Pexels**.
- Live data: Open-Meteo, countries.dev, Wikipedia, OpenRouteService.
- The user database and generated usage histories are not included.

## Limitations and next steps

- The knowledge base covers 35 countries
- Recommendations rely on content similarity only; other signals (popularity, user behavior) could be added
- No quantitative evaluation of the agent's answer quality yet (retrieval relevance, answer faithfulness)

## Author

Chaymae Yassine, AI & Data Engineering student at EMSI Rabat · 
