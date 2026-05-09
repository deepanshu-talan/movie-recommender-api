"""SQLite persistent movie store with FTS5 full-text search.

Provides a clean CRUD interface over an embedded SQLite database.
All movie data fetched from the TMDB API is persisted here so
subsequent requests are served locally without hitting the API.

Design notes
------------
- Uses WAL mode for better read concurrency.
- FTS5 virtual table for ranked full-text search on title/overview/keywords.
- Triggers keep the FTS index in sync automatically (INSERT/UPDATE/DELETE).
- Per-category staleness tracked in the ``staleness`` table.
- Interface is abstract enough to swap SQLite → PostgreSQL later.
"""
import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta, timezone

from app.core.config import Config
from app.core.logging_config import get_logger

logger = get_logger("movie_db")

# Thread-local connections (SQLite objects can't cross threads)
_local = threading.local()


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def _get_conn() -> sqlite3.Connection:
    """Return a thread-local SQLite connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
        _local.conn = sqlite3.connect(
            Config.DATABASE_PATH,
            check_same_thread=False,
            timeout=10,
        )
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
        _local.conn.execute("PRAGMA busy_timeout=5000")
    return _local.conn


def _dict_row(row: sqlite3.Row | None) -> dict | None:
    """Convert a sqlite3.Row to a plain dict."""
    if row is None:
        return None
    d = dict(row)
    # Deserialize JSON fields
    for field in ("genres", "keywords"):
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                d[field] = []
    return d


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
-- Core movie data
CREATE TABLE IF NOT EXISTS movies (
    id              INTEGER PRIMARY KEY,
    title           TEXT    NOT NULL,
    overview        TEXT    DEFAULT '',
    release_date    TEXT    DEFAULT '',
    vote_average    REAL    DEFAULT 0,
    vote_count      INTEGER DEFAULT 0,
    popularity      REAL    DEFAULT 0,
    poster_path     TEXT,
    backdrop_path   TEXT,
    original_language TEXT  DEFAULT 'en',
    runtime         INTEGER,
    budget          INTEGER DEFAULT 0,
    revenue         INTEGER DEFAULT 0,
    tagline         TEXT    DEFAULT '',
    status          TEXT    DEFAULT '',
    keywords        TEXT    DEFAULT '[]',
    genres          TEXT    DEFAULT '[]',
    created_at      TEXT    DEFAULT (datetime('now')),
    updated_at      TEXT    DEFAULT (datetime('now'))
);

-- Genre reference table
CREATE TABLE IF NOT EXISTS genres (
    id   INTEGER PRIMARY KEY,
    name TEXT    NOT NULL
);

-- Category lists (trending, popular, high_rated)
CREATE TABLE IF NOT EXISTS categories (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,
    movie_id  INTEGER NOT NULL,
    position  INTEGER DEFAULT 0,
    page      INTEGER DEFAULT 1,
    updated_at TEXT   DEFAULT (datetime('now')),
    UNIQUE(name, movie_id, page)
);

-- Staleness tracker per category (+ per page)
CREATE TABLE IF NOT EXISTS staleness (
    category         TEXT    NOT NULL,
    page             INTEGER DEFAULT 1,
    updated_at       TEXT    DEFAULT (datetime('now')),
    stale_after_hours INTEGER DEFAULT 24,
    PRIMARY KEY (category, page)
);

-- Default popular fallback (survives total failure)
CREATE TABLE IF NOT EXISTS default_popular (
    movie_id INTEGER PRIMARY KEY,
    position INTEGER DEFAULT 0,
    data     TEXT    NOT NULL
);
"""

_FTS_SQL = """
CREATE VIRTUAL TABLE IF NOT EXISTS movies_fts USING fts5(
    title, overview, keywords,
    content='movies', content_rowid='id'
);
"""

