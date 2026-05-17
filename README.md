# Vibe Search
---
title: Vibe Search
emoji: 🏠
colorFrom: red
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
license: mit
---

Visual similarity search for Airbnb listings using CLIP embeddings.

Upload a photo of a place you love — get back Airbnb listings with the same vibe.

![Demo screenshot — coming soon](docs/demo.png)

## How it works

1. Pre-computed CLIP embeddings for ~1,500 real Airbnb listings across Barcelona, Lisbon, and Amsterdam
2. User uploads a photo via the React frontend
3. FastAPI backend embeds the uploaded image with the same CLIP model
4. Cosine similarity finds the top 10 most visually similar listings
5. Results returned as JSON, rendered as a thumbnail grid

## Stack

- **Backend:** FastAPI + Uvicorn, Python 3.11
- **ML:** CLIP (ViT-B-32) via sentence-transformers
- **Data:** 1,439 listings from [Inside Airbnb](https://insideairbnb.com/)
- **Frontend:** React + Vite, plain CSS
- **Vector search:** Cosine similarity on NumPy arrays (no vector DB — at this scale, simple wins)

## Architecture decisions

- **No vector database.** 1,400 vectors is too small to justify Pinecone/pgvector. NumPy is microseconds.
- **Parameterized per-city architecture.** Each city has its own folder with embeddings + photos. Adding a new city is a folder + running 3 scripts, no code changes.
- **Bundled deployment.** Photos served by the FastAPI backend rather than a CDN — at 50MB total, the operational simplicity wins.

## Run locally

Backend:
\`\`\`
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn api:app --reload
\`\`\`

Frontend:
\`\`\`
cd frontend
npm install
npm run dev
\`\`\`

## Deployment

- Backend: Render
- Frontend: Vercel

[Live demo here] (to be added)
