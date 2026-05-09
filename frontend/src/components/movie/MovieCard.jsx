import { memo, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { buildPosterUrl, formatYear, formatRating, genreIdsToNames } from "../../utils/helpers";
import { isWishlisted, toggleWishlist } from "../../utils/storage";

function MovieCard({ movie, genreMap, showMatch }) {
  const posterUrl = buildPosterUrl(movie.poster_path, "w342");
  const year = formatYear(movie.release_date || movie.year);
  const rating = formatRating(movie.vote_average);
  const genres = genreIdsToNames(movie.genres, genreMap).slice(0, 2);
  const [saved, setSaved] = useState(isWishlisted(movie.id));

  useEffect(() => {
    const refresh = () => setSaved(isWishlisted(movie.id));
    window.addEventListener("movers.wishlist:changed", refresh);
    return () => window.removeEventListener("movers.wishlist:changed", refresh);
  }, [movie.id]);

  return (
    <Link
      to={`/movie/${movie.id}`}
      id={`movie-card-${movie.id}`}
      className="group relative rounded-xl overflow-hidden bg-surface-container aspect-[2/3] border border-white/5 hover:border-white/20 transition-all duration-300 hover:scale-105 hover:z-10 shadow-lg hover:shadow-[0_20px_40px_rgba(0,0,0,0.6)] cursor-pointer block"
    >
      <button
        type="button"
        aria-label={saved ? "Remove from wishlist" : "Add to wishlist"}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          toggleWishlist(movie);
          setSaved(isWishlisted(movie.id));
        }}
        className={`absolute top-2 right-2 z-20 w-9 h-9 rounded-full border border-white/15 backdrop-blur-md flex items-center justify-center transition-colors ${
          saved ? "bg-red-600 text-white" : "bg-black/50 text-white hover:bg-red-600"
        }`}
      >
        <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: saved ? "'FILL' 1" : "'FILL' 0" }}>
          favorite
        </span>
      </button>
      <img
        alt={movie.title}
        src={posterUrl}
        loading="lazy"
        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        onError={(e) => {
          e.target.src = "/placeholder-poster.png";
        }}
      />

      {/* Hover overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
        {/* Match badge + rating */}
        <div className="flex items-center justify-between mb-2">
          {showMatch && movie.match_percentage && (
            <span className="bg-secondary-container/80 text-white px-2 py-0.5 rounded-full text-xs font-bold shadow-md backdrop-blur-sm">
              {Math.round(movie.match_percentage)}% Match
            </span>
          )}
          <div className="flex items-center text-yellow-500 text-sm gap-1">
            <span
              className="material-symbols-outlined text-sm"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              star
            </span>
            <span className="font-bold">{rating}</span>
          </div>
        </div>

        <h3 className="font-semibold text-white text-sm truncate">{movie.title}</h3>

        <div className="flex items-center gap-2 mt-1">
          {year && <span className="text-gray-400 text-xs">{year}</span>}
          {genres.length > 0 && (
            <div className="flex gap-1">
              {genres.map((g) => (
                <span
                  key={g}
                  className="bg-surface-variant/80 text-gray-200 text-xs px-2 py-0.5 rounded"
                >
                  {g}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}

export default memo(MovieCard);