_TRIGGERS_SQL = """
-- Keep FTS index in sync with movies table
CREATE TRIGGER IF NOT EXISTS movies_ai AFTER INSERT ON movies BEGIN
    INSERT INTO movies_fts(rowid, title, overview, keywords)
    VALUES (new.id, new.title, new.overview, new.keywords);
END;

CREATE TRIGGER IF NOT EXISTS movies_ad AFTER DELETE ON movies BEGIN
    INSERT INTO movies_fts(movies_fts, rowid, title, overview, keywords)
    VALUES ('delete', old.id, old.title, old.overview, old.keywords);
END;

CREATE TRIGGER IF NOT EXISTS movies_au AFTER UPDATE ON movies BEGIN
    INSERT INTO movies_fts(movies_fts, rowid, title, overview, keywords)
    VALUES ('delete', old.id, old.title, old.overview, old.keywords);
    INSERT INTO movies_fts(rowid, title, overview, keywords)
    VALUES (new.id, new.title, new.overview, new.keywords);
END;
"""

_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_categories_name_page ON categories(name, page);
CREATE INDEX IF NOT EXISTS idx_movies_popularity ON movies(popularity DESC);
CREATE INDEX IF NOT EXISTS idx_movies_vote_average ON movies(vote_average DESC);
CREATE INDEX IF NOT EXISTS idx_movies_updated ON movies(updated_at);
"""


def init_db() -> None:
    """Create all tables, FTS index, triggers, and indexes.

    Safe to call multiple times — uses IF NOT EXISTS throughout.
    On first run, imports the existing JSON dataset if available.
    """
    conn = _get_conn()
    conn.executescript(_SCHEMA_SQL)
    conn.executescript(_FTS_SQL)
    conn.executescript(_TRIGGERS_SQL)
    conn.executescript(_INDEX_SQL)
    conn.commit()
    logger.info("database_initialized", path=Config.DATABASE_PATH)

    # One-time import of existing JSON dataset
    _import_json_dataset_if_needed(conn)


def _import_json_dataset_if_needed(conn: sqlite3.Connection) -> None:
    """Import data/tmdb_dataset/movies.json into SQLite on first run."""
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    if count > 0:
        return  # Already populated

    dataset_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "tmdb_dataset", "movies.json",
    )
    if not os.path.exists(dataset_path):
        logger.info("no_json_dataset_to_import", path=dataset_path)
        return

    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            movies = json.load(f)
        if movies:
            save_movies(movies)
            # Also seed default_popular with top 60 by popularity
            top = sorted(movies, key=lambda m: m.get("popularity", 0), reverse=True)[:60]
            _save_default_popular(top)
            logger.info("json_dataset_imported", count=len(movies))
    except Exception as e:
        logger.warning("json_dataset_import_failed", error=str(e))


# ---------------------------------------------------------------------------
# Movie CRUD
# ---------------------------------------------------------------------------

def get_movie(movie_id: int) -> dict | None:
    """Fetch a single movie by TMDB ID. Returns None if not found."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    return _dict_row(row)


def save_movie(movie: dict) -> None:
    """Upsert a single movie record."""
    conn = _get_conn()
    _upsert_movie(conn, movie)
    conn.commit()


def save_movies(movies: list[dict]) -> None:
    """Bulk upsert a list of movie dicts."""
    conn = _get_conn()
    for movie in movies:
        _upsert_movie(conn, movie)
    conn.commit()


