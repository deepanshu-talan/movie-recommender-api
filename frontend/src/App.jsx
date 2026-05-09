import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout";
import HomePage from "./pages/HomePage";
import SearchPage from "./pages/SearchPage";
import MovieDetailPage from "./pages/MovieDetailPage";
import BrowsePage from "./pages/BrowsePage";
import SettingsPage from "./pages/SettingsPage";
import ProfilePage from "./pages/ProfilePage";
import WishlistPage from "./pages/WishlistPage";
import TrailerPage from "./pages/TrailerPage";
import TrailersPage from "./pages/TrailersPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="movie/:id" element={<MovieDetailPage />} />
          <Route path="movie/:id/trailer" element={<TrailerPage />} />
          <Route path="recommendations" element={<BrowsePage type="ai" />} />
          <Route path="trending" element={<BrowsePage type="trending" />} />
          <Route path="popular" element={<BrowsePage type="popular" />} />
          <Route path="high-rated" element={<BrowsePage type="highRated" />} />
          <Route path="trailers" element={<TrailersPage />} />
          <Route path="wishlist" element={<WishlistPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route
            path="*"
            element={
              <div className="flex flex-col items-center justify-center py-32 gap-4">
                <span className="material-symbols-outlined text-6xl text-gray-600">error</span>
                <h1 className="text-h1 text-white">404 — Page Not Found</h1>
                <p className="text-gray-400">The page you're looking for doesn't exist.</p>
              </div>
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
