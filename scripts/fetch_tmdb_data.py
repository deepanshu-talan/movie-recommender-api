"""Fetch movie data from TMDB API and build an offline dataset.

Usage:
    python scripts/fetch_tmdb_data.py --count 5000 --output data/tmdb_dataset/movies.json

Fetches popular movies from TMDB, including keywords, and saves
them as a JSON file ready for ML training.
"""
import os
import sys
import json
import time
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tmdb_service import tmdb_service
from app.core.logging_config import setup_logging, get_logger

setup_logging("INFO")
logger = get_logger("fetch_data")


def fetch_movies(count: int = 5000) -> list:
    """Fetch top N popular movies from TMDB with keywords."""
    movies = []
    seen_ids = set()
    pages_needed = (count // 20) + 1  # TMDB returns 20 per page

    logger.info("starting_fetch", target_count=count, pages=pages_needed)

    for page in range(1, pages_needed + 1):
        if len(movies) >= count:
            break

        result = tmdb_service.get_popular(page)
        batch = result.get("results", [])

        if not batch:
            logger.warning("empty_page", page=page)
            break

        for movie in batch:
            if len(movies) >= count:
                break
            if movie["id"] in seen_ids:
                continue
            if not movie.get("overview"):
                continue

            seen_ids.add(movie["id"])

            # Fetch keywords for this movie
            keywords = tmdb_service.get_movie_keywords(movie["id"])
            movie["keywords"] = keywords

            movies.append(movie)
            time.sleep(0.3)

            if len(movies) % 100 == 0:
                logger.info("fetch_progress", fetched=len(movies), target=count)

        # Respect rate limits
        time.sleep(0.25)

    logger.info("fetch_complete", total=len(movies))
    return movies


def main():
    parser = argparse.ArgumentParser(description="Fetch TMDB movie dataset")
    parser.add_argument("--count", type=int, default=5000, help="Number of movies to fetch")
    parser.add_argument("--output", type=str, default="data/tmdb_dataset/movies.json", help="Output file path")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    movies = fetch_movies(args.count)
    if not movies:
        print("No movies fetched. Check TMDB credentials and network access; dataset was not overwritten.")
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    logger.info("dataset_saved", path=args.output, count=len(movies))
    print(f"\nSaved {len(movies)} movies to {args.output}")


if __name__ == "__main__":
    main()
