import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { searchMovies, getGenres } from "../services/api";
import MovieGrid from "../components/movie/MovieGrid";
import { SkeletonGrid, EmptyState, ErrorMessage, Spinner } from "../components/ui/Skeleton";
import { useDebounce } from "../hooks/useDebounce";

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlQuery = searchParams.get("q") || "";

  const [query, setQuery] = useState(urlQuery);
  const [results, setResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [page, setPage] = useState(1);
  const [genreMap, setGenreMap] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const debouncedQuery = useDebounce(query, 300);

  // Load genres once
  useEffect(() => {
    getGenres().then(setGenreMap).catch(() => {});
  }, []);

  // Search when debounced query changes
  useEffect(() => {
    if (debouncedQuery.trim().length < 2) {
      setResults([]);
      setTotalResults(0);
      return;
    }

    setSearchParams({ q: debouncedQuery });
    setLoading(true);
    setError(null);
    setPage(1);

    searchMovies(debouncedQuery, 1)
      .then((data) => {
        setResults(data.results || []);
        setTotalResults(data.total_results || 0);
      })
      .catch((err) => setError(err.message || "Search failed"))
      .finally(() => setLoading(false));
  }, [debouncedQuery]);

  // Load more (pagination)
  const loadMore = async () => {
    const nextPage = page + 1;
    setPage(nextPage);
    try {
      const data = await searchMovies(debouncedQuery, nextPage);
      setResults((prev) => [...prev, ...(data.results || [])]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="px-6 sm:px-8 md:px-16 py-8 sm:py-12 w-full max-w-[1440px] mx-auto">
      {/* Search Header */}
      <div className="mb-8 border-b border-white/10 pb-6">
        <h1 className="text-h1 text-white mb-4">Search Movies</h1>

        {/* Search Input */}
        <div className="relative max-w-xl">
          <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
            search
          </span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by title..."
            className="w-full bg-surface-container/50 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-500 focus:outline-none focus:border-red-500 focus:bg-surface-container transition-all text-body-md"
          />
        </div>

        {totalResults > 0 && !loading && (
          <p className="text-gray-400 text-sm mt-4">
            Showing {results.length} of {totalResults} results for "{debouncedQuery}"
          </p>
        )}
      </div>

      {/* Results */}
      {error && <ErrorMessage message={error} onRetry={() => setQuery(query)} />}

      {loading ? (
        <SkeletonGrid count={12} />
      ) : results.length > 0 ? (
        <>
          <MovieGrid movies={results} genreMap={genreMap} />
          {results.length < totalResults && (
            <div className="mt-12 flex justify-center">
              <button
                onClick={loadMore}
                className="bg-surface-container-high text-white px-8 py-3 rounded-xl font-semibold hover:bg-surface-bright transition-colors border border-white/10"
              >
                Load More
              </button>
            </div>
          )}
        </>
      ) : debouncedQuery.length >= 2 && !loading ? (
        <EmptyState
          title="No Results Found"
          subtitle={`We couldn't find any movies matching "${debouncedQuery}". Try a different search term.`}
        />
      ) : (
        <EmptyState
          title="Start Searching"
          subtitle="Type at least 2 characters to search for movies."
        >
          <span className="material-symbols-outlined text-6xl text-gray-700 -mt-4">search</span>
        </EmptyState>
      )}
    </div>
  );
}
