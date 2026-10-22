"use client";

import React, { useEffect, useState } from "react";
import { checkBackendHealth } from "@/lib/api";
import { HealthResponse } from "@/lib/types";
import { Activity, ShieldCheck, AlertCircle, FileText, PlusCircle, LayoutDashboard, Database } from "lucide-react";

interface NavbarProps {
  activeScreen: "dashboard" | "report" | "results" | "complaint" | "tracking" | "matrix";
  setActiveScreen: (screen: "dashboard" | "report" | "results" | "complaint" | "tracking" | "matrix") => void;
  hasAnalysisResults: boolean;
}

export default function Navbar({ activeScreen, setActiveScreen, hasAnalysisResults }: NavbarProps) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const refreshHealth = async () => {
    setLoading(true);
    const data = await checkBackendHealth();
    setHealth(data);
    setLoading(false);
  };

  useEffect(() => {
    refreshHealth();
    const interval = setInterval(refreshHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-50 bg-slate-900 border-b border-slate-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveScreen("dashboard")}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-md shadow-emerald-500/20">
              <ShieldCheck className="w-6 h-6 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  CivicSense<span className="text-emerald-400">AI</span>
                </span>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-slate-800 text-emerald-400 border border-emerald-500/30">
                  Citizen Portal
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Multimodal AI Civic Intelligence</p>
            </div>
          </div>

          {/* Navigation links */}
          <nav className="hidden md:flex items-center space-x-1">
            <button
              onClick={() => setActiveScreen("dashboard")}
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeScreen === "dashboard"
                  ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => setActiveScreen("report")}
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeScreen === "report"
                  ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30 font-semibold"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
            >
              <PlusCircle className="w-4 h-4" />
              <span>Report Issue</span>
            </button>

            {hasAnalysisResults && (
              <button
                onClick={() => setActiveScreen("results")}
                className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeScreen === "results" || activeScreen === "complaint"
                    ? "bg-slate-800 text-white border border-slate-700"
                    : "text-slate-400 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                <Activity className="w-4 h-4 text-cyan-400" />
                <span>AI Results</span>
              </button>
            )}

            <button
              onClick={() => setActiveScreen("tracking")}
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeScreen === "tracking"
                  ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>My Complaints</span>
            </button>

            <button
              onClick={() => setActiveScreen("matrix")}
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeScreen === "matrix"
                  ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40"
                  : "text-slate-400 hover:text-indigo-300 hover:bg-indigo-950/40"
              }`}
            >
              <Database className="w-4 h-4 text-indigo-400" />
              <span>Testing Matrix</span>
            </button>
          </nav>

          {/* Backend Health Badge */}
          <div className="flex items-center space-x-2">
            <div
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-full border text-xs font-medium cursor-pointer transition-all ${
                health
                  ? "bg-emerald-950/40 text-emerald-400 border-emerald-500/30 hover:bg-emerald-950/60"
                  : "bg-red-950/40 text-red-400 border-red-500/30 hover:bg-red-950/60"
              }`}
              onClick={refreshHealth}
              title={health ? `AI Service Online (v${health.version})` : "Cannot reach FastAPI backend at localhost:8000"}
            >
              <span className={`w-2 h-2 rounded-full ${health ? "bg-emerald-400 animate-pulse" : "bg-red-400"}`} />
              <span className="hidden sm:inline">
                {health ? "FastAPI Live" : "FastAPI Offline"}
              </span>
              {loading && <span className="text-[10px] opacity-75">...</span>}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
