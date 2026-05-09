import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getTrending, getPopular, getGenres } from "../services/api";
import HeroSection from "../components/movie/HeroSection";
import MovieGrid from "../components/movie/MovieGrid";
import { SkeletonHero, SkeletonGrid, ErrorMessage } from "../components/ui/Skeleton";
import { getPreferences } from "../utils/storage";

const byTrending = (a, b) => {
  const aDate = Date.parse(a.release_date || "") || 0;
  const bDate = Date.parse(b.release_date || "") || 0;
  if (bDate !== aDate) return bDate - aDate;
  return (b.popularity || 0) - (a.popularity || 0);
};

const byPopular = (a, b) =>
  (b.popularity || 0) - (a.popularity || 0) ||
  (b.vote_count || 0) - (a.vote_count || 0);

export default function HomePage() {
  const [trending, setTrending] = useState([]);
  const [popular, setPopular] = useState([]);
  const [genreMap, setGenreMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const preferences = getPreferences();
      const [trendingData, popularData, genresData] = await Promise.all([
        getTrending(preferences),
        getPopular(1, preferences),
        getGenres(),
      ]);
      const trendingResults = Array.isArray(trendingData) ? trendingData : trendingData.results || [];
      setTrending([...trendingResults].sort(byTrending));
      setPopular([...(popularData.results || [])].sort(byPopular));
      setGenreMap(genresData || {});
    } catch (err) {
      setError(err.message || "Failed to load content");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const refresh = () => fetchData();
    window.addEventListener("movers.preferences:changed", refresh);
    return () => window.removeEventListener("movers.preferences:changed", refresh);
  }, []);

  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  const heroMovie = trending[0] || null;

  return (
    <>
      {/* Hero */}
      {loading ? <SkeletonHero /> : <HeroSection movie={heroMovie} />}

      {/* CTA Block */}
      <section className="relative -mt-12 z-20 px-6 sm:px-8 md:px-16 w-full max-w-[1440px] mx-auto mb-12 sm:mb-16">
        <div className="bg-surface-container-high/80 backdrop-blur-2xl rounded-2xl p-6 sm:p-8 border border-white/10 shadow-[0_20px_40px_rgba(0,0,0,0.5)] inner-glow-top-left flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex-1">
            <h2 className="text-h2 text-white mb-2">Not sure what to watch?</h2>
            <p className="text-gray-400 text-body-md">
              Let our AI analyze your taste and find the perfect movie for tonight.
            </p>
          </div>
          <Link
            to="/recommendations"
            className="bg-gradient-to-r from-secondary-container to-secondary text-white px-8 py-4 rounded-xl font-semibold hover:scale-105 transition-all duration-300 shadow-[0_0_30px_rgba(119,1,208,0.4)] flex items-center gap-3 inner-glow-top-left w-full md:w-auto justify-center"
          >
            <span className="material-symbols-outlined">auto_awesome</span>
            Get Recommendations
          </Link>
        </div>
      </section>

      {/* Content Sections */}
      <div className="px-6 sm:px-8 md:px-16 pb-24 w-full max-w-[1440px] mx-auto flex flex-col gap-12 sm:gap-16">
        {/* Trending */}
        <section>
          <div className="flex justify-between items-end mb-6">
            <h2 className="text-h2 text-white">Trending This Week</h2>
            <Link
              to="/trending"
              className="text-gray-400 hover:text-white text-sm flex items-center gap-1 transition-colors"
            >
              View All
              <span className="material-symbols-outlined text-[18px]">chevron_right</span>
            </Link>
          </div>
          {loading ? (
            <SkeletonGrid count={6} />
          ) : trending.length === 0 ? (
            <p className="text-gray-500">No trending movies match your current preferences.</p>
          ) : (
            <MovieGrid movies={trending.slice(0, 12)} genreMap={genreMap} />
          )}
        </section>

        {/* Popular */}
        <section>
          <div className="flex justify-between items-end mb-6">
            <h2 className="text-h2 text-white">Popular Movies</h2>
            <Link
              to="/popular"
              className="text-gray-400 hover:text-white text-sm flex items-center gap-1 transition-colors"
            >
              View All
              <span className="material-symbols-outlined text-[18px]">chevron_right</span>
            </Link>
          </div>
          {loading ? (
            <SkeletonGrid count={6} />
          ) : popular.length === 0 ? (
            <p className="text-gray-500">No popular movies match your current preferences.</p>
          ) : (
            <MovieGrid movies={popular.slice(0, 12)} genreMap={genreMap} />
          )}
        </section>

        {/* Categories Bento Grid */}
        <section>
          <h2 className="text-h2 text-white mb-6">Explore Categories</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { name: "Action", gradient: "from-orange-900/60 to-red-900/60" },
              { name: "Science Fiction", gradient: "from-purple-900/60 to-blue-900/60", span: "md:col-span-2" },
              { name: "Drama", gradient: "from-emerald-900/60 to-teal-900/60", span: "md:col-span-2" },
              { name: "Thriller", gradient: "from-gray-900/60 to-slate-900/60" },
            ].map((cat) => (
              <Link
                key={cat.name}
                to={`/search?q=${encodeURIComponent(cat.name)}`}
                className={`group relative h-40 sm:h-48 rounded-2xl overflow-hidden cursor-pointer ${cat.span || ""}`}
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${cat.gradient} group-hover:opacity-80 transition-opacity duration-300`} />
                <div className="absolute inset-0 p-6 flex flex-col justify-end border border-white/10 rounded-2xl inner-glow-top-left">
                  <h3 className="text-white text-h2 drop-shadow-lg">{cat.name}</h3>
                  <p className="text-gray-300 text-sm mt-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300 transform translate-y-2 group-hover:translate-y-0">
                    Explore the best {cat.name.toLowerCase()} movies
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}
