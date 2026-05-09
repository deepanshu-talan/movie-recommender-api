import axios from "axios";
import { API_BASE } from "../utils/constants";

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

export const searchMovies = (query, page = 1) =>
  api.get("/search", { params: { q: query, page } }).then((r) => r.data.data);

export const getMovieDetail = (id) =>
  api.get(`/movie/${id}`).then((r) => r.data.data);

export const getRecommendations = (movieId, preferences = {}) =>
  api.get("/recommend", { params: { movie_id: movieId, ...preferences } }).then((r) => r.data.data);

export const getMovieVideos = (id) =>
  api.get(`/movie/${id}/videos`).then((r) => r.data.data);

export const getTrending = (preferences = {}) =>
  api.get("/trending", { params: preferences }).then((r) => r.data.data);

export const getPopular = (page = 1, preferences = {}) =>
  api.get("/popular", { params: { page, ...preferences } }).then((r) => r.data.data);

export const getHighRated = (page = 1, preferences = {}) =>
  api.get("/high-rated", { params: { page, ...preferences } }).then((r) => r.data.data);

export const getGenres = () =>
  api.get("/genres").then((r) => r.data.data);

export default api;
