const PREF_KEY = "movers.preferences";
const WISHLIST_KEY = "movers.wishlist";

export const defaultPreferences = {
  industry: "all",
  genre: "all",
  language: "all",
};

const readJson = (key, fallback) => {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
};

const writeJson = (key, value) => {
  localStorage.setItem(key, JSON.stringify(value));
  window.dispatchEvent(new Event(`${key}:changed`));
};

export const getPreferences = () => ({
  ...defaultPreferences,
  ...readJson(PREF_KEY, defaultPreferences),
});

export const savePreferences = (preferences) => {
  const next = { ...defaultPreferences, ...preferences };
  writeJson(PREF_KEY, next);
  return next;
};

export const getWishlist = () => readJson(WISHLIST_KEY, []);

export const isWishlisted = (movieId) =>
  getWishlist().some((movie) => String(movie.id) === String(movieId));

export const toggleWishlist = (movie) => {
  const current = getWishlist();
  const exists = current.some((item) => String(item.id) === String(movie.id));
  const next = exists
    ? current.filter((item) => String(item.id) !== String(movie.id))
    : [{ ...movie, saved_at: new Date().toISOString() }, ...current];
  writeJson(WISHLIST_KEY, next);
  return next;
};

export const clearWishlist = () => writeJson(WISHLIST_KEY, []);

export const matchesPreferences = (movie, preferences = getPreferences(), genreMap = {}) => {
  const industry = preferences.industry || "all";
  const language = preferences.language || "all";
  const genre = preferences.genre || "all";
  const originalLanguage = movie.original_language || "";
  const names = (movie.genres || []).map((g) =>
    typeof g === "object" ? g.name : genreMap[g] || String(g)
  );

  if (industry === "hollywood" && originalLanguage !== "en") return false;
  if (industry === "bollywood" && originalLanguage !== "hi") return false;
  if (industry === "korean" && originalLanguage !== "ko") return false;
  if (industry === "japanese" && originalLanguage !== "ja") return false;
  if (language !== "all" && originalLanguage !== language) return false;
  if (genre !== "all" && !names.some((name) => name.toLowerCase() === genre)) return false;
  return true;
};
