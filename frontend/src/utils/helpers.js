/** TMDB image URL builder */
const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/";

export const buildPosterUrl = (path, size = "w500") =>
  path ? `${TMDB_IMAGE_BASE}${size}${path}` : "/placeholder-poster.png";

export const buildBackdropUrl = (path, size = "w1280") =>
  path ? `${TMDB_IMAGE_BASE}${size}${path}` : null;

export const formatYear = (dateStr) => {
  if (!dateStr) return "";
  return dateStr.slice(0, 4);
};

export const formatRating = (rating) => {
  if (!rating) return "N/A";
  return Number(rating).toFixed(1);
};

export const formatRuntime = (minutes) => {
  if (!minutes) return "";
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h ? `${h}h ${m}m` : `${m}m`;
};

export const genreIdsToNames = (ids, genreMap) => {
  if (!ids || !genreMap) return [];
  return ids
    .map((id) => (typeof id === "object" ? id.name || id : genreMap[id]))
    .filter(Boolean);
};
