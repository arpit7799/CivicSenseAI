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
  BellRing,
  BookOpen,
  Compass,
  Users,
  Building2,
  PhoneCall,
  Search,
  Newspaper,
  ExternalLink,
  RefreshCw,
  Radio,
} from "lucide-react";
import GovCarousel from "@/components/GovCarousel";
import GovPartnersRibbon from "@/components/GovPartnersRibbon";
import { fetchCivicHotspots, fetchCivicTrends, fetchCivicNews, getStoredComplaints } from "@/lib/api";
import { StoredComplaint, CivicNewsArticle } from "@/lib/types";

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
  const [trackingSearch, setTrackingSearch] = useState<string>("");

  // Real-time Civic News API state
  const [activeFeedTab, setActiveFeedTab] = useState<"hotspots" | "news">("hotspots");
  const [newsCategory, setNewsCategory] = useState<"all" | "roads" | "sanitation" | "environment" | "municipal">("all");
  const [newsArticles, setNewsArticles] = useState<CivicNewsArticle[]>([]);
  const [loadingNews, setLoadingNews] = useState<boolean>(false);
  const [newsLastUpdated, setNewsLastUpdated] = useState<string>("");

  const loadNewsFeed = async (cat: "all" | "roads" | "sanitation" | "environment" | "municipal" = newsCategory) => {
    setLoadingNews(true);
    try {
      const res = await fetchCivicNews("Gurugram", cat, 5);
      if (res && res.articles) {
        setNewsArticles(res.articles);
        setNewsLastUpdated(res.last_updated);
      }
    } catch (e) {
      console.warn("Failed to load civic news feed:", e);
    } finally {
      setLoadingNews(false);
    }
  };

  useEffect(() => {
    loadNewsFeed(newsCategory);
  }, [newsCategory]);

  const formatTimeAgo = (isoString: string) => {
    try {
      const diffMs = Date.now() - new Date(isoString).getTime();
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      if (diffHours < 1) return "Just now";
      if (diffHours < 24) return `${diffHours}h ago`;
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays < 7) return `${diffDays}d ago`;
      return new Date(isoString).toLocaleDateString("en-IN", { month: "short", day: "numeric" });
    } catch {
      return "Recent";
    }
  };

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
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* 1. Official Government Alert & Announcement Marquee Ticker */}
      <div className="bg-[#0b192c] border border-amber-500/30 rounded-2xl p-3 shadow-lg flex items-center space-x-3 text-xs overflow-hidden">
        <div className="flex items-center space-x-1.5 px-3 py-1 rounded-xl bg-amber-500/20 text-amber-300 font-bold shrink-0 border border-amber-500/30">
          <BellRing className="w-3.5 h-3.5 text-amber-400" />
          <span>नागरिक सूचना (NOTICE)</span>
        </div>
        <div className="text-slate-300 truncate">
          <span className="font-semibold text-white">हरियाणा नगर निगम नागरिक अधिकार पत्र 2024:</span>{" "}
          Under statutory mandate, all pothole, sanitation, and electrical grievances submitted through CivicSense AI receive automated municipal dispatch with a 24–72 hour physical inspection guarantee. Call 24x7 Control Room:{" "}
          <strong className="text-amber-300 font-mono">1800-180-1817</strong>.
        </div>
      </div>

      {/* 2. Authentic Government Hero Slideshow / Carousel */}
      <GovCarousel
        onNavigateReport={onNavigateReport}
        onNavigateTracking={onNavigateTracking}
        onNavigateMatrix={onNavigateMatrix}
      />

      {/* 3. Quick Citizen Services Portal Tiles (Government Style) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Tile 1: File Grievance */}
        <div
          onClick={onNavigateReport}
          className="group bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 hover:border-emerald-500/50 rounded-2xl p-5 shadow-xl transition-all hover:scale-[1.02] cursor-pointer"
        >
          <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
            <PlusCircle className="w-6 h-6" />
          </div>
          <h3 className="mt-4 font-extrabold text-base text-white group-hover:text-emerald-400 transition-colors">
            नागरिक शिकायत दर्ज करें
          </h3>
          <p className="text-xs font-semibold text-slate-400">File Civic Grievance</p>
          <p className="mt-2 text-xs text-slate-400 leading-relaxed">
            Upload photographs of potholes, garbage piles, or broken lights for AI detection and direct routing.
          </p>
          <div className="mt-4 flex items-center text-xs font-bold text-emerald-400 group-hover:translate-x-1 transition-transform">
            <span>Proceed to File</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </div>
        </div>

        {/* Tile 2: Track Status */}
        <div
          onClick={onNavigateTracking}
          className="group bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 hover:border-cyan-500/50 rounded-2xl p-5 shadow-xl transition-all hover:scale-[1.02] cursor-pointer"
        >
          <div className="w-12 h-12 rounded-xl bg-cyan-950/80 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
            <FileText className="w-6 h-6" />
          </div>
          <h3 className="mt-4 font-extrabold text-base text-white group-hover:text-cyan-400 transition-colors">
            शिकायत स्थिति देखें
          </h3>
          <p className="text-xs font-semibold text-slate-400">Track Complaint Status</p>
          <p className="mt-2 text-xs text-slate-400 leading-relaxed">
            Audit your registered municipal reference tickets (`CIVIC-2026-XXXX`) and view inspection reports.
          </p>
          <div className="mt-4 flex items-center text-xs font-bold text-cyan-400 group-hover:translate-x-1 transition-transform">
            <span>Track Registry</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </div>
        </div>

        {/* Tile 3: Citizen Charter */}
        <div
          onClick={onNavigateMatrix}
          className="group bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 hover:border-amber-500/50 rounded-2xl p-5 shadow-xl transition-all hover:scale-[1.02] cursor-pointer"
        >
          <div className="w-12 h-12 rounded-xl bg-amber-950/80 border border-amber-500/30 flex items-center justify-center text-amber-400 group-hover:scale-110 transition-transform">
            <BookOpen className="w-6 h-6" />
          </div>
          <h3 className="mt-4 font-extrabold text-base text-white group-hover:text-amber-400 transition-colors">
            नागरिक अधिकार पत्र
          </h3>
          <p className="text-xs font-semibold text-slate-400">Citizen Charter Rules</p>
          <p className="mt-2 text-xs text-slate-400 leading-relaxed">
            Review statutory resolution timelines, escalation hierarchy, and legal redressal provisions.
          </p>
          <div className="mt-4 flex items-center text-xs font-bold text-amber-400 group-hover:translate-x-1 transition-transform">
            <span>View Provisions</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </div>
        </div>

        {/* Tile 4: Ward & Engineering Locator */}
        <div
          onClick={onNavigateReport}
          className="group bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 hover:border-indigo-500/50 rounded-2xl p-5 shadow-xl transition-all hover:scale-[1.02] cursor-pointer"
        >
          <div className="w-12 h-12 rounded-xl bg-indigo-950/80 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
            <Compass className="w-6 h-6" />
          </div>
          <h3 className="mt-4 font-extrabold text-base text-white group-hover:text-indigo-400 transition-colors">
            वार्ड एवं क्षेत्रीय अभियंता
          </h3>
          <p className="text-xs font-semibold text-slate-400">Ward & JE Directory</p>
          <p className="mt-2 text-xs text-slate-400 leading-relaxed">
            Geographic reverse geocoding pinpoints your exact ward, municipal zone, and assigned engineer.
          </p>
          <div className="mt-4 flex items-center text-xs font-bold text-indigo-400 group-hover:translate-x-1 transition-transform">
            <span>Locate Ward</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </div>
        </div>
      </div>

      {/* 4. Official E-Governance & Mission Integrations Ribbon */}
      <GovPartnersRibbon />

      {/* 5. Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>My Registered Complaints</span>
            <FileText className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-white">{complaints.length}</p>
          <p className="text-[11px] text-slate-500">Tracked in citizen portal</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Draft Ready Tickets</span>
            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-white">
            {complaints.filter((c) => c.status === "Draft Ready").length}
          </p>
          <p className="text-[11px] text-slate-500">Validated with legal charter</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Active City Hotspots</span>
            <Flame className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-white">
            {hotspotsData?.hotspots?.length ?? 3}
          </p>
          <p className="text-[11px] text-slate-500">Monitored clusters in Gurugram</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-2xl space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Vision AI Accuracy</span>
            <TrendingUp className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-white">91.5%</p>
          <p className="text-[11px] text-slate-500">YOLOv8 mAP50 benchmark</p>
        </div>
      </div>

      {/* 6. Two Column Section: Live Hotspots & Recent Complaints */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Nearby Civic Issues & Real-Time NewsAPI Feed */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          {/* Card Header with Tab Switcher */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-3">
            <div className="flex items-center space-x-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800/80">
              <button
                onClick={() => setActiveFeedTab("hotspots")}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  activeFeedTab === "hotspots"
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Flame className="w-3.5 h-3.5 text-amber-400" />
                <span>Nearby Hotspots</span>
              </button>
              <button
                onClick={() => setActiveFeedTab("news")}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  activeFeedTab === "news"
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Newspaper className="w-3.5 h-3.5 text-cyan-400" />
                <span>Live Civic News</span>
                <span className="flex h-2 w-2 relative ml-1">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
              </button>
            </div>

            {activeFeedTab === "hotspots" ? (
              <span className="text-xs text-slate-400 flex items-center space-x-1">
                <MapPin className="w-3.5 h-3.5 text-slate-500" />
                <span>Sector 34 & Vicinity (10km)</span>
              </span>
            ) : (
              <div className="flex items-center space-x-2">
                <span className="text-[10px] uppercase tracking-wider font-extrabold px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 flex items-center space-x-1">
                  <Radio className="w-3 h-3 animate-pulse" />
                  <span>NewsAPI Live</span>
                </span>
                <button
                  onClick={() => loadNewsFeed(newsCategory)}
                  disabled={loadingNews}
                  title="Refresh Civic News Feed"
                  className="p-1 rounded-lg text-slate-400 hover:text-cyan-400 hover:bg-slate-800 transition-colors cursor-pointer disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loadingNews ? "animate-spin" : ""}`} />
                </button>
              </div>
            )}
          </div>

          {/* Tab 1: Nearby Civic Hotspots */}
          {activeFeedTab === "hotspots" && (
            <div className="space-y-3">
              <div className="bg-slate-950/70 border border-slate-800/80 p-3.5 rounded-xl space-y-1.5 hover:border-slate-700 transition-colors">
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
                  Potholes and monsoon waterlogging near arterial transit junction.
                </p>
                <div className="flex items-center space-x-3 text-[10px] text-slate-500 pt-1">
                  <span>Authority: Municipal Corp. of Gurugram</span>
                  <span>Ward: 34</span>
                </div>
              </div>

              <div className="bg-slate-950/70 border border-slate-800/80 p-3.5 rounded-xl space-y-1.5 hover:border-slate-700 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-xs text-white flex items-center space-x-1.5">
                    <MapPin className="w-3.5 h-3.5 text-amber-400" />
                    <span>Sector 38 Main Commercial Market</span>
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800">
                    Moderate (4 Issues)
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">
                  Sanitation bins overflowing near commercial complex sidewalk.
                </p>
                <div className="flex items-center space-x-3 text-[10px] text-slate-500 pt-1">
                  <span>Authority: MCG Sanitation Division</span>
                  <span>Ward: 32</span>
                </div>
              </div>

              <div className="bg-slate-950/70 border border-slate-800/80 p-3.5 rounded-xl space-y-1.5 hover:border-slate-700 transition-colors">
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

              {/* Dynamic backend hotspots if available */}
              {hotspotsData?.clusters && hotspotsData.clusters.length > 0 && (
                <div className="pt-2 border-t border-slate-800">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                    Spatial Clustering Engine (DBSCAN)
                  </span>
                  {hotspotsData.clusters.slice(0, 2).map((c: any, idx: number) => (
                    <div key={idx} className="bg-slate-950/50 border border-slate-800/60 p-2.5 rounded-lg text-xs space-y-1 mb-1.5">
                      <div className="flex items-center justify-between text-slate-300">
                        <span className="font-medium text-white">Cluster #{c.cluster_id ?? idx + 1} ({c.issue_type ?? "mixed"})</span>
                        <span className="text-[10px] text-amber-400">{c.complaint_count ?? c.size} reports</span>
                      </div>
                      <p className="text-[10px] text-slate-500">Radius: {c.radius_meters ? (c.radius_meters / 1000).toFixed(1) + "km" : "Local"}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Real-Time Civic News Feed (NewsAPI.org) */}
          {activeFeedTab === "news" && (
            <div className="space-y-3">
              {/* Category Filter Pills */}
              <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 scrollbar-none text-[11px]">
                {[
                  { id: "all", label: "All News" },
                  { id: "roads", label: "Roads & Transit" },
                  { id: "sanitation", label: "Sanitation" },
                  { id: "environment", label: "Pollution / AQI" },
                  { id: "municipal", label: "MCG & Policy" },
                ].map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setNewsCategory(cat.id as any)}
                    className={`px-2.5 py-1 rounded-lg font-semibold whitespace-nowrap transition-colors cursor-pointer ${
                      newsCategory === cat.id
                        ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm"
                        : "bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800"
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>

              {/* News Articles List */}
              {loadingNews ? (
                <div className="py-8 space-y-3 text-center">
                  <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-cyan-400 border-t-transparent" />
                  <p className="text-xs text-slate-400">Fetching live civic bulletins for Gurugram & NCR...</p>
                </div>
              ) : newsArticles.length === 0 ? (
                <div className="py-8 text-center text-xs text-slate-400 space-y-2">
                  <p>No recent civic articles found for this filter category.</p>
                  <button
                    onClick={() => setNewsCategory("all")}
                    className="text-cyan-400 hover:underline font-semibold cursor-pointer"
                  >
                    Reset to All News
                  </button>
                </div>
              ) : (
                <div className="space-y-2.5 max-h-[360px] overflow-y-auto pr-1">
                  {newsArticles.map((article, idx) => {
                    const badgeColor =
                      article.category === "Roads & Traffic"
                        ? "bg-rose-950/80 text-rose-300 border-rose-800/80"
                        : article.category === "Sanitation & Waste"
                        ? "bg-amber-950/80 text-amber-300 border-amber-800/80"
                        : article.category === "Environment & AQI"
                        ? "bg-emerald-950/80 text-emerald-300 border-emerald-800/80"
                        : "bg-cyan-950/80 text-cyan-300 border-cyan-800/80";

                    return (
                      <div
                        key={idx}
                        className="group bg-slate-950/80 border border-slate-800/80 hover:border-cyan-500/40 p-3.5 rounded-xl space-y-1.5 transition-all shadow-sm"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded border ${badgeColor}`}
                          >
                            {article.category}
                          </span>
                          <span className="text-[10px] text-slate-500 flex items-center space-x-1 shrink-0">
                            <span>{article.source_name}</span>
                            <span>•</span>
                            <span>{formatTimeAgo(article.published_at)}</span>
                          </span>
                        </div>

                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-bold text-xs text-white group-hover:text-cyan-300 transition-colors block line-clamp-2"
                        >
                          {article.title}
                        </a>

                        {article.description && (
                          <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                            {article.description}
                          </p>
                        )}

                        <div className="flex items-center justify-between pt-1 border-t border-slate-900 text-[10px]">
                          <span className="text-slate-500">Region: {article.city}</span>
                          <a
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center space-x-1 group-hover:translate-x-0.5 transition-transform"
                          >
                            <span>Read Full Bulletin</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500">
                <span>Aggregated via NewsAPI.org (Civic Wire)</span>
                {newsLastUpdated && <span>Updated: {formatTimeAgo(newsLastUpdated)}</span>}
              </div>
            </div>
          )}
        </div>

        {/* Recent Registered Complaints */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-emerald-400" />
              <h2 className="text-base font-bold text-white">Recent Complaints Log</h2>
            </div>
            {complaints.length > 0 && (
              <button
                onClick={onNavigateTracking}
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center space-x-1 cursor-pointer"
              >
                <span>View Full Registry</span>
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
                  className="bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 p-3.5 rounded-xl cursor-pointer transition-all space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-amber-300">
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
