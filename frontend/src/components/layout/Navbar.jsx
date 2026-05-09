import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim().length >= 2) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <header className="fixed top-0 w-full z-50 border-b border-white/10 bg-black/60 backdrop-blur-xl shadow-2xl">
      <div className="flex justify-between items-center px-4 sm:px-8 h-16 max-w-[1440px] mx-auto w-full">
        {/* Logo + Nav Links */}
        <div className="flex items-center gap-8">
          <Link
            to="/"
            className="text-2xl font-black tracking-tighter text-red-600 uppercase"
          >
            MovieRS
          </Link>
          <nav className="hidden md:flex items-center gap-1">
            <Link
              to="/"
              className="text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-300 px-3 py-2 rounded-lg text-sm font-medium"
            >
              Movies
            </Link>
            <Link
              to="/recommendations"
              className="text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-300 px-3 py-2 rounded-lg text-sm font-medium"
            >
              AI Picks
            </Link>
            <Link
              to="/trailers"
              className="text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-300 px-3 py-2 rounded-lg text-sm font-medium"
            >
              Trailers
            </Link>
          </nav>
        </div>

        {/* Search + Actions */}
        <div className="flex items-center gap-4">
          <form onSubmit={handleSearch} className="hidden sm:flex relative group items-center">
            <span className="material-symbols-outlined absolute left-3 text-gray-500 group-focus-within:text-red-500 transition-colors pointer-events-none">
              search
            </span>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search movies..."
              className="bg-white/5 border border-white/10 rounded-full py-2 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-red-600 focus:bg-black/80 transition-all duration-300 w-56 focus:w-72 backdrop-blur-md inner-glow-top-left"
            />
          </form>

          <button className="text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-300 p-2 rounded-full relative">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-600 rounded-full"></span>
          </button>

          <Link to="/profile" className="w-8 h-8 rounded-full overflow-hidden border border-white/20 bg-surface-container-high block hover:border-red-600 transition-colors">
            <div className="w-full h-full bg-gradient-to-br from-red-600/40 to-purple-600/40" />
          </Link>
        </div>
      </div>
    </header>
  );
}
