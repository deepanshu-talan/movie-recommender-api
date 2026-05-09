# MovieRS — AI-Powered Movie Recommendation System

A production-grade movie recommendation web application using **TMDB API**, **TF-IDF + Cosine Similarity** for content-based filtering, and a modern **React** frontend.

## Architecture

```
User → React (Vite) → Flask API → ML Engine → Response
                         ↓
                    Redis (Hot Cache)
                         ↓
                    SQLite DB (Persistent Store)
                         ↓
                     TMDB API (External)
                         ↓
                    Save → SQLite + Redis

        Background Scheduler (APScheduler)
        - Pre-warms trending/popular (every 6h)
        - Refreshes genres (daily)
```

**Data Flow:** Request → Redis → SQLite (check staleness) → TMDB API → save to DB + Redis

Every response includes a `source` field: `redis`, `database`, `tmdb_api`, `database_stale`, or `fallback`.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS v4, React Router v6, Axios |
| Backend | Python, Flask, Gunicorn |
| ML | Scikit-learn (TF-IDF), Cosine Similarity, Joblib |
| Database | SQLite (persistent store, FTS5 full-text search) |
| Cache | Redis (hot cache, TTL-based) |
| Background Jobs | APScheduler (pre-warming, staleness refresh) |
| Data Source | TMDB API v3 |
| Infrastructure | Docker, Docker Compose |

### Per-Category Staleness

| Category | Stale After | Reason |
|----------|-------------|--------|
| Trending | 6 hours | Changes frequently |
| Popular | 12 hours | Shifts slowly |
| High Rated | 7 days | Very stable |
| Movie Details | 7 days | Metadata rarely changes |
| Genres | 30 days | Almost never changes |

## Quick Start

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env and add your TMDB_ACCESS_TOKEN
```

### 2. Backend setup

```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Build ML model (first time)

```bash
python scripts/fetch_tmdb_data.py --count 500  # Start small
python scripts/train_model.py
```

### 4. Start backend

```bash
python app/main.py
# Server runs at http://localhost:5000
```

### 5. Frontend setup

```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:5173
```

### Docker (alternative)

```bash
cd docker
docker-compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/search?q=X&page=N` | Search movies |
| GET | `/api/v1/movie/{id}` | Movie details |
| GET | `/api/v1/recommend?movie_id={id}` | ML recommendations |
| GET | `/api/v1/trending` | Trending movies |
| GET | `/api/v1/popular?page=N` | Popular movies |
| GET | `/api/v1/genres` | Genre list |
| GET | `/api/v1/health` | Health check |

## Project Structure

```
├── app/                  # Flask backend
│   ├── api/routes/       # API endpoints
│   ├── core/             # Config, logging, security
│   ├── db/               # SQLite database + Redis client
│   │   ├── movie_db.py   # Persistent movie store (FTS5)
│   │   └── redis_client.py
│   ├── ml/               # ML pipeline
│   └── services/         # TMDB + cache + recommendation
│       ├── scheduler.py  # APScheduler background jobs
│       └── ...
├── frontend/             # React (Vite) app
│   └── src/
│       ├── components/   # Reusable UI components
│       ├── pages/        # Route pages
│       ├── services/     # API client
│       └── hooks/        # Custom React hooks
├── scripts/              # Data fetching + model training
├── data/                 # ML artifacts + datasets + movies.db
└── docker/               # Docker configuration
```

## License

MIT
