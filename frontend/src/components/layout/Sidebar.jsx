import { NavLink } from "react-router-dom";

const navItems = [
  { icon: "explore", label: "Discover", to: "/" },
  { icon: "trending_up", label: "Trending", to: "/trending" },
  { icon: "star", label: "High Rated", to: "/high-rated" },
  { icon: "auto_awesome", label: "AI Picks", to: "/recommendations" },
  { icon: "bookmarks", label: "My List", to: "/wishlist" },
];

export default function Sidebar() {
  return (
    <aside className="hidden xl:flex fixed left-0 top-16 h-[calc(100vh-64px)] w-64 border-r border-white/10 bg-black/40 backdrop-blur-2xl inner-glow-top-left flex-col py-6 z-40 text-sm font-medium">
      <div className="px-6 mb-6">
        <h3 className="text-white font-semibold mb-1">Library</h3>
        <p className="text-gray-500 text-xs">Your curated cinema</p>
      </div>

      <nav className="flex-1 flex flex-col gap-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              isActive
                ? "bg-gradient-to-r from-red-600/20 to-transparent text-white border-l-4 border-red-600 px-4 py-3 flex items-center gap-4 transition-colors"
                : "text-gray-500 hover:text-gray-200 px-4 py-3 hover:bg-white/5 transition-colors flex items-center gap-4"
            }
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto px-4 flex flex-col gap-2">
        <div className="flex flex-col gap-1 border-t border-white/5 pt-4">
          <NavLink to="/settings" className="text-gray-500 hover:text-gray-200 px-4 py-2 hover:bg-white/5 transition-colors rounded-lg flex items-center gap-4 text-xs">
            <span className="material-symbols-outlined text-lg">settings</span>
            Settings
          </NavLink>
          <a href="#" className="text-gray-500 hover:text-gray-200 px-4 py-2 hover:bg-white/5 transition-colors rounded-lg flex items-center gap-4 text-xs">
            <span className="material-symbols-outlined text-lg">help_outline</span>
            Help
          </a>
        </div>
      </div>
    </aside>
  );
}
