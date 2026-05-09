"""Background scheduler for pre-warming trending/popular data.

Uses APScheduler to periodically fetch fresh data from TMDB and save it
to the SQLite database, ensuring cold starts are instant and data stays fresh.

Leader flag: Only one instance should run the scheduler in multi-instance
deployments. Set SCHEDULER_ENABLED=0 on non-leader instances.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import Config
from app.core.logging_config import get_logger

logger = get_logger("scheduler")

_scheduler = None


def start_scheduler() -> None:
    """Start the background scheduler if this instance is the leader."""
    global _scheduler

    if not Config.SCHEDULER_ENABLED:
        logger.info("scheduler_disabled", reason="SCHEDULER_ENABLED=0")
        return

    if _scheduler is not None:
        return  # Already running

    _scheduler = BackgroundScheduler(daemon=True)

    # Trending: refresh every 6 hours
    _scheduler.add_job(
        refresh_trending,
        trigger=IntervalTrigger(hours=6),
        id="refresh_trending",
        name="Refresh trending movies",
        replace_existing=True,
    )

    # Popular: refresh every 6 hours
    _scheduler.add_job(
        refresh_popular,
        trigger=IntervalTrigger(hours=6),
        id="refresh_popular",
        name="Refresh popular movies",
        replace_existing=True,
    )

    # Genres: refresh daily
    _scheduler.add_job(
        refresh_genres,
        trigger=IntervalTrigger(hours=24),
        id="refresh_genres",
        name="Refresh genre list",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("scheduler_started", jobs=3)

    # Run initial refresh on startup (non-blocking)
    _scheduler.add_job(
        _initial_refresh,
        id="initial_refresh",
        name="Initial data refresh",
        replace_existing=True,
    )


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("scheduler_stopped")


def _initial_refresh() -> None:
    """Run all refresh jobs once on startup to pre-warm the database."""
    logger.info("initial_refresh_started")
    refresh_genres()
    refresh_trending()
    refresh_popular()
    logger.info("initial_refresh_completed")


def refresh_trending() -> None:
    """Fetch trending movies from TMDB and save to DB + Redis."""
    try:
        from app.services.tmdb_service import tmdb_service
        from app.db.movie_db import save_category, is_stale
        from app.services.cache_service import cache_set, cache_key, TTL_TRENDING

        if not is_stale("trending", page=1):
            logger.debug("trending_still_fresh")
            return

        data = tmdb_service.get_trending(time_window="week")
        if data:
            save_category("trending", data, page=1, stale_hours=Config.STALE_TRENDING)
            # Also warm Redis
            ck = cache_key("tmdb", "trending", "week", "all", "all", "all")
            cache_set(ck, data, TTL_TRENDING)
            logger.info("trending_refreshed", count=len(data))
        else:
            logger.warning("trending_refresh_empty")
    except Exception as e:
        logger.error("trending_refresh_failed", error=str(e))


def refresh_popular() -> None:
    """Fetch popular movies (pages 1-3) from TMDB and save to DB + Redis."""
    try:
        from app.services.tmdb_service import tmdb_service
        from app.db.movie_db import save_category, is_stale, _save_default_popular
        from app.services.cache_service import cache_set, cache_key, TTL_POPULAR

        all_movies = []
        for page in range(1, 4):
            if not is_stale("popular", page=page):
                continue
            data = tmdb_service.get_popular(page=page)
            results = data.get("results", [])
            if results:
                save_category("popular", results, page=page,
                              stale_hours=Config.STALE_POPULAR)
                all_movies.extend(results)
                # Warm Redis for this page
                ck = cache_key("tmdb", "popular", page, "all", "all", "all")
                cache_set(ck, data, TTL_POPULAR)

        if all_movies:
            # Update default popular fallback with the freshest data
            _save_default_popular(all_movies[:60])
            logger.info("popular_refreshed", count=len(all_movies))
        else:
            logger.debug("popular_still_fresh")
    except Exception as e:
        logger.error("popular_refresh_failed", error=str(e))


def refresh_genres() -> None:
    """Fetch genre list from TMDB and save to DB + Redis."""
    try:
        from app.services.tmdb_service import tmdb_service
        from app.db.movie_db import save_genres, is_stale
        from app.services.cache_service import cache_set, cache_key, TTL_GENRES

        if not is_stale("genres", page=1):
            logger.debug("genres_still_fresh")
            return

        data = tmdb_service.get_genre_list()
        if data:
            save_genres(data)
            ck = cache_key("tmdb", "genres")
            cache_set(ck, data, TTL_GENRES)
            logger.info("genres_refreshed", count=len(data))
        else:
            logger.warning("genres_refresh_empty")
    except Exception as e:
        logger.error("genres_refresh_failed", error=str(e))
