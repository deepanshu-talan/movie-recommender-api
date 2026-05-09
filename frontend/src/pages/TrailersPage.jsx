import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getGenres, getTrending } from "../services/api";
import { buildBackdropUrl, buildPosterUrl, genreIdsToNames } from "../utils/helpers";
import { SkeletonGrid } from "../components/ui/Skeleton";

export default function TrailersPage() {
  const [movies, setMovies] = useState([]);
  const [genreMap, setGenreMap] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getTrending(), getGenres()])
      .then(([trending, genres]) => {
        setMovies(Array.isArray(trending) ? trending : trending.results || []);
        setGenreMap(genres || {});
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="px-6 sm:px-8 md:px-16 py-8 sm:py-12 w-full max-w-[1440px] mx-auto">
      <div className="mb-8 border-b border-white/10 pb-6">
        <h1 className="text-h1 text-white mb-2">Trailers</h1>
        <p className="text-gray-400">Pick a movie and watch its official trailer when TMDB has one available.</p>
      </div>

      {loading ? (
        <SkeletonGrid count={12} />
      ) : (
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-5">
          {movies.map((movie) => {
            const genres = genreIdsToNames(movie.genres, genreMap).slice(0, 2);
            return (
              <Link key={movie.id} to={`/movie/${movie.id}/trailer`} className="relative min-h-56 rounded-xl overflow-hidden border border-white/10 bg-surface-container group">
                <img src={buildBackdropUrl(movie.backdrop_path) || buildPosterUrl(movie.poster_path)} alt={movie.title} className="absolute inset-0 w-full h-full object-cover opacity-50 group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent" />
                <div className="relative z-10 h-full p-5 flex flex-col justify-end">
                  <span className="material-symbols-outlined text-red-500 text-5xl mb-auto">play_circle</span>
                  <h2 className="text-white text-xl font-semibold">{movie.title}</h2>
                  <p className="text-gray-300 text-sm">{genres.join(" / ")}</p>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
