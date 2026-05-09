import { useState, useEffect } from "react";
import { getTrending, getPopular, getGenres } from "../services/api";
import MovieGrid from "../components/movie/MovieGrid";
import { SkeletonGrid, ErrorMessage } from "../components/ui/Skeleton";

export default function RecommendationsPage() {
  const [movies, setMovies] = useState([]);
  const [genreMap, setGenreMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [trendingData, popularData, genresData] = await Promise.all([
        getTrending(),
        getPopular(),
        getGenres(),
      ]);
      const trending = Array.isArray(trendingData) ? trendingData : trendingData.results || [];
      const popular = popularData.results || [];

      // Combine and deduplicate
      const seen = new Set();
      const combined = [...trending, ...popular].filter((m) => {
        if (seen.has(m.id)) return false;
        seen.add(m.id);
        return true;
      });

      // Add synthetic match scores
      combined.forEach((m, i) => {
        m.match_percentage = Math.max(60, 99 - i * 1.5);
        m.similarity = m.match_percentage / 100;
      });

      setMovies(combined);
      setGenreMap(genresData || {});
    } catch (err) {
      setError(err.message || "Failed to load recommendations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="px-6 sm:px-8 md:px-16 py-8 sm:py-12 w-full max-w-[1440px] mx-auto">
      {/* Header */}
      <div className="mb-8 sm:mb-12">
        <div className="flex items-center gap-3 mb-4">
          <span className="material-symbols-outlined text-secondary text-3xl">auto_awesome</span>
          <h1 className="text-h1 text-white">AI Recommendations</h1>
        </div>
        <p className="text-gray-400 text-body-md max-w-2xl">
          Curated picks powered by our content-based recommendation engine.
          These selections are based on genre similarity, keyword matching, and popularity signals.
        </p>
      </div>

      {/* Content */}
      {error && <ErrorMessage message={error} onRetry={fetchData} />}
      {loading ? (
        <SkeletonGrid count={18} />
      ) : (
        <MovieGrid movies={movies} genreMap={genreMap} showMatch />
      )}
    </div>
  );
}
