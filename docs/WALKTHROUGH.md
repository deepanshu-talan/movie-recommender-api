# Complete Project Walkthrough ΓÇö MovieRS

> A step-by-step guide explaining every decision, every component, and every error faced while building this production-grade Movie Recommendation System ΓÇö from scratch to AWS deployment.

---

## 1. Project Overview

### What Problem Does This Solve?

Users are overwhelmed with thousands of movies. Netflix, Amazon, and Hotstar solve this with recommendation engines that surface relevant content. This project builds the same system from scratch:

- **Input**: A user searches or browses movies
- **Output**: Personalized recommendations based on content similarity

### Why Content-Based Filtering (Not Collaborative)?

| Approach | How It Works | Limitation |
|----------|-------------|------------|
| **Collaborative** | "Users who liked X also liked Y" | Needs massive user history data (cold-start problem) |
| **Content-Based** | "Movie X has similar genres/overview to Y" | Limited to metadata similarity |

I chose content-based because:
1. **No user data needed** ΓÇö works from day one
2. **Explainable** ΓÇö I can say "recommended because both are sci-fi thrillers"
3. **No cold-start** ΓÇö new movies can be recommended immediately if they have metadata

### Limitations
- Cannot capture personal taste (user who loves "bad" horror movies won't get them)
- No social signal ("your friends watched this")
- Limited to metadata quality ΓÇö if TMDB overview is vague, similarity suffers

---

## 2. System Architecture

```
ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ     ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ
Γöé   Browser    ΓöéΓöÇΓöÇΓöÇΓöÇΓû╢Γöé  Nginx (Reverse Proxy + SPA Server)  Γöé
Γöé              ΓöéΓùÇΓöÇΓöÇΓöÇΓöÇΓöé  frontend container, port 80          Γöé
ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ     ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓö¼ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ
                                    Γöé /api/* requests
                                    Γû╝
                     ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ
                     Γöé  Flask + Gunicorn (Backend API)       Γöé
                     Γöé  backend container, port 5000         Γöé
                     Γöé                                       Γöé
                     Γöé  ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ  ΓöîΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÉ           Γöé
                     Γöé  Γöé Redis   Γöé  Γöé SQLite   Γöé           Γöé
                     Γöé  Γöé (cache) Γöé  Γöé (persist)Γöé           Γöé
                     Γöé  ΓööΓöÇΓöÇΓöÇΓöÇΓö¼ΓöÇΓöÇΓöÇΓöÇΓöÿ  ΓööΓöÇΓöÇΓöÇΓöÇΓö¼ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ           Γöé
                     Γöé       Γöé            Γöé                  Γöé
                     Γöé       ΓööΓöÇΓöÇΓöÇΓöÇ miss ΓöÇΓöÇΓöÿ                  Γöé
                     Γöé              Γöé                        Γöé
                     Γöé              Γû╝                        Γöé
                     Γöé        TMDB API (external)            Γöé
                     Γöé              Γöé                        Γöé
                     Γöé              Γû╝                        Γöé
                     Γöé     ML Engine (TF-IDF + Cosine)       Γöé
                     ΓööΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÿ
```

### What Happens At Each Stage

| Stage | Input | Output | Why Needed |
|-------|-------|--------|-----------|
| **Nginx** | HTTP request | Route to API or serve HTML | Single entry point, port 80 |
| **Flask Route** | API path + params | Structured JSON | Request handling + validation |
| **Redis Check** | Cache key | Hit: cached JSON / Miss: null | Sub-millisecond response for hot data |
| **SQLite Check** | SQL query | Fresh data or stale data | Persistent store survives restarts |
| **TMDB API** | HTTP request | Movie metadata JSON | Real-time source of truth |
| **ML Engine** | Movie ID | Top-N similar movie IDs | Content similarity computation |
| **APScheduler** | Cron trigger | Pre-warmed DB data | Eliminates cold-start latency |

---

## 3. Dataset Understanding

Data comes from **TMDB API v3** (The Movie Database), not a static CSV.

### Key Fields Used

| Field | Example | Why It Matters |
|-------|---------|---------------|
| `title` | "Inception" | Display + search |
| `overview` | "A thief who steals corporate secrets..." | **Primary ML feature** ΓÇö most text for similarity |
| `genre_ids` | [28, 12, 878] | Category matching |
| `vote_average` | 8.4 | Quality ranking |
| `release_date` | "2010-07-16" | Recency filtering |
| `poster_path` | "/9gk7adHYeDv..." | UI display |

### Why These Features

The `overview` field is the richest text source. Genres help cluster similar movies. Vote average and popularity provide ranking signals. Combined, they give enough signal for meaningful content-based recommendations.

---

## 4. Data Preprocessing

### Text Cleaning Pipeline (`app/ml/preprocessing.py`)

```python
# Step 1: Lowercase everything
"A Thief Who Steals" ΓåÆ "a thief who steals"

# Step 2: Remove special characters
"sci-fi, action/adventure!" ΓåÆ "scifi actionadventure"

# Step 3: Remove stopwords
"a thief who steals from the mind" ΓåÆ "thief steals mind"

# Step 4: Combine features
overview + genre_names + keywords ΓåÆ single text blob
```

### Why Each Step

| Step | Why | What Happens Without It |
|------|-----|------------------------|
| Lowercase | "Inception" and "inception" are treated as same word | Double-counted as different features |
| Remove special chars | Prevents punctuation from being treated as tokens | "sci-fi" and "scifi" become different words |
| Stopwords | "the", "a", "is" add noise, not meaning | TF-IDF wastes dimensions on meaningless words |
| Feature combo | More text = more signal for similarity | Overview alone might be too short for some movies |

---

## 5. Feature Engineering ΓÇö TF-IDF

### What Is TF-IDF?

**TF-IDF = Term Frequency ├ù Inverse Document Frequency**

In plain English: "How important is this word to THIS specific movie compared to ALL movies?"

| Concept | Meaning | Example |
|---------|---------|---------|
| **TF** (Term Frequency) | How often a word appears in this movie's text | "heist" appears 3 times in Inception's text |
| **IDF** (Inverse Document Frequency) | How rare this word is across all movies | "heist" appears in only 5 out of 5000 movies ΓåÆ high IDF |
| **TF-IDF** | TF ├ù IDF | "heist" is both frequent in Inception AND rare overall ΓåÆ HIGH score |

### Why TF-IDF Over CountVectorizer?

| Method | Problem |
|--------|---------|
| CountVectorizer | Treats all words equally ΓÇö "movie" (appears everywhere) gets same weight as "heist" (rare, meaningful) |
| TF-IDF | Downweights common words, upweights distinctive words |

### How Movies Become Vectors

```
Movie: "Inception" ΓåÆ text: "thief steals dreams heist subconscious mind"
                   ΓåÆ TF-IDF vector: [0.0, 0.45, 0.0, 0.62, 0.0, 0.38, ...]
                                      Γåæ              Γåæ              Γåæ
                                   "action"       "heist"        "mind"
                                   (common)       (rare)         (moderate)
```

Each movie becomes a **numerical vector** with thousands of dimensions (one per unique word in the entire dataset).

---

## 6. Recommendation Logic ΓÇö Cosine Similarity

### What Is Cosine Similarity?

It measures the **angle** between two movie vectors, not their magnitude.

```
Cosine Similarity = cos(╬╕) = (A ┬╖ B) / (|A| ├ù |B|)

Score = 1.0 ΓåÆ identical direction (same content)
Score = 0.0 ΓåÆ completely different content
```

### Why Cosine Over Euclidean Distance?

Euclidean distance is affected by document length ΓÇö a 500-word overview vs a 50-word overview would be "far apart" even if they discuss the same topics. Cosine similarity only cares about the **direction** (what topics), not the **magnitude** (how many words).

### How Top-N Recommendations Work

```python
# 1. Compute similarity of movie X with ALL other movies
scores = cosine_similarity(tfidf_matrix[movie_index], tfidf_matrix)

# 2. Sort by similarity score (descending)
sorted_scores = sorted(enumerate(scores[0]), key=lambda x: x[1], reverse=True)

# 3. Return top 10 (excluding the movie itself)
recommendations = sorted_scores[1:11]
```

### Performance Optimization

The similarity matrix is **precomputed once** and saved as a `.joblib` file:
- **Without precompute**: Each request recalculates similarity ΓåÆ 2-5 seconds per request
- **With precompute**: Load matrix from file ΓåÆ <50ms per request

---

## 7. Backend ΓÇö Flask API

### Request Flow

```
User types "inception" in search bar
    ΓåÆ Frontend sends: GET /api/v1/search?q=inception&page=1
    ΓåÆ Nginx proxies to Flask backend
    ΓåÆ Flask route handler:
        1. Check Redis cache (key: "search:inception:1")
        2. Cache miss ΓåÆ Query SQLite FTS5 index
        3. FTS5 returns ranked results
        4. Save to Redis (TTL: 12 hours)
        5. Return JSON response with source tag
```

### API Response Format

```json
{
  "status": "success",
  "data": [
    {
      "id": 27205,
      "title": "Inception",
      "overview": "Cobb, a skilled thief...",
      "poster_path": "/9gk7adHYeDvhIhOT...",
      "vote_average": 8.4,
      "genre_ids": [28, 12, 878]
    }
  ],
  "cached": false,
  "source": "database"
}
```

### Source Tags (Debugging)

Every response tells you WHERE the data came from:

| Source | Meaning |
|--------|---------|
| `redis` | Served from hot cache |
| `database` | Served from SQLite |
| `tmdb_api` | Fetched live from TMDB |
| `database_stale` | SQLite data is old, but API was down |
| `fallback` | Emergency fallback (default popular) |

---

## 8. Database Layer ΓÇö SQLite + FTS5

### Why SQLite?

| Feature | Benefit |
|---------|---------|
| Zero configuration | No separate database server needed |
| WAL mode | Concurrent reads don't block writes |
| FTS5 module | Built-in full-text search with ranking |
| Single file | Easy backup, easy Docker volume mount |
| ACID compliant | No data corruption on crashes |

### Full-Text Search (FTS5)

Instead of `LIKE '%inception%'` (slow, no ranking), FTS5 provides:

```sql
-- Ranked search with BM25 scoring
SELECT * FROM movies_fts
WHERE movies_fts MATCH 'inception'
ORDER BY rank;
```

This gives Google-like ranked results based on term frequency and relevance.

### Staleness Strategy

Each category has its own "stale after" threshold:

```python
STALE_TRENDING = 6 * 3600      # 6 hours ΓÇö changes fast
STALE_POPULAR = 12 * 3600      # 12 hours
STALE_HIGH_RATED = 7 * 86400   # 7 days ΓÇö very stable
STALE_GENRES = 30 * 86400      # 30 days ΓÇö almost never changes
```

When data is stale, the system fetches fresh data from TMDB, saves it, and serves the new version. If TMDB is down, it serves the stale data with `source: "database_stale"` ΓÇö degraded but functional.

---

## 9. Frontend ΓÇö React + Tailwind

### Key Design Decisions

| Decision | Why |
|----------|-----|
| Vite (not CRA) | 10x faster dev server, native ES modules |
| Tailwind CSS v4 | Utility-first, rapid dark-mode styling |
| Axios | Request interceptors, timeout handling |
| React Router v6 | Client-side routing without page reloads |
| Debounced search | 300ms delay prevents flooding the API |

### Proxy Architecture

In development, Vite proxies `/api/*` to `localhost:5000`:
```javascript
// vite.config.js
proxy: {
  "/api": { target: "http://localhost:5000", changeOrigin: true }
}
```

In production, Nginx does the same:
```nginx
location /api/ {
    proxy_pass http://backend:5000;
}
```

The frontend code (`API_BASE = ""`) uses relative URLs, so it works identically in both environments without any code changes.

---

## 10. AWS Deployment ΓÇö Step by Step

### Why EC2?

| Option Considered | Why Not |
|-------------------|---------|
| Lambda + API Gateway | Cold starts kill recommendation latency; SQLite needs persistent filesystem |
| ECS Fargate | Overkill for single-instance; costs more |
| Elastic Beanstalk | Less control; adds abstraction |
| **EC2 (chosen)** | Full control, free tier, Docker Compose support |

### Deployment Steps (Exactly What I Did)

#### Step 1: Configure AWS CLI
```bash
aws configure
# Access Key ID: ****
# Secret Access Key: ****
# Region: ap-south-1 (Mumbai)
# Output: json
```

#### Step 2: Create SSH Key Pair
```bash
aws ec2 create-key-pair --key-name movie-recommender-key \
  --query "KeyMaterial" --output text > ~/.ssh/movie-recommender-key.pem
```

#### Step 3: Create Security Group
```bash
aws ec2 create-security-group --group-name movie-recommender-sg \
  --description "MovieRecommender - HTTP + SSH"

# Open port 80 (HTTP) and 22 (SSH)
aws ec2 authorize-security-group-ingress --group-id sg-XXXXX \
  --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-XXXXX \
  --protocol tcp --port 22 --cidr 0.0.0.0/0
```

#### Step 4: Launch EC2 with User Data
```bash
aws ec2 run-instances \
  --image-id ami-090eaa8ecb757149c \
  --instance-type t3.micro \
  --key-name movie-recommender-key \
  --security-group-ids sg-XXXXX \
  --user-data file://docker/ec2-user-data.sh \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=MovieRecommender}]"
```

The `ec2-user-data.sh` script runs automatically on first boot:
1. Installs Docker + Docker Compose
2. Clones the GitHub repo
3. Creates `.env` with production settings
4. Runs `docker-compose up -d --build`

#### Step 5: Verify
```bash
# Wait ~5 minutes for Docker build
curl http://<public-ip>/api/v1/health
# {"status": "healthy", "database": {"movies": 65, "genres": 19}}
```

### CloudWatch Monitoring

EC2 instances have **Basic Monitoring** enabled by default (free):

| Metric | Frequency | Where To See |
|--------|-----------|-------------|
| CPU Utilization | Every 5 min | EC2 ΓåÆ Instance ΓåÆ Monitoring tab |
| Network In/Out | Every 5 min | Same location |
| Disk Read/Write | Every 5 min | Same location |
| Status Checks | Every 1 min | EC2 ΓåÆ Instance ΓåÆ Status checks |

**How to view:** AWS Console ΓåÆ EC2 ΓåÆ Instances ΓåÆ Select `MovieRecommender` ΓåÆ **Monitoring** tab

You can also create **CloudWatch Alarms**:
- Alert when CPU > 80% for 5 minutes
- Alert when status check fails

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "MovieRS-High-CPU" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=InstanceId,Value=i-0e1ddea77e9ec9614
```

For **application-level logs**, SSH into the instance:
```bash
ssh -i ~/.ssh/movie-recommender-key.pem ec2-user@3.111.150.141
cd app/docker
docker-compose logs -f backend   # Flask logs
docker-compose logs -f frontend  # Nginx access logs
```

---

## 11. Errors Faced During Development

### Error 1: SQLite WAL Files Pushed to Git

**What happened:** `data/movies.db-shm` and `data/movies.db-wal` were staged by `git add .`

**Why:** `.gitignore` only had `data/*.db` but SQLite WAL mode creates `-shm` and `-wal` companion files.

**Fix:**
```bash
git rm --cached data/movies.db-shm data/movies.db-wal
# Added to .gitignore:
data/*.db-shm
data/*.db-wal
```

### Error 2: Git Push Rejected (Remote Has Content)

**What happened:** `git push` failed with "remote contains work that you do not have locally"

**Why:** The GitHub repo was initialized with a README, creating a commit that doesn't exist locally.

**Fix:** `git push --force origin main` (safe because this was the initial push)

### Error 3: IAM User Missing EC2 Permissions

**What happened:** `aws ec2 create-key-pair` returned `UnauthorizedOperation`

**Why:** The IAM user `User001` only had default permissions, no EC2 access.

**Fix:** Added `AmazonEC2FullAccess` policy to the IAM user via AWS Console.

### Error 4: `t2.micro` Not Free Tier in ap-south-1

**What happened:** `run-instances` returned "instance type is not eligible for Free Tier"

**Why:** AWS changed free tier eligibility. In `ap-south-1`, `t3.micro` is now the free tier type.

**Fix:**
```bash
aws ec2 describe-instance-types \
  --filters "Name=free-tier-eligible,Values=true" \
  --query "InstanceTypes[*].InstanceType"
# Result: t3.micro, t3.small, t4g.micro, etc.
```
Changed instance type to `t3.micro`.

### Error 5: SSH Key File Save Failed

**What happened:** Key pair was created in AWS but the `.pem` file wasn't saved locally.

**Why:** The `~/.ssh/` directory didn't exist on the Windows machine.

**Fix:**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.ssh"
# Then re-create the key pair
```

### Error 6: Tailwind `@theme` CSS Lint Warning

**What happened:** VS Code showed "Unknown at rule @theme" in `index.css`

**Why:** Tailwind CSS v4 uses `@theme` which older CSS linters don't recognize.

**Fix:** Added `.vscode/settings.json` with `"css.lint.unknownAtRules": "ignore"`

### Error 7: CORS Issues in Development

**What happened:** Frontend at `localhost:5173` couldn't reach API at `localhost:5000`

**Why:** Browser blocks cross-origin requests by default.

**Fix (Development):** Vite proxy handles this ΓÇö frontend sends requests to itself, Vite forwards to backend.

**Fix (Production):** Not an issue ΓÇö Nginx serves both frontend and API from the same origin (port 80).

### Error 8: Gunicorn Workers ├ù APScheduler Duplicates

**What happened:** With 4 Gunicorn workers, the background scheduler ran 4 copies of every job.

**Why:** Each worker process forks the app factory, which starts the scheduler independently.

**Fix:**
1. Reduced workers to 2 (memory constraint on t3.micro)
2. Added `--preload` flag to share the app instance
3. Added `SCHEDULER_ENABLED` environment variable as a leader flag

---

## 12. Limitations

| Limitation | Impact | Why It Exists |
|-----------|--------|---------------|
| SQLite = single writer | Cannot scale horizontally | File-based DB, not client-server |
| No user accounts | Cannot track individual preferences | Authentication not implemented yet |
| Content-based only | Misses social/behavioral signals | No user interaction data collected |
| Cold ML model | Needs manual training with `train_model.py` | No automated retraining pipeline |
| No HTTPS | Traffic is unencrypted | Would need domain + SSL certificate |
| Single EC2 instance | Single point of failure | No load balancer or auto-scaling |

---

## 13. Future Improvements

| Priority | Improvement | Effort |
|----------|------------|--------|
| High | Add HTTPS (Cloudflare or ACM + ALB) | 1 hour |
| High | PostgreSQL migration (for multi-instance) | 1 day |
| Medium | User accounts + watch history | 2-3 days |
| Medium | Collaborative filtering (user-item matrix) | 3-5 days |
| Medium | Elasticsearch for fuzzy/semantic search | 1-2 days |
| Low | CI/CD pipeline (GitHub Actions ΓåÆ ECR ΓåÆ ECS) | 1 day |
| Low | CloudWatch custom metrics + alarms | 2 hours |
| Low | A/B testing framework for recommendations | 2-3 days |

---

## 14. Interview Preparation

### 2-Minute Explanation

> "I built a full-stack movie recommendation system deployed on AWS. The backend is a Flask API that fetches movie data from the TMDB API and stores it in SQLite with full-text search. For recommendations, I use TF-IDF vectorization on movie overviews and compute cosine similarity to find content-similar movies. The similarity matrix is precomputed and stored as a joblib file for sub-50ms response times.
>
> The system uses a cache-aside pattern ΓÇö Redis for hot cache, SQLite for persistence, TMDB API as the source of truth. Each data category has its own staleness threshold. The React frontend is served by Nginx which also reverse-proxies API requests to the Flask backend. The whole thing runs as three Docker containers on a single EC2 instance."

### 5-Minute Explanation

Add to the above:

> "For data preprocessing, I combine movie overviews with genre names, lowercase everything, remove stopwords, and strip special characters. This cleaned text is vectorized using TF-IDF which weights words by how unique they are to each movie ΓÇö so 'heist' gets a high score for Inception because it's rare across all movies but frequent in Inception's text.
>
> The cosine similarity between these vectors gives a 0-to-1 score for how similar two movies are. I precompute the full similarity matrix and serialize it with joblib so recommendations are instant at runtime.
>
> For resilience, if the TMDB API is down, the system gracefully degrades ΓÇö serving stale database data instead of failing. Every API response includes a source tag so you can see whether the data came from cache, database, or the live API. APScheduler runs background jobs to pre-warm trending and popular data so the first user never hits a cold cache.
>
> On AWS, I used EC2 with a user-data bootstrap script that installs Docker, clones the repo from GitHub, and starts everything automatically. CloudWatch provides basic CPU and network monitoring out of the box."

### Common Interview Questions

**Q: Why TF-IDF instead of word embeddings (Word2Vec, BERT)?**
> TF-IDF is interpretable, fast, and sufficient for metadata-level similarity. Word2Vec/BERT would add complexity without proportional benefit when the input text is short movie overviews, not full documents. For a Phase 2, I'd consider sentence-transformers for semantic similarity.

**Q: How do you handle the cold-start problem?**
> Content-based filtering doesn't have a user cold-start problem ΓÇö new users get recommendations based on the movie they're viewing. For movie cold-start, any movie with an overview can be vectorized immediately. APScheduler pre-warms trending data so the database is never empty.

**Q: Why SQLite instead of PostgreSQL?**
> For a single-instance deployment, SQLite provides ACID compliance with zero infrastructure overhead. The entire database is a single file that persists via a Docker volume. The code is abstracted so migrating to PostgreSQL would only require changing the database module ΓÇö all route and service code stays the same.

**Q: What happens if TMDB API goes down?**
> The system has 4 levels of fallback: Redis ΓåÆ SQLite ΓåÆ TMDB API ΓåÆ default_popular table. If the API is unreachable, it serves stale data from the database with a `source: "database_stale"` tag. If even the database is empty (first boot), it returns a hardcoded fallback. The system never returns a 500 error for data availability issues.

**Q: How would you scale this?**
> Phase 1 (current): Single EC2, SQLite, good for ~100 concurrent users. Phase 2: PostgreSQL on RDS, Redis on ElastiCache, ECS Fargate for auto-scaling, ALB for load balancing. Phase 3: Add Elasticsearch for fuzzy search, collaborative filtering with a user-item matrix, and a CI/CD pipeline with GitHub Actions deploying to ECR.

**Q: Why did you precompute the similarity matrix?**
> Without precomputation, every recommendation request would compute cosine similarity across the entire TF-IDF matrix ΓÇö O(n┬▓) operation taking 2-5 seconds. With precomputation, it's a single array lookup ΓÇö O(1) in under 50ms. The tradeoff is memory, but for ~5000 movies the matrix is only ~100MB.

**Q: Explain your caching strategy.**
> Cache-aside pattern with two layers. Redis (in-memory, TTL-based) handles hot data for sub-millisecond responses. SQLite (persistent, staleness-based) survives container restarts. Each category has its own staleness threshold ΓÇö trending data becomes stale after 6 hours, genre lists after 30 days. This prevents unnecessary API calls while keeping data fresh where it matters.

---

*Built by Deepanshu Talan ΓÇö [GitHub](https://github.com/deepanshu-talan/scalable-movie-recommendation-system)*