def _upsert_movie(conn: sqlite3.Connection, movie: dict) -> None:
    """Insert or replace a movie row."""
    genres = movie.get("genres", [])
    keywords = movie.get("keywords", [])
    # Normalize genres to list of strings
    if genres and isinstance(genres[0], dict):
        genres = [g.get("name", "") for g in genres]
    elif genres and isinstance(genres[0], int):
        genres = [str(g) for g in genres]

    conn.execute(
        """INSERT INTO movies (
            id, title, overview, release_date, vote_average, vote_count,
            popularity, poster_path, backdrop_path, original_language,
            runtime, budget, revenue, tagline, status, keywords, genres, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title, overview=excluded.overview,
            release_date=excluded.release_date, vote_average=excluded.vote_average,
            vote_count=excluded.vote_count, popularity=excluded.popularity,
            poster_path=excluded.poster_path, backdrop_path=excluded.backdrop_path,
            original_language=excluded.original_language, runtime=excluded.runtime,
            budget=excluded.budget, revenue=excluded.revenue,
            tagline=excluded.tagline, status=excluded.status,
            keywords=excluded.keywords, genres=excluded.genres,
            updated_at=datetime('now')
        """,
        (
            movie.get("id"),
            movie.get("title", "Unknown"),
            movie.get("overview", ""),
            movie.get("release_date", ""),
            movie.get("vote_average", 0),
            movie.get("vote_count", 0),
            movie.get("popularity", 0),
            movie.get("poster_path"),
            movie.get("backdrop_path"),
            movie.get("original_language", "en"),
            movie.get("runtime"),
            movie.get("budget", 0),
            movie.get("revenue", 0),
            movie.get("tagline", ""),
            movie.get("status", ""),
            json.dumps(keywords),
            json.dumps(genres),
        ),
    )


def is_movie_stale(movie_id: int, stale_hours: int = None) -> bool:
    """Check if a movie record is older than the configured staleness window."""
    if stale_hours is None:
        stale_hours = Config.STALE_MOVIE_DETAIL
    conn = _get_conn()
    row = conn.execute(
        "SELECT updated_at FROM movies WHERE id = ?", (movie_id,)
    ).fetchone()
    if not row:
        return True
    return _is_timestamp_stale(row["updated_at"], stale_hours)


# ---------------------------------------------------------------------------
# Search (FTS5)
# ---------------------------------------------------------------------------

