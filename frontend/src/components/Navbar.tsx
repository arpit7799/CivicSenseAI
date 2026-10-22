"use client";

import React, { useEffect, useState } from "react";
import { checkBackendHealth } from "@/lib/api";
import { HealthResponse } from "@/lib/types";
import {
  Activity,
  ShieldCheck,
  FileText,
  PlusCircle,
  LayoutDashboard,
  Database,
  Phone,
  Globe,
  HelpCircle,
} from "lucide-react";

interface NavbarProps {
  activeScreen: "dashboard" | "report" | "results" | "complaint" | "tracking" | "matrix";
  setActiveScreen: (screen: "dashboard" | "report" | "results" | "complaint" | "tracking" | "matrix") => void;
  hasAnalysisResults: boolean;
}

export default function Navbar({ activeScreen, setActiveScreen, hasAnalysisResults }: NavbarProps) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [lang, setLang] = useState<"EN" | "HI">("EN");

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
    <header className="sticky top-0 z-50 shadow-2xl">
      {/* 1. Indian Tricolor Top Accent Line */}
      <div className="h-1.5 w-full flex">
        <div className="h-full w-1/3 bg-[#FF9933]" /> {/* Saffron */}
        <div className="h-full w-1/3 bg-[#FFFFFF]" /> {/* White */}
        <div className="h-full w-1/3 bg-[#138808]" /> {/* Green */}
      </div>

      {/* 2. Official Government Identity & Citizen Accessibility Strip */}
      <div className="bg-[#0b192c] border-b border-slate-800 text-slate-300 text-xs px-4 sm:px-6 lg:px-8 py-1.5">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-1.5">
          {/* Left: Official Government of India & Haryana Seal */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1.5">
              <span className="font-bold text-white tracking-wide">भारत सरकार</span>
              <span className="text-slate-500">|</span>
              <span className="font-medium text-slate-300">Government of India</span>
            </div>
            <span className="hidden md:inline text-slate-600">•</span>
            <div className="hidden md:flex items-center space-x-1.5 text-slate-400">
              <span className="font-semibold text-amber-300">हरियाणा सरकार</span>
              <span className="text-slate-600">|</span>
              <span>Govt. of Haryana</span>
            </div>
          </div>

          {/* Right: Helpline & Language & Accessibility Controls */}
          <div className="flex items-center space-x-4 text-[11px]">
            {/* Toll-Free Civic Helpline */}
            <div className="flex items-center space-x-1.5 text-amber-400 font-semibold bg-amber-950/40 border border-amber-500/30 px-2.5 py-0.5 rounded-full">
              <Phone className="w-3 h-3" />
              <span>Toll-Free: 1800-180-1817</span>
            </div>

            {/* Language Switcher */}
            <button
              onClick={() => setLang(lang === "EN" ? "HI" : "EN")}
              className="flex items-center space-x-1 text-slate-300 hover:text-white transition-colors cursor-pointer"
            >
              <Globe className="w-3 h-3 text-cyan-400" />
              <span className="font-bold">{lang === "EN" ? "हिन्दी" : "English"}</span>
            </button>

            {/* Accessibility Size */}
            <div className="hidden sm:flex items-center space-x-1 text-slate-400 border-l border-slate-700 pl-3">
              <span className="text-[10px] hover:text-white cursor-pointer px-1">A-</span>
              <span className="text-[11px] font-bold text-white px-1">A</span>
              <span className="text-[12px] hover:text-white cursor-pointer px-1">A+</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Main Official Portal Navigation Bar */}
      <div className="bg-[#0f233d] border-b border-slate-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-18">
            {/* Brand Logo & Municipal Seal */}
            <div
              className="flex items-center space-x-3 cursor-pointer py-2"
              onClick={() => setActiveScreen("dashboard")}
            >
              {/* Official Seal Emblem */}
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 via-emerald-600 to-cyan-500 p-0.5 shadow-md shadow-amber-500/10">
                <div className="w-full h-full bg-[#0b192c] rounded-[14px] flex items-center justify-center">
                  <ShieldCheck className="w-7 h-7 text-amber-400" />
                </div>
              </div>

              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-black text-xl tracking-tight text-white">
                    CivicSense<span className="text-amber-400">AI</span>
                  </span>
                  <span className="px-2 py-0.5 text-[10px] font-extrabold rounded-md bg-emerald-950/80 text-emerald-400 border border-emerald-500/40 uppercase tracking-wider">
                    Official Portal
                  </span>
                </div>
                <p className="text-[11px] text-slate-300 font-medium">
                  नागरिक शिकायत एवं समाधान मंच | Municipal Corporation of Gurugram
                </p>
              </div>
            </div>

            {/* Navigation tabs */}
            <nav className="hidden md:flex items-center space-x-1">
              <button
                onClick={() => setActiveScreen("dashboard")}
                className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeScreen === "dashboard"
                    ? "bg-[#18365a] text-amber-300 border border-amber-400/40 shadow-sm"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>Dashboard (मुख्य)</span>
              </button>

              <button
                onClick={() => setActiveScreen("report")}
                className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeScreen === "report"
                    ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/30"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                <PlusCircle className="w-4 h-4" />
                <span>Report Issue (शिकायत)</span>
              </button>

              {hasAnalysisResults && (
                <button
                  onClick={() => setActiveScreen("results")}
                  className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    activeScreen === "results" || activeScreen === "complaint"
                      ? "bg-[#18365a] text-cyan-300 border border-cyan-400/40"
                      : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                  }`}
                >
                  <Activity className="w-4 h-4 text-cyan-400" />
                  <span>AI Results (परिणाम)</span>
                </button>
              )}

              <button
                onClick={() => setActiveScreen("tracking")}
                className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeScreen === "tracking"
                    ? "bg-[#18365a] text-amber-300 border border-amber-400/40 shadow-sm"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                <FileText className="w-4 h-4" />
                <span>My Complaints (स्थिति)</span>
              </button>

              <button
                onClick={() => setActiveScreen("matrix")}
                className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeScreen === "matrix"
                    ? "bg-indigo-950 text-indigo-300 border border-indigo-500/50"
                    : "text-slate-400 hover:text-indigo-300 hover:bg-indigo-950/40"
                }`}
              >
                <Database className="w-4 h-4 text-indigo-400" />
                <span>Test Matrix (परीक्षण)</span>
              </button>
            </nav>

            {/* Backend Service Status Badge */}
            <div className="flex items-center space-x-2">
              <div
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-full border text-xs font-semibold cursor-pointer transition-all ${
                  health
                    ? "bg-emerald-950/60 text-emerald-400 border-emerald-500/40 hover:bg-emerald-950/80"
                    : "bg-red-950/60 text-red-400 border-red-500/40 hover:bg-red-950/80"
                }`}
                onClick={refreshHealth}
                title={health ? `FastAPI Backend Online (v${health.version})` : "Cannot reach FastAPI backend"}
              >
                <span className={`w-2 h-2 rounded-full ${health ? "bg-emerald-400 animate-pulse" : "bg-red-400"}`} />
                <span className="hidden sm:inline">
                  {health ? "FastAPI Live (127.0.0.1)" : "FastAPI Offline"}
                </span>
                {loading && <span className="text-[10px] opacity-75">...</span>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
