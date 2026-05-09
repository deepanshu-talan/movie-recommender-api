import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getMovieDetail, getMovieVideos } from "../services/api";
import { buildBackdropUrl } from "../utils/helpers";
import { ErrorMessage, Spinner } from "../components/ui/Skeleton";

export default function TrailerPage() {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [videos, setVideos] = useState([]);
  const [fallbackUrl, setFallbackUrl] = useState("");
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [movieData, videoData] = await Promise.all([
        getMovieDetail(id),
        getMovieVideos(id),
      ]);
      const results = videoData.results || [];
      setMovie(movieData);
      setVideos(results);
      setFallbackUrl(videoData.fallback_url || "");
      setSelected(results[0] || null);
    } catch (err) {
      setError(err.message || "Failed to load trailer");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    window.scrollTo(0, 0);
    fetchData();
  }, [id]);

  if (loading) return <Spinner size="lg" />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  const backdrop = buildBackdropUrl(movie?.backdrop_path);

  return (
    <div className="px-6 sm:px-8 md:px-16 py-8 sm:py-12 w-full max-w-[1200px] mx-auto">
      <div className="mb-6">
        <Link to={`/movie/${id}`} className="text-gray-400 hover:text-white inline-flex items-center gap-2 mb-4">
          <span className="material-symbols-outlined">arrow_back</span>
          Back to movie
        </Link>
        <h1 className="text-h1 text-white">{movie?.title || "Trailer"}</h1>
      </div>

      <div className="rounded-xl overflow-hidden border border-white/10 bg-black aspect-video">
        {selected ? (
          <iframe
            title={selected.name}
            src={selected.embed_url}
            className="w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
          />
        ) : (
          <div className="relative w-full h-full flex flex-col items-center justify-center text-center px-6">
            {backdrop && <img src={backdrop} alt="" className="absolute inset-0 w-full h-full object-cover opacity-20" />}
            <div className="relative z-10">
              <span className="material-symbols-outlined text-6xl text-gray-500 mb-4">smart_display</span>
              <p className="text-white font-semibold mb-2">No embedded trailer found</p>
              {fallbackUrl && (
                <a href={fallbackUrl} target="_blank" rel="noreferrer" className="text-red-400 hover:text-red-300">
                  Search YouTube for the official trailer
                </a>
              )}
            </div>
          </div>
        )}
      </div>

      {videos.length > 1 && (
        <div className="mt-6 grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {videos.map((video) => (
            <button
              key={video.id}
              onClick={() => setSelected(video)}
              className={`text-left p-4 rounded-lg border transition-colors ${
                selected?.id === video.id ? "border-red-600 bg-red-600/10" : "border-white/10 bg-white/5 hover:bg-white/10"
              }`}
            >
              <p className="text-white font-medium line-clamp-1">{video.name}</p>
              <p className="text-gray-500 text-sm">{video.type}{video.official ? " / Official" : ""}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
