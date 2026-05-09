import { useEffect, useMemo, useState } from "react";
import { getGenres, getHighRated, getPopular, getTrending } from "../services/api";
import MovieGrid from "../components/movie/MovieGrid";
import { SkeletonGrid, ErrorMessage } from "../components/ui/Skeleton";
import { getPreferences, matchesPreferences } from "../utils/storage";

const copy = {
  trending: {
    icon: "trending_up",
    title: "Trending Movies",
    subtitle: "Movies people are watching now, served from your local catalog first.",
  },
  highRated: {
    icon: "star",
    title: "High Rated Cinema",
    subtitle: "Top-rated movies filtered by your saved preferences.",
  },
  popular: {
    icon: "local_fire_department",
    title: "Popular Movies",
    subtitle: "Popular picks filtered by your saved preferences.",
  },
  ai: {
    icon: "auto_awesome",
    title: "AI Picks",
    subtitle: "A preference-aware blend of trending and popular titles.",
  },
};

const byTrending = (a, b) => {
  const aDate = Date.parse(a.release_date || "") || 0;
  const bDate = Date.parse(b.release_date || "") || 0;
  if (bDate !== aDate) return bDate - aDate;
  return (b.popularity || 0) - (a.popularity || 0);
};

const byPopular = (a, b) =>
  (b.popularity || 0) - (a.popularity || 0) ||
  (b.vote_count || 0) - (a.vote_count || 0);

const byHighRated = (a, b) =>
  (b.vote_average || 0) - (a.vote_average || 0) ||
  (b.vote_count || 0) - (a.vote_count || 0);

const aiScore = (movie, index) => {
  const bucketBonus = { trending: 0.18, high_rated: 0.12, popular: 0.06 }[movie.ai_bucket] || 0;
  return (
    bucketBonus +
    Math.min((movie.vote_average || 0) / 10, 1) * 0.4 +
    Math.min((movie.popularity || 0) / 250, 1) * 0.25 +
    Math.max(0, 1 - index / 60) * 0.17
  );
};

export default function BrowsePage({ type = "trending" }) {
  const [movies, setMovies] = useState([]);
  const [genreMap, setGenreMap] = useState({});
  const [preferences, setPreferences] = useState(getPreferences());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const page = copy[type] || copy.trending;

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const prefs = getPreferences();
      setPreferences(prefs);
      const genresData = await getGenres();
      let nextMovies = [];

      if (type === "highRated") {
        const data = await getHighRated(1, prefs);
        nextMovies = [...(data.results || [])].sort(byHighRated);
      } else if (type === "popular") {
        const data = await getPopular(1, prefs);
        nextMovies = [...(data.results || [])].sort(byPopular);
      } else if (type === "ai") {
        const [trendingData, popularData, highRatedData] = await Promise.all([
          getTrending(prefs),
          getPopular(1, prefs),
          getHighRated(1, prefs),
        ]);
        const trending = Array.isArray(trendingData) ? trendingData : trendingData.results || [];
        const popular = popularData.results || [];
        const highRated = highRatedData.results || [];
        const seen = new Set();
        const blended = [];
        const maxLength = Math.max(trending.length, popular.length, highRated.length);

        for (let index = 0; index < maxLength; index += 1) {
          if (trending[index]) blended.push({ ...trending[index], ai_bucket: "trending" });
          if (highRated[index]) blended.push({ ...highRated[index], ai_bucket: "high_rated" });
          if (popular[index]) blended.push({ ...popular[index], ai_bucket: "popular" });
        }

        nextMovies = blended.filter((movie) => {
          if (seen.has(movie.id)) return false;
          seen.add(movie.id);
          return matchesPreferences(movie, prefs, genresData || {});
        }).sort((a, b) => aiScore(b, blended.indexOf(b)) - aiScore(a, blended.indexOf(a)));
        nextMovies = nextMovies.map((movie, index) => ({
          ...movie,
          match_percentage: Math.max(60, 97 - index * 1.4),
          similarity: Math.max(0.6, 0.97 - index * 0.014),
        }));
      } else {
        const data = await getTrending(prefs);
        const results = Array.isArray(data) ? data : data.results || [];
        nextMovies = [...results].sort(byTrending);
      }

      setGenreMap(genresData || {});
      setMovies(nextMovies);
    } catch (err) {
      setError(err.message || "Failed to load movies");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const onPreferences = () => fetchData();
    window.addEventListener("movers.preferences:changed", onPreferences);
    return () => window.removeEventListener("movers.preferences:changed", onPreferences);
  }, [type]);

  const preferenceSummary = useMemo(() => {
    return [preferences.industry, preferences.genre, preferences.language]
      .filter((value) => value && value !== "all")
      .join(" / ");
  }, [preferences]);

  return (
    <div className="px-6 sm:px-8 md:px-16 py-8 sm:py-12 w-full max-w-[1440px] mx-auto">
      <div className="mb-8 sm:mb-10 border-b border-white/10 pb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-3">
            <span className="material-symbols-outlined text-secondary text-3xl">{page.icon}</span>
            <h1 className="text-h1 text-white">{page.title}</h1>
          </div>
          <p className="text-gray-400 text-body-md max-w-2xl">{page.subtitle}</p>
        </div>
        {preferenceSummary && (
          <div className="text-xs uppercase tracking-wide text-gray-400 bg-white/5 border border-white/10 rounded-full px-4 py-2">
            {preferenceSummary}
          </div>
        )}
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchData} />}
      {loading ? (
        <SkeletonGrid count={18} />
      ) : movies.length === 0 ? (
        <div className="rounded-xl border border-white/10 bg-surface-container/50 p-10 text-center">
          <span className="material-symbols-outlined text-5xl text-gray-600 mb-3">tune</span>
          <h2 className="text-white text-xl font-semibold mb-2">No movies match these preferences yet</h2>
          <p className="text-gray-400">Try a broader genre/language or fetch a larger TMDB dataset.</p>
        </div>
      ) : (
        <MovieGrid movies={movies} genreMap={genreMap} showMatch={type === "ai"} />
      )}
    </div>
  );
}
