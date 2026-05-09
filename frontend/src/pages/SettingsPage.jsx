import { useEffect, useState } from "react";
import { getGenres } from "../services/api";
import { defaultPreferences, getPreferences, savePreferences } from "../utils/storage";

const languages = [
  ["all", "Any language"],
  ["en", "English"],
  ["hi", "Hindi"],
  ["ko", "Korean"],
  ["ja", "Japanese"],
  ["ta", "Tamil"],
  ["te", "Telugu"],
];

const industries = [
  ["all", "All cinema"],
  ["hollywood", "Hollywood"],
  ["bollywood", "Bollywood"],
  ["korean", "Korean"],
  ["japanese", "Japanese"],
];

export default function SettingsPage() {
  const [preferences, setPreferences] = useState(getPreferences());
  const [genres, setGenres] = useState({});
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getGenres().then(setGenres).catch(() => {});
  }, []);

  const update = (key, value) => {
    setPreferences((current) => ({ ...current, [key]: value }));
    setSaved(false);
  };

  const save = () => {
    setPreferences(savePreferences(preferences));
    setSaved(true);
  };

  const reset = () => {
    setPreferences(savePreferences(defaultPreferences));
    setSaved(true);
  };

  return (
    <div className="px-6 sm:px-8 md:px-16 py-8 sm:py-12 w-full max-w-[1000px] mx-auto">
      <div className="mb-10">
        <h1 className="text-h1 text-white mb-2">Settings</h1>
        <p className="text-gray-400">Tune recommendations and high-rated picks around what you actually watch.</p>
      </div>

      <section className="bg-surface-container/60 border border-white/10 rounded-xl p-6 sm:p-8 inner-glow-top-left">
        <h2 className="text-h2 text-white mb-6">Viewing Preferences</h2>
        <div className="grid sm:grid-cols-3 gap-5">
          <label className="flex flex-col gap-2 text-sm text-gray-300">
            Cinema
            <select value={preferences.industry} onChange={(e) => update("industry", e.target.value)} className="bg-black/40 border border-white/10 rounded-lg px-3 py-3 text-white">
              {industries.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
          <label className="flex flex-col gap-2 text-sm text-gray-300">
            Genre
            <select value={preferences.genre} onChange={(e) => update("genre", e.target.value)} className="bg-black/40 border border-white/10 rounded-lg px-3 py-3 text-white">
              <option value="all">Any genre</option>
              {Object.values(genres).sort().map((genre) => (
                <option key={genre} value={genre.toLowerCase()}>{genre}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-2 text-sm text-gray-300">
            Language
            <select value={preferences.language} onChange={(e) => update("language", e.target.value)} className="bg-black/40 border border-white/10 rounded-lg px-3 py-3 text-white">
              {languages.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
        </div>

        <div className="flex gap-3 mt-8">
          <button onClick={save} className="bg-primary-container text-white px-6 py-3 rounded-lg font-semibold hover:brightness-110 transition-all">
            Save Preferences
          </button>
          <button onClick={reset} className="bg-white/10 text-white px-6 py-3 rounded-lg border border-white/10 hover:bg-white/20 transition-all">
            Reset
          </button>
          {saved && <span className="text-green-400 text-sm self-center">Saved</span>}
        </div>
      </section>
    </div>
  );
}
