import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getGenres } from "../services/api";
import { defaultPreferences, getPreferences, getWishlist, savePreferences } from "../utils/storage";

const languages = [
  ["all", "Any language"],
  ["en", "English"],
  ["hi", "Hindi"],
  ["ko", "Korean"],
  ["ja", "Japanese"],
  ["ta", "Tamil"],
  ["te", "Telugu"],
];

const industries = [
  ["all", "All cinema"],
  ["hollywood", "Hollywood"],
  ["bollywood", "Bollywood"],
  ["korean", "Korean"],
  ["japanese", "Japanese"],
];

export default function ProfilePage() {
  const [preferences, setPreferences] = useState(getPreferences());
  const [wishlist, setWishlist] = useState(getWishlist());
  const [genres, setGenres] = useState({});
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getGenres().then(setGenres).catch(() => {});

    const refreshLocalState = () => {
      setPreferences(getPreferences());
      setWishlist(getWishlist());
    };

    window.addEventListener("movers.preferences:changed", refreshLocalState);
    window.addEventListener("movers.wishlist:changed", refreshLocalState);
    return () => {
      window.removeEventListener("movers.preferences:changed", refreshLocalState);
      window.removeEventListener("movers.wishlist:changed", refreshLocalState);
    };
  }, []);

  const preferenceSummary = useMemo(() => {
    return [preferences.industry, preferences.genre, preferences.language]
      .filter((value) => value && value !== "all")
      .join(" / ") || "All cinema / any genre / any language";
  }, [preferences]);

  const update = (key, value) => {
    setPreferences((current) => ({ ...current, [key]: value }));
    setSaved(false);
  };

  const save = () => {
    setPreferences(savePreferences(preferences));
    setSaved(true);
  };

  const reset = () => {
    setPreferences(savePreferences(defaultPreferences));
    setSaved(true);
  };

  return (
    <div className="px-6 sm:px-8 md:px-16 py-8 sm:py-12 w-full max-w-[1000px] mx-auto">
      <div className="flex flex-col sm:flex-row gap-6 items-start sm:items-center mb-10">
        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-red-600/50 to-purple-700/50 border border-white/20" />
        <div>
          <h1 className="text-h1 text-white mb-2">MovieRS Profile</h1>
          <p className="text-gray-400">Your local cinema profile, preferences, and saved watchlist.</p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-5">
        <Link to="/wishlist" className="bg-surface-container/60 border border-white/10 rounded-xl p-6 hover:bg-white/5 transition-all">
          <span className="material-symbols-outlined text-red-500 text-3xl mb-4 block">bookmarks</span>
          <h2 className="text-white font-semibold mb-1">Wishlist</h2>
          <p className="text-gray-400 text-sm">{wishlist.length} saved movies</p>
        </Link>
        <Link to="/settings" className="bg-surface-container/60 border border-white/10 rounded-xl p-6 hover:bg-white/5 transition-all">
          <span className="material-symbols-outlined text-secondary text-3xl mb-4 block">tune</span>
          <h2 className="text-white font-semibold mb-1">Preferences</h2>
          <p className="text-gray-400 text-sm">{preferenceSummary}</p>
        </Link>
        <Link to="/trailers" className="bg-surface-container/60 border border-white/10 rounded-xl p-6 hover:bg-white/5 transition-all">
          <span className="material-symbols-outlined text-yellow-500 text-3xl mb-4 block">smart_display</span>
          <h2 className="text-white font-semibold mb-1">Trailers</h2>
          <p className="text-gray-400 text-sm">Browse trailer-ready movies</p>
        </Link>
      </div>

      <section className="mt-8 bg-surface-container/60 border border-white/10 rounded-xl p-6 sm:p-8 inner-glow-top-left">
        <div className="mb-6">
          <h2 className="text-h2 text-white mb-2">Viewing Preferences</h2>
          <p className="text-gray-400">Saved preferences now shape recommendations, high-rated movies, AI picks, and movie detail suggestions.</p>
        </div>

        <div className="grid sm:grid-cols-3 gap-5">
          <label className="flex flex-col gap-2 text-sm text-gray-300">
            Cinema
            <select value={preferences.industry} onChange={(e) => update("industry", e.target.value)} className="bg-black/40 border border-white/10 rounded-lg px-3 py-3 text-white">
              {industries.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>

          <label className="flex flex-col gap-2 text-sm text-gray-300">
            Genre
            <select value={preferences.genre} onChange={(e) => update("genre", e.target.value)} className="bg-black/40 border border-white/10 rounded-lg px-3 py-3 text-white">
              <option value="all">Any genre</option>
              {Object.values(genres).sort().map((genre) => (
                <option key={genre} value={genre.toLowerCase()}>{genre}</option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2 text-sm text-gray-300">
            Language
            <select value={preferences.language} onChange={(e) => update("language", e.target.value)} className="bg-black/40 border border-white/10 rounded-lg px-3 py-3 text-white">
              {languages.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
        </div>

        <div className="flex flex-wrap gap-3 mt-8">
          <button onClick={save} className="bg-primary-container text-white px-6 py-3 rounded-lg font-semibold hover:brightness-110 transition-all">
            Save Preferences
          </button>
          <button onClick={reset} className="bg-white/10 text-white px-6 py-3 rounded-lg border border-white/10 hover:bg-white/20 transition-all">
            Reset
          </button>
          {saved && <span className="text-green-400 text-sm self-center">Saved and applied</span>}
        </div>
      </section>
    </div>
  );
}
