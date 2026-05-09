import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { buildBackdropUrl } from "../../utils/helpers";
import { isWishlisted, toggleWishlist } from "../../utils/storage";

export default function HeroSection({ movie }) {
  const backdropUrl = movie ? buildBackdropUrl(movie.backdrop_path) : null;
  const rating = movie?.vote_average ? Number(movie.vote_average).toFixed(1) : null;
  const [saved, setSaved] = useState(movie ? isWishlisted(movie.id) : false);

  useEffect(() => {
    if (movie) {
      setSaved(isWishlisted(movie.id));
    }
  }, [movie]);

  if (!movie) {
    return (
      <section className="relative w-full h-[520px] sm:h-[620px] lg:h-[716px] min-h-[400px] flex items-end pb-16 sm:pb-24 px-6 sm:px-8 md:px-16 overflow-hidden bg-gradient-to-br from-surface-container-high via-background to-black">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_25%,rgba(229,9,20,0.18),transparent_34%),radial-gradient(circle_at_78%_22%,rgba(119,1,208,0.16),transparent_30%)]" />
        <div className="relative z-10 max-w-[800px] flex flex-col gap-4 sm:gap-6">
          <span className="bg-red-600/20 text-red-500 text-label-caps px-3 py-1 rounded-full border border-red-500/30 backdrop-blur-md w-fit">
            NO MATCHES YET
          </span>
          <h1 className="text-display text-white drop-shadow-2xl">No trending movies for these preferences</h1>
          <p className="text-body-lg text-gray-300 max-w-2xl">
            Try a broader language, genre, or cinema preference to open up more matches.
          </p>
          <div className="flex items-center gap-4 mt-2 flex-wrap">
            <Link
              to="/profile"
              className="bg-primary-container text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl text-h2 font-semibold hover:scale-105 transition-transform duration-300 shadow-[0_0_30px_rgba(229,9,20,0.4)] flex items-center gap-3 inner-glow-top-left"
            >
              <span className="material-symbols-outlined">tune</span>
              Adjust Preferences
            </Link>
            <Link
              to="/trending"
              className="bg-white/10 backdrop-blur-xl text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl font-semibold hover:bg-white/20 transition-all duration-300 border border-white/20 flex items-center gap-3 inner-glow-top-left"
            >
              <span className="material-symbols-outlined">explore</span>
              Browse Trending
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="relative w-full h-[520px] sm:h-[620px] lg:h-[716px] min-h-[400px] flex items-end pb-16 sm:pb-24 px-6 sm:px-8 md:px-16 overflow-hidden">
      {/* Background Image */}
      <div className="absolute inset-0 z-0">
        {backdropUrl ? (
          <img
            alt={movie.title}
            src={backdropUrl}
            className="w-full h-full object-cover opacity-60"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-surface-container-high to-background" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/50 to-transparent" />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-[800px] flex flex-col gap-4 sm:gap-6">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="bg-red-600/20 text-red-500 text-label-caps px-3 py-1 rounded-full border border-red-500/30 backdrop-blur-md">
            TRENDING NOW
          </span>
          {rating && (
            <div className="flex items-center gap-1 bg-black/40 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 text-sm font-semibold text-white">
              <span
                className="material-symbols-outlined text-[16px] text-yellow-500"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                star
              </span>
              {rating}
            </div>
          )}
        </div>

        <h1 className="text-display text-white drop-shadow-2xl">{movie.title}</h1>

        {movie.overview && (
          <p className="text-body-lg text-gray-300 max-w-2xl line-clamp-3">
            {movie.overview}
          </p>
        )}

        <div className="flex items-center gap-4 mt-2 flex-wrap">
          <Link
            to={`/movie/${movie.id}/trailer`}
            className="bg-primary-container text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl text-h2 font-semibold hover:scale-105 transition-transform duration-300 shadow-[0_0_30px_rgba(229,9,20,0.4)] flex items-center gap-3 inner-glow-top-left"
          >
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
              play_arrow
            </span>
            Watch Trailer
          </Link>
          <Link
            to={`/movie/${movie.id}`}
            className="bg-white/10 backdrop-blur-xl text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl font-semibold hover:bg-white/20 transition-all duration-300 border border-white/20 flex items-center gap-3 inner-glow-top-left"
          >
            <span className="material-symbols-outlined">info</span>
            Details
          </Link>
          <button
            onClick={() => {
              toggleWishlist(movie);
              setSaved(isWishlisted(movie.id));
            }}
            className={`${saved ? "bg-red-600" : "bg-white/10"} backdrop-blur-xl text-white px-6 sm:px-8 py-3 sm:py-4 rounded-xl font-semibold hover:bg-red-600 transition-all duration-300 border border-white/20 flex items-center gap-3 inner-glow-top-left`}
          >
            <span className="material-symbols-outlined">{saved ? "bookmark_added" : "add"}</span>
            {saved ? "Saved" : "My List"}
          </button>
        </div>
      </div>
    </section>
  );
}
