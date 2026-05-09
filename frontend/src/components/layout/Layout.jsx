import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import Footer from "./Footer";

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <Sidebar />
      <main className="flex-1 w-full xl:pl-64 pt-16 flex flex-col relative z-10">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
