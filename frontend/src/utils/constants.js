/** API base URL — uses Vite proxy in dev */
export const API_BASE = import.meta.env.VITE_API_URL || "";

/** TMDB image base */
export const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/";

/** Debounce delay for search input (ms) */
export const SEARCH_DEBOUNCE_MS = 300;

/** Max recommendation count */
export const MAX_RECOMMENDATIONS = 10;