def search_movies(query: str, page: int = 1, per_page: int = 20) -> dict:
    """Full-text search on title, overview, and keywords using FTS5.

    Returns paginated results ranked by relevance.
    """
    conn = _get_conn()
    # FTS5 query: escape special chars, add prefix matching
    fts_query = _sanitize_fts_query(query)
    if not fts_query:
        return {"results": [], "total_pages": 0, "total_results": 0, "page": page}

    # Count total matches
    count_row = conn.execute(
        "SELECT COUNT(*) FROM movies_fts WHERE movies_fts MATCH ?",
        (fts_query,),
    ).fetchone()
    total_results = count_row[0] if count_row else 0
    total_pages = max(1, (total_results + per_page - 1) // per_page) if total_results else 0

    offset = (max(1, page) - 1) * per_page
    rows = conn.execute(
        """SELECT m.* FROM movies m
           JOIN movies_fts f ON m.id = f.rowid
           WHERE f.movies_fts MATCH ?
           ORDER BY rank
           LIMIT ? OFFSET ?""",
        (fts_query, per_page, offset),
    ).fetchall()

    return {
        "results": [_to_movie_response(r) for r in rows],
        "total_pages": total_pages,
        "total_results": total_results,
        "page": page,
    }


def _sanitize_fts_query(query: str) -> str:
    """Sanitize a user query for FTS5. Adds prefix matching."""
    query = query.strip()
    if not query:
        return ""
    # Remove FTS5 special characters to prevent injection
    safe = "".join(c for c in query if c.isalnum() or c in " _-")
    # Split into tokens and add prefix matching
    tokens = safe.split()
    if not tokens:
        return ""
    # Last token gets prefix match, others are exact
    parts = [f'"{t}"' for t in tokens[:-1]]
    parts.append(f'"{tokens[-1]}"*')
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Category lists (trending, popular, high_rated)
# ---------------------------------------------------------------------------

def get_category(name: str, page: int = 1, per_page: int = 20,
                 preferences: dict | None = None) -> dict:
    """Get movies from a named category, optionally filtered by preferences."""
    conn = _get_conn()

    # Build preference filter clause
    where_parts, params = _build_preference_filter(preferences)
    where_clause = f"AND {' AND '.join(where_parts)}" if where_parts else ""

    # Count total
    count_row = conn.execute(
        f"""SELECT COUNT(*) FROM categories c
            JOIN movies m ON c.movie_id = m.id
            WHERE c.name = ? AND c.page = ? {where_clause}""",
        [name, page] + params,
    ).fetchone()
    total_results = count_row[0] if count_row else 0
    total_pages = max(1, (total_results + per_page - 1) // per_page) if total_results else 0

    rows = conn.execute(
        f"""SELECT m.* FROM categories c
            JOIN movies m ON c.movie_id = m.id
            WHERE c.name = ? AND c.page = ? {where_clause}
            ORDER BY c.position
            LIMIT ? OFFSET ?""",
        [name, page] + params + [per_page, 0],
    ).fetchall()

    return {
        "results": [_to_movie_response(r) for r in rows],
        "total_pages": total_pages,
        "total_results": total_results,
        "page": page,
    }


def get_filtered_movies(preferences: dict | None = None, sort: str = "popular",
                        page: int = 1, per_page: int = 20) -> dict:
    """Get movies filtered by preferences using a category-independent ranking."""
    conn = _get_conn()
    where_parts, params = _build_preference_filter(preferences)
    where_clause = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
    sort_sql = {
        "recent": "release_date DESC, popularity DESC, vote_average DESC",
        "popular": "popularity DESC, vote_count DESC, vote_average DESC",
        "rated": "vote_average DESC, vote_count DESC, popularity DESC",
    }.get(sort, "popularity DESC, vote_count DESC, vote_average DESC")

    count_row = conn.execute(
        f"SELECT COUNT(*) FROM movies m {where_clause}",
        params,
    ).fetchone()
    total_results = count_row[0] if count_row else 0
    total_pages = max(1, (total_results + per_page - 1) // per_page) if total_results else 0
    offset = (max(1, page) - 1) * per_page

    rows = conn.execute(
        f"""SELECT m.* FROM movies m
            {where_clause}
            ORDER BY {sort_sql}
            LIMIT ? OFFSET ?""",
        params + [per_page, offset],
    ).fetchall()

    return {
        "results": [_to_movie_response(r) for r in rows],
        "total_pages": total_pages,
        "total_results": total_results,
        "page": page,
    }


def save_category(name: str, movies: list[dict], page: int = 1,
                  stale_hours: int = 24) -> None:
    """Save a list of movies under a named category for a given page."""
    conn = _get_conn()

    # Clear existing entries for this category+page
    conn.execute(
        "DELETE FROM categories WHERE name = ? AND page = ?", (name, page)
    )

    # Insert movies and their category membership
    for i, movie in enumerate(movies):
        _upsert_movie(conn, movie)
        conn.execute(
            """INSERT OR REPLACE INTO categories (name, movie_id, position, page, updated_at)
               VALUES (?, ?, ?, ?, datetime('now'))""",
            (name, movie.get("id"), i, page),
        )

    # Update staleness tracker
    conn.execute(
        """INSERT OR REPLACE INTO staleness (category, page, updated_at, stale_after_hours)
           VALUES (?, ?, datetime('now'), ?)""",
        (name, page, stale_hours),
    )
    conn.commit()


def is_stale(category: str, page: int = 1) -> bool:
    """Check if a category+page combination is stale and needs refresh."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT updated_at, stale_after_hours FROM staleness WHERE category = ? AND page = ?",
        (category, page),
    ).fetchone()
    if not row:
        return True  # Never fetched → stale
    return _is_timestamp_stale(row["updated_at"], row["stale_after_hours"])


# ---------------------------------------------------------------------------
# Genres
# ---------------------------------------------------------------------------

def get_genres() -> dict:
    """Get genre ID → name mapping from the database."""
    conn = _get_conn()
    rows = conn.execute("SELECT id, name FROM genres").fetchall()
    if not rows:
        return {}
    return {row["id"]: row["name"] for row in rows}


def save_genres(genre_map: dict) -> None:
    """Save genre ID → name mapping to the database."""
    conn = _get_conn()
    for gid, name in genre_map.items():
        conn.execute(
            "INSERT OR REPLACE INTO genres (id, name) VALUES (?, ?)",
            (int(gid), name),
        )
    # Update staleness
    conn.execute(
        """INSERT OR REPLACE INTO staleness (category, page, updated_at, stale_after_hours)
           VALUES ('genres', 1, datetime('now'), ?)""",
        (Config.STALE_GENRES,),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Default popular fallback (emergency data when everything fails)
# ---------------------------------------------------------------------------

def _save_default_popular(movies: list[dict]) -> None:
    """Save a default popular list for total-failure fallback."""
    conn = _get_conn()
    conn.execute("DELETE FROM default_popular")
    for i, movie in enumerate(movies):
        conn.execute(
            "INSERT INTO default_popular (movie_id, position, data) VALUES (?, ?, ?)",
            (movie.get("id"), i, json.dumps(movie)),
        )
    conn.commit()


def get_default_popular(limit: int = 20) -> list[dict]:
    """Get the emergency fallback popular list (used when Redis + DB + API all fail)."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT data FROM default_popular ORDER BY position LIMIT ?", (limit,)
    ).fetchall()
    results = []
    for row in rows:
        try:
            results.append(json.loads(row["data"]))
        except (json.JSONDecodeError, TypeError):
            pass
    return results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_timestamp_stale(updated_at_str: str, stale_hours: int) -> bool:
    """Check if a UTC timestamp string is older than stale_hours."""
    try:
        updated = datetime.fromisoformat(updated_at_str).replace(tzinfo=timezone.utc)
        threshold = datetime.now(timezone.utc) - timedelta(hours=stale_hours)
        return updated < threshold
    except (ValueError, TypeError):
        return True


def _build_preference_filter(preferences: dict | None) -> tuple[list[str], list]:
    """Build SQL WHERE clauses from preference filters."""
    if not preferences:
        return [], []

    parts = []
    params = []
    industry = (preferences.get("industry") or "all").lower()
    language = (preferences.get("language") or "all").lower()
    genre = (preferences.get("genre") or "all").lower()

    industry_lang = {
        "hollywood": "en", "bollywood": "hi", "korean": "ko", "japanese": "ja"
    }
    if industry in industry_lang:
        parts.append("m.original_language = ?")
        params.append(industry_lang[industry])
    elif language != "all":
        parts.append("m.original_language = ?")
        params.append(language)

    if genre != "all":
        genre_ids = {
            "action": 28,
            "adventure": 12,
            "animation": 16,
            "comedy": 35,
            "crime": 80,
            "documentary": 99,
            "drama": 18,
            "family": 10751,
            "fantasy": 14,
            "history": 36,
            "horror": 27,
            "music": 10402,
            "mystery": 9648,
            "romance": 10749,
            "science fiction": 878,
            "thriller": 53,
            "tv movie": 10770,
            "war": 10752,
            "western": 37,
        }
        # TMDB category rows can store genres as IDs ([28]) or names
        # (["Action"]), depending on which endpoint saved the movie.
        genre_id = genre_ids.get(genre)
        parts.append("(LOWER(m.genres) LIKE ? OR m.genres LIKE ?)")
        params.append(f'%"{genre}"%')
        params.append(f"%{genre_id}%" if genre_id else "__never_match__")

    return parts, params


def _to_movie_response(row: sqlite3.Row) -> dict:
    """Convert a database row to the standard movie response dict."""
    d = dict(row)
    # Deserialize JSON fields
    for field in ("genres", "keywords"):
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                d[field] = []
    # Add computed year field
    rd = d.get("release_date", "")
    d["year"] = rd[:4] if rd else ""
    # Remove internal timestamps from API response
    d.pop("created_at", None)
    d.pop("updated_at", None)
    return d


def get_db_stats() -> dict:
    """Get database statistics for the health endpoint."""
    conn = _get_conn()
    movie_count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    genre_count = conn.execute("SELECT COUNT(*) FROM genres").fetchone()[0]
    category_count = conn.execute(
        "SELECT COUNT(DISTINCT name) FROM categories"
    ).fetchone()[0]
    return {
        "movies": movie_count,
        "genres": genre_count,
        "categories": category_count,
        "path": Config.DATABASE_PATH,
    }
