export default function Footer() {
  return (
    <footer className="w-full py-8 mt-auto border-t border-white/10 bg-black text-gray-600 text-xs relative z-50">
      <div className="max-w-[1440px] mx-auto px-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="text-sm font-bold text-gray-400">
          © {new Date().getFullYear()} MovieRS AI. All rights reserved.
        </div>
        <div className="flex gap-6">
          <a href="#" className="text-gray-500 hover:text-red-500 transition-colors">
            Privacy Policy
          </a>
          <a href="#" className="text-gray-500 hover:text-red-500 transition-colors">
            Terms of Service
          </a>
          <a href="#" className="text-gray-500 hover:text-red-500 transition-colors">
            Contact
          </a>
        </div>
      </div>
    </footer>
  );
}
