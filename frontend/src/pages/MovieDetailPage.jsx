import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getMovieDetail, getRecommendations, getGenres } from "../services/api";
import { buildPosterUrl, buildBackdropUrl, formatRating, formatRuntime } from "../utils/helpers";
import { getPreferences, isWishlisted, toggleWishlist } from "../utils/storage";
import MovieGrid from "../components/movie/MovieGrid";
import { Spinner, ErrorMessage, SkeletonGrid } from "../components/ui/Skeleton";

export default function MovieDetailPage() {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [recs, setRecs] = useState([]);
  const [genreMap, setGenreMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [recsLoading, setRecsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(false);

  const fetchMovie = async () => {
    setLoading(true);
    setError(null);
    try {
      const [movieData, genresData] = await Promise.all([
        getMovieDetail(id),
        getGenres(),
      ]);
      setMovie(movieData);
      setSaved(isWishlisted(movieData.id));
      setGenreMap(genresData || {});

      // Fetch recommendations
      setRecsLoading(true);
      const recsData = await getRecommendations(id, getPreferences());
      setRecs(Array.isArray(recsData) ? recsData : []);
    } catch (err) {
      setError(err.message || "Failed to load movie");
    } finally {
      setLoading(false);
      setRecsLoading(false);
    }
  };

  useEffect(() => {
    window.scrollTo(0, 0);
    fetchMovie();

    const refreshForPreferences = () => {
      setRecsLoading(true);
      getRecommendations(id, getPreferences())
        .then((recsData) => setRecs(Array.isArray(recsData) ? recsData : []))
        .catch(() => setRecs([]))
        .finally(() => setRecsLoading(false));
    };

    window.addEventListener("movers.preferences:changed", refreshForPreferences);
    return () => window.removeEventListener("movers.preferences:changed", refreshForPreferences);
  }, [id]);

  if (loading) return <Spinner size="lg" />;
  if (error) return <ErrorMessage message={error} onRetry={fetchMovie} />;
  if (!movie) return <ErrorMessage message="Movie not found" />;

  const posterUrl = buildPosterUrl(movie.poster_path);
  const backdropUrl = buildBackdropUrl(movie.backdrop_path);
  const rating = formatRating(movie.vote_average);
  const runtime = formatRuntime(movie.runtime);
  const year = movie.release_date?.slice(0, 4) || movie.year || "";
  const genres = (movie.genres || []).map((g) =>
    typeof g === "object" ? g.name || g : genreMap[g] || g
  );
  const toggleSaved = () => {
    toggleWishlist(movie);
    setSaved(isWishlisted(movie.id));
  };

  return (
    <>
      {/* Backdrop Hero */}
      <section className="relative w-full h-[400px] sm:h-[500px] overflow-hidden">
        <div className="absolute inset-0">
          {backdropUrl ? (
            <img src={backdropUrl} alt={movie.title} className="w-full h-full object-cover opacity-40" />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-surface-container-high to-background" />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent" />
        </div>
      </section>

      {/* Movie Info */}
      <div className="px-6 sm:px-8 md:px-16 -mt-48 sm:-mt-64 relative z-10 w-full max-w-[1440px] mx-auto pb-24">
        <div className="flex flex-col md:flex-row gap-8 mb-16">
          {/* Poster */}
          <div className="w-48 sm:w-64 flex-shrink-0 mx-auto md:mx-0">
            <img
              src={posterUrl}
              alt={movie.title}
              className="w-full rounded-xl shadow-[0_20px_40px_rgba(0,0,0,0.6)] border border-white/10"
              onError={(e) => { e.target.src = "/placeholder-poster.png"; }}
            />
          </div>

          {/* Details */}
          <div className="flex-1 flex flex-col gap-4">
            <h1 className="text-display text-white">{movie.title}</h1>

            {movie.tagline && (
              <p className="text-gray-400 italic text-body-lg">"{movie.tagline}"</p>
            )}

            {/* Meta row */}
            <div className="flex items-center gap-4 flex-wrap text-sm">
              {year && <span className="text-gray-300">{year}</span>}
              {runtime && <span className="text-gray-300">{runtime}</span>}
              {rating && (
                <div className="flex items-center gap-1 bg-black/40 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 text-white font-semibold">
                  <span
                    className="material-symbols-outlined text-yellow-500 text-[16px]"
                    style={{ fontVariationSettings: "'FILL' 1" }}
                  >
                    star
                  </span>
                  {rating}
                </div>
              )}
              {movie.vote_count > 0 && (
                <span className="text-gray-500">({movie.vote_count.toLocaleString()} votes)</span>
              )}
            </div>

            {/* Genres */}
            {genres.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {genres.map((g) => (
                  <span
                    key={g}
                    className="bg-surface-variant/80 text-gray-200 text-xs px-3 py-1.5 rounded-full border border-white/5"
                  >
                    {g}
                  </span>
                ))}
              </div>
            )}

            {/* Overview */}
            {movie.overview && (
              <div className="mt-4">
                <h3 className="text-white font-semibold mb-2">Overview</h3>
                <p className="text-gray-300 text-body-md leading-relaxed">{movie.overview}</p>
              </div>
            )}

            {/* Keywords */}
            {movie.keywords && movie.keywords.length > 0 && (
              <div className="mt-4">
                <h3 className="text-white font-semibold mb-2 text-sm">Keywords</h3>
                <div className="flex flex-wrap gap-2">
                  {movie.keywords.slice(0, 10).map((kw) => (
                    <span
                      key={kw}
                      className="bg-surface-container text-gray-400 text-xs px-2 py-1 rounded border border-white/5"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div className="flex items-center gap-4 mt-6 flex-wrap">
              <Link to={`/movie/${movie.id}/trailer`} className="bg-primary-container text-white px-6 py-3 rounded-xl font-semibold hover:brightness-110 transition-all shadow-[0_0_20px_rgba(229,9,20,0.3)] flex items-center gap-2 inner-glow-top-left">
                <span className="material-symbols-outlined">play_arrow</span>
                Watch Trailer
              </Link>
              <button onClick={toggleSaved} className={`${saved ? "bg-red-600" : "bg-white/10"} text-white px-6 py-3 rounded-xl font-semibold hover:bg-red-600 transition-all border border-white/20 flex items-center gap-2`}>
                <span className="material-symbols-outlined">bookmark_add</span>
                {saved ? "Saved" : "Add to Watchlist"}
              </button>
              <button className="bg-white/10 text-white px-6 py-3 rounded-xl font-semibold hover:bg-white/20 transition-all border border-white/20 flex items-center gap-2">
                <span className="material-symbols-outlined">share</span>
                Share
              </button>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <section>
          <h2 className="text-h2 text-white mb-6">You Might Also Like</h2>
          {recsLoading ? (
            <SkeletonGrid count={6} />
          ) : recs.length > 0 ? (
            <MovieGrid movies={recs} genreMap={genreMap} showMatch />
          ) : (
            <p className="text-gray-500">No recommendations available for this movie.</p>
          )}
        </section>
      </div>
    </>
  );
}
