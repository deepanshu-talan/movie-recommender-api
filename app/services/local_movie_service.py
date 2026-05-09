"""Local movie catalog backed by the SQLite persistent database.

This module provides the same interface as before but reads from SQLite
instead of a JSON flat-file. Used by routes and the recommendation service
when they need local movie data without going to the TMDB API.
"""
from app.db.movie_db import (
    get_movie as db_get_movie,
    search_movies as db_search,
    get_category,
    get_genres as db_get_genres,
    get_default_popular,
)


GENRE_MAP = {
    12: "Adventure", 14: "Fantasy", 16: "Animation", 18: "Drama",
    27: "Horror", 28: "Action", 35: "Comedy", 36: "History",
    37: "Western", 53: "Thriller", 80: "Crime", 99: "Documentary",
    878: "Science Fiction", 9648: "Mystery", 10402: "Music",
    10749: "Romance", 10751: "Family", 10752: "War", 10770: "TV Movie",
}


def get_movie(movie_id: int) -> dict | None:
    """Find a local movie by TMDB ID."""
    return db_get_movie(movie_id)


def get_popular(page: int = 1, per_page: int = 20, preferences: dict | None = None) -> dict:
    """Return locally cached popular movies with pagination."""
    data = get_category("popular", page=page, per_page=per_page, preferences=preferences)
    if data["results"]:
        return data
    # Fallback to default popular if category is empty
    fallback = get_default_popular(limit=per_page)
    return {
        "results": fallback,
        "total_pages": 1,
        "total_results": len(fallback),
        "page": 1,
    }


def get_high_rated(page: int = 1, per_page: int = 20, preferences: dict | None = None) -> dict:
    """Return local movies sorted by rating."""
    data = get_category("high_rated", page=page, per_page=per_page, preferences=preferences)
    return data


def get_trending(limit: int = 20, preferences: dict | None = None) -> list[dict]:
    """Return a local trending list."""
    data = get_category("trending", page=1, per_page=limit, preferences=preferences)
    return data.get("results", [])


def search_movies(query: str, page: int = 1, per_page: int = 20) -> dict:
    """Search local movie database using FTS5."""
    return db_search(query, page, per_page)


def get_genres() -> dict:
    """Return genres from DB, falling back to hardcoded map."""
    db_genres = db_get_genres()
    return db_genres if db_genres else GENRE_MAP.copy()


def resolve_genres(genres: list) -> dict:
    """Normalize mixed genre IDs/names to an ID-to-name mapping."""
    resolved = {}
    for genre in genres or []:
        if isinstance(genre, dict):
            genre_id = genre.get("id")
            name = genre.get("name")
        elif isinstance(genre, int):
            genre_id = genre
            name = GENRE_MAP.get(genre, str(genre))
        else:
            genre_id = str(genre)
            name = str(genre)

        if genre_id is not None and name:
            resolved[genre_id] = name
    return resolved


def paginate(movies: list[dict], page: int = 1, per_page: int = 20) -> dict:
    """Paginate a list using TMDB-like response keys."""
    page = max(1, page)
    total_results = len(movies)
    total_pages = max(1, (total_results + per_page - 1) // per_page) if total_results else 0
    start = (page - 1) * per_page
    end = start + per_page

    return {
        "results": [m.copy() if isinstance(m, dict) else m for m in movies[start:end]],
        "total_pages": total_pages,
        "total_results": total_results,
        "page": page,
    }
