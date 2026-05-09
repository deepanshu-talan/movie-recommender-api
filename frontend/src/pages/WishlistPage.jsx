import { useEffect, useState } from "react";
import { getGenres } from "../services/api";
import MovieGrid from "../components/movie/MovieGrid";
import { EmptyState } from "../components/ui/Skeleton";
import { clearWishlist, getWishlist } from "../utils/storage";

export default function WishlistPage() {
  const [wishlist, setWishlist] = useState(getWishlist());
  const [genreMap, setGenreMap] = useState({});

  useEffect(() => {
    getGenres().then(setGenreMap).catch(() => {});
    const refresh = () => setWishlist(getWishlist());
    window.addEventListener("movers.wishlist:changed", refresh);
    return () => window.removeEventListener("movers.wishlist:changed", refresh);
  }, []);

  return (
    <div className="px-6 sm:px-8 md:px-16 py-8 sm:py-12 w-full max-w-[1440px] mx-auto">
      <div className="flex items-end justify-between gap-4 mb-8 border-b border-white/10 pb-6">
        <div>
          <h1 className="text-h1 text-white mb-2">My Wishlist</h1>
          <p className="text-gray-400">{wishlist.length} saved movie{wishlist.length === 1 ? "" : "s"}</p>
        </div>
        {wishlist.length > 0 && (
          <button onClick={() => clearWishlist()} className="bg-white/10 text-white px-4 py-2 rounded-lg border border-white/10 hover:bg-white/20">
            Clear List
          </button>
        )}
      </div>

      {wishlist.length > 0 ? (
        <MovieGrid movies={wishlist} genreMap={genreMap} />
      ) : (
        <EmptyState title="Your wishlist is empty" subtitle="Tap the heart on any movie card or detail page to save it here." />
      )}
    </div>
  );
}
