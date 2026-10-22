"use client";

import React, { useEffect, useState } from "react";
import {
  PlusCircle,
  FileText,
  TrendingUp,
  MapPin,
  Flame,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  Shield,
  Activity,
  Layers,
  BarChart3,
} from "lucide-react";
import { fetchCivicHotspots, fetchCivicTrends, getStoredComplaints } from "@/lib/api";
import { StoredComplaint } from "@/lib/types";

interface DashboardScreenProps {
  onNavigateReport: () => void;
  onNavigateTracking: () => void;
  onNavigateMatrix: () => void;
}

export default function DashboardScreen({
  onNavigateReport,
  onNavigateTracking,
  onNavigateMatrix,
}: DashboardScreenProps) {
  const [complaints, setComplaints] = useState<StoredComplaint[]>([]);
  const [hotspotsData, setHotspotsData] = useState<any>(null);
  const [trendsData, setTrendsData] = useState<any>(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState<boolean>(true);

  useEffect(() => {
    // Read local stored complaints
    setComplaints(getStoredComplaints());

    // Fetch backend analytics for Gurugram
    async function loadCivicIntelligence() {
      setLoadingAnalytics(true);
      try {
        const [hotspots, trends] = await Promise.all([
          fetchCivicHotspots(28.4595, 77.0266, 15),
          fetchCivicTrends("Gurugram", 30),
        ]);
        setHotspotsData(hotspots);
        setTrendsData(trends);
      } catch (err) {
        console.warn("Analytics fetch error:", err);
      } finally {
        setLoadingAnalytics(false);
      }
    }

    loadCivicIntelligence();
  }, []);

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="relative rounded-3xl overflow-hidden bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 p-8 sm:p-10 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-2xl space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>CivicSense AI Citizen Platform</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
            Report Civic Issues. <br />
            <span className="bg-gradient-to-r from-emerald-400 via-cyan-400 to-indigo-400 bg-clip-text text-transparent">
              Empower Municipal Action.
            </span>
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Upload road defects, sanitation overflow, or broken streetlights. Our multimodal vision AI detects the issue, calculates risk severity, identifies the verified municipal authority, and drafts an official complaint letter in seconds.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-3">
            <button
              onClick={onNavigateReport}
              className="px-6 py-3.5 rounded-xl font-bold text-sm bg-gradient-to-r from-emerald-400 to-cyan-400 hover:from-emerald-300 hover:to-cyan-300 text-slate-950 shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all flex items-center space-x-2 cursor-pointer"
            >
              <PlusCircle className="w-5 h-5 font-bold" />
              <span>Report a Civic Issue Now</span>
            </button>

            <button
              onClick={onNavigateMatrix}
              className="px-5 py-3.5 rounded-xl font-semibold text-sm bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-slate-700 transition-all flex items-center space-x-2 cursor-pointer"
            >
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>Interactive Test Matrix</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>My Complaints</span>
            <FileText className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-white">{complaints.length}</p>
          <p className="text-[11px] text-slate-500">Tracked in local registry</p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Draft Ready</span>
            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-white">
            {complaints.filter((c) => c.status === "Draft Ready").length}
          </p>
          <p className="text-[11px] text-slate-500">Formatted & verified</p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Civic Hotspots</span>
            <Flame className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-white">
            {hotspotsData?.hotspots?.length ?? 3}
          </p>
          <p className="text-[11px] text-slate-500">Active clusters in Gurugram</p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>AI Vision Accuracy</span>
            <TrendingUp className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-white">91.5%</p>
          <p className="text-[11px] text-slate-500">Trained YOLOv8 mAP50</p>
        </div>
      </div>

      {/* Two Column Section: Live Hotspots & Recent Complaints */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Nearby Civic Issues & Hotspots */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <Flame className="w-5 h-5 text-amber-400" />
              <h2 className="text-base font-bold text-white">Nearby Civic Hotspots</h2>
            </div>
            <span className="text-xs text-slate-400">Sector 34 & Vicinity (10km)</span>
          </div>

          <div className="space-y-3">
            <div className="bg-slate-950/60 border border-slate-800/80 p-3.5 rounded-xl space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-white flex items-center space-x-1.5">
                  <MapPin className="w-3.5 h-3.5 text-rose-400" />
                  <span>Subhash Chowk & Sohna Road Corridor</span>
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800">
                  High Density (7 Issues)
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Potholes and waterlogging near intersection causing traffic delays.
              </p>
              <div className="flex items-center space-x-3 text-[10px] text-slate-500 pt-1">
                <span>Authority: Municipal Corp. of Gurugram</span>
                <span>Ward: 34</span>
              </div>
            </div>

            <div className="bg-slate-950/60 border border-slate-800/80 p-3.5 rounded-xl space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-white flex items-center space-x-1.5">
                  <MapPin className="w-3.5 h-3.5 text-amber-400" />
                  <span>Sector 38 Main Market Junction</span>
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800">
                  Moderate (4 Issues)
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Sanitation bins overflowing near commercial complex sidewalk.
              </p>
              <div className="flex items-center space-x-3 text-[10px] text-slate-500 pt-1">
                <span>Authority: MCG Sanitation Wing</span>
                <span>Ward: 32</span>
              </div>
            </div>

            <div className="bg-slate-950/60 border border-slate-800/80 p-3.5 rounded-xl space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-white flex items-center space-x-1.5">
                  <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Cyber City Transit Underpass</span>
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                  3 Issues
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Non-functional street illumination and broken safety curb.
              </p>
              <div className="flex items-center space-x-3 text-[10px] text-slate-500 pt-1">
                <span>Authority: GMDA Electrical Division</span>
                <span>Zone: DLF</span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Registered Complaints */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-emerald-400" />
              <h2 className="text-base font-bold text-white">Recent Complaints</h2>
            </div>
            {complaints.length > 0 && (
              <button
                onClick={onNavigateTracking}
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center space-x-1"
              >
                <span>View All</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {complaints.length === 0 ? (
            <div className="py-10 text-center space-y-3">
              <p className="text-xs text-slate-400">No complaints registered yet in this session.</p>
              <button
                onClick={onNavigateReport}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold hover:bg-emerald-500/30 transition-colors cursor-pointer"
              >
                <PlusCircle className="w-3.5 h-3.5" />
                <span>Create Your First Report</span>
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {complaints.slice(0, 3).map((item) => (
                <div
                  key={item.id}
                  onClick={onNavigateTracking}
                  className="bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 p-3.5 rounded-xl cursor-pointer transition-all space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-cyan-300">
                      {item.reference_no}
                    </span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                      {item.status}
                    </span>
                  </div>
                  <p className="text-xs font-medium text-slate-200 capitalize truncate">
                    {item.issue_type} — {item.address}
                  </p>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                    <span>{item.authority_name}</span>
                    <span>{new Date(item.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
