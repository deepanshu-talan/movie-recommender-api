"""TMDB API service — handles all communication with The Movie Database API."""
import time
import re
import requests
from app.core.config import Config
from app.core.logging_config import get_logger

logger = get_logger("tmdb_service")


class TMDBService:
    """Client for TMDB API v3 with retry and error handling."""

    def __init__(self):
        self.base_url = Config.TMDB_BASE_URL
        self.api_key = Config.TMDB_API_KEY
        self.access_token = Config.TMDB_ACCESS_TOKEN
        self.session = requests.Session()
        self.session.headers.update({"accept": "application/json"})

        if self.access_token:
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
        elif not self.api_key:
            logger.warning("tmdb_credentials_missing")

    def _request(self, endpoint: str, params: dict = None, retries: int = 1) -> dict | None:
        """Make a GET request to TMDB with retry/backoff for transient failures."""
        url = f"{self.base_url}{endpoint}"
        request_params = dict(params or {})
        if not self.access_token and self.api_key:
            request_params["api_key"] = self.api_key

        for attempt in range(retries):
            try:
                resp = self.session.get(url, params=request_params, timeout=6)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 429:
                    wait = 2 ** attempt
                    logger.warning("tmdb_rate_limited", retry_in=wait, attempt=attempt + 1)
                    time.sleep(wait)
                    continue
                if resp.status_code == 404:
                    logger.info("tmdb_not_found", endpoint=endpoint)
                    return None
                logger.error("tmdb_error", status=resp.status_code, endpoint=endpoint, body=resp.text[:200])
                if resp.status_code in {500, 502, 503, 504} and attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except requests.RequestException as e:
                logger.error("tmdb_request_failed", error=self._sanitize_error(e), attempt=attempt + 1)
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None

    @staticmethod
    def _sanitize_error(error: Exception) -> str:
        """Remove credentials from request exception messages."""
        return re.sub(r"api_key=[^&\s)]+", "api_key=<redacted>", str(error))

    def search_movies(self, query: str, page: int = 1) -> dict:
        """Search movies by title. Returns {results, total_pages, total_results}."""
        data = self._request("/search/movie", {"query": query, "page": page})
        if not data:
            return {"results": [], "total_pages": 0, "total_results": 0}
        return {
            "results": [self._normalize_movie(m) for m in data.get("results", [])],
            "total_pages": data.get("total_pages", 0),
            "total_results": data.get("total_results", 0),
            "page": data.get("page", 1),
        }

    def get_movie_details(self, movie_id: int) -> dict | None:
        """Get detailed movie info by TMDB ID."""
        data = self._request(f"/movie/{movie_id}", {"append_to_response": "keywords"})
        if not data:
            return None
        movie = self._normalize_movie(data)
        # Add extra detail fields
        movie["runtime"] = data.get("runtime")
        movie["budget"] = data.get("budget", 0)
        movie["revenue"] = data.get("revenue", 0)
        movie["tagline"] = data.get("tagline", "")
        movie["status"] = data.get("status", "")
        # Extract keywords
        keywords_data = data.get("keywords", {})
        movie["keywords"] = [k["name"] for k in keywords_data.get("keywords", [])]
        return movie

    def get_movie_keywords(self, movie_id: int) -> list:
        """Get keywords for a movie."""
        data = self._request(f"/movie/{movie_id}/keywords")
        if not data:
            return []
        return [k["name"] for k in data.get("keywords", [])]

    def get_movie_videos(self, movie_id: int) -> list:
        """Get official YouTube videos/trailers for a movie."""
        data = self._request(f"/movie/{movie_id}/videos")
        if not data:
            return []
        videos = []
        for video in data.get("results", []):
            if video.get("site") != "YouTube":
                continue
            videos.append({
                "id": video.get("id"),
                "key": video.get("key"),
                "name": video.get("name"),
                "type": video.get("type"),
                "official": video.get("official", False),
                "published_at": video.get("published_at"),
                "url": f"https://www.youtube.com/watch?v={video.get('key')}",
                "embed_url": f"https://www.youtube.com/embed/{video.get('key')}",
            })
        videos.sort(key=lambda v: (v["type"] != "Trailer", not v["official"], v.get("published_at") or ""), reverse=False)
        return videos

    def get_trending(self, time_window: str = "week") -> list:
        """Get trending movies (day or week)."""
        data = self._request(f"/trending/movie/{time_window}")
        if not data:
            return []
        return [self._normalize_movie(m) for m in data.get("results", [])]

    def get_popular(self, page: int = 1) -> dict:
        """Get popular movies with pagination."""
        data = self._request("/movie/popular", {"page": page})
        if not data:
            return {"results": [], "total_pages": 0}
        return {
            "results": [self._normalize_movie(m) for m in data.get("results", [])],
            "total_pages": data.get("total_pages", 0),
            "page": data.get("page", 1),
        }

    def discover_movies(self, page: int = 1, sort_by: str = "popularity.desc", preferences: dict | None = None) -> dict:
        """Discover movies from TMDB using optional preference filters."""
        preferences = preferences or {}
        params = {"page": page, "sort_by": sort_by}

        language = _preference_language(preferences)
        if language:
            params["with_original_language"] = language

        genre_id = _preference_genre_id(preferences)
        if genre_id:
            params["with_genres"] = genre_id

        if sort_by == "vote_average.desc":
            params["vote_count.gte"] = 50

        data = self._request("/discover/movie", params)
        if not data:
            return {"results": [], "total_pages": 0, "total_results": 0, "page": page}
        return {
            "results": [self._normalize_movie(m) for m in data.get("results", [])],
            "total_pages": data.get("total_pages", 0),
            "total_results": data.get("total_results", 0),
            "page": data.get("page", page),
        }

    def get_genre_list(self) -> dict:
        """Get genre ID → name mapping."""
        data = self._request("/genre/movie/list")
        if not data:
            return {}
        return {g["id"]: g["name"] for g in data.get("genres", [])}

    def get_recommendations(self, movie_id: int) -> list:
        """Get TMDB's own recommendations for a movie (fallback)."""
        data = self._request(f"/movie/{movie_id}/recommendations")
        if not data:
            return []
        return [self._normalize_movie(m) for m in data.get("results", [])[:10]]

    @staticmethod
    def _normalize_movie(raw: dict) -> dict:
        """Normalize TMDB response to our internal format."""
        return {
            "id": raw.get("id"),
            "title": raw.get("title", "Unknown"),
            "overview": raw.get("overview", ""),
            "release_date": raw.get("release_date", ""),
            "year": raw.get("release_date", "")[:4] if raw.get("release_date") else "",
            "genres": [g["name"] if isinstance(g, dict) else g for g in raw.get("genres", raw.get("genre_ids", []))],
            "vote_average": raw.get("vote_average", 0),
            "vote_count": raw.get("vote_count", 0),
            "popularity": raw.get("popularity", 0),
            "poster_path": raw.get("poster_path"),
            "backdrop_path": raw.get("backdrop_path"),
            "original_language": raw.get("original_language", "en"),
        }


# Singleton instance
tmdb_service = TMDBService()


def _preference_language(preferences: dict) -> str:
    industry = (preferences.get("industry") or "all").lower()
    language = (preferences.get("language") or "all").lower()
    industry_languages = {
        "hollywood": "en",
        "bollywood": "hi",
        "korean": "ko",
        "japanese": "ja",
    }
    return industry_languages.get(industry) or ("" if language == "all" else language)


def _preference_genre_id(preferences: dict) -> int | None:
    genre = (preferences.get("genre") or "all").lower()
    if genre == "all":
        return None
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
    return genre_ids.get(genre)
