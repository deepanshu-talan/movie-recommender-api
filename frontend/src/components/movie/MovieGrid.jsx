import MovieCard from "./MovieCard";

export default function MovieGrid({ movies, genreMap, showMatch = false }) {
  if (!movies || movies.length === 0) return null;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 sm:gap-6">
      {movies.map((movie) => (
        <MovieCard
          key={movie.id}
          movie={movie}
          genreMap={genreMap}
          showMatch={showMatch}
        />
      ))}
    </div>
  );
}
