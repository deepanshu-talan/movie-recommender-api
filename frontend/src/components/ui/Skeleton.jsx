/** Skeleton loading components */
export function SkeletonCard() {
  return (
    <div className="rounded-xl overflow-hidden aspect-[2/3] skeleton" />
  );
}

export function SkeletonGrid({ count = 12 }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 sm:gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

export function SkeletonHero() {
  return (
    <div className="relative w-full h-[520px] sm:h-[620px] lg:h-[716px] min-h-[400px] skeleton">
      <div className="absolute bottom-24 left-16 flex flex-col gap-4 w-1/2">
        <div className="h-6 w-32 skeleton rounded-full" />
        <div className="h-12 w-3/4 skeleton rounded" />
        <div className="h-20 w-full skeleton rounded" />
      </div>
    </div>
  );
}

export function SkeletonText({ width = "w-full", height = "h-4" }) {
  return <div className={`${width} ${height} skeleton rounded`} />;
}

export function Spinner({ size = "md" }) {
  const sizeClass = size === "sm" ? "w-6 h-6" : size === "lg" ? "w-12 h-12" : "w-8 h-8";
  return (
    <div className="flex justify-center py-8">
      <div className={`${sizeClass} border-2 border-red-600 border-t-transparent rounded-full animate-spin`} />
    </div>
  );
}

export function ErrorMessage({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <span className="material-symbols-outlined text-4xl text-error">error</span>
      <p className="text-gray-400 text-center">{message || "Something went wrong"}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="bg-primary-container text-white px-6 py-2 rounded-lg font-semibold hover:brightness-110 transition-all text-sm"
        >
          Try Again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, subtitle, children }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <span className="material-symbols-outlined text-6xl text-gray-600">movie_filter</span>
      <h2 className="text-h2 text-white">{title || "No Results Found"}</h2>
      {subtitle && <p className="text-gray-400 text-center max-w-md">{subtitle}</p>}
      {children}
    </div>
  );
}
