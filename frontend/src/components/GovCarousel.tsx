"use client";

import React, { useState, useEffect } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Pause,
  Play,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  Building2,
  AlertCircle,
  FileText,
  MapPin,
  CheckCircle2,
} from "lucide-react";

interface SlideData {
  id: string;
  image: string;
  ministry: string;
  hindiTitle: string;
  englishTitle: string;
  subtitle: string;
  primaryActionText: string;
  secondaryActionText: string;
  actionType: "pothole" | "garbage" | "streetlight" | "matrix" | "tracking";
}

const SLIDES: SlideData[] = [
  {
    id: "slide-1",
    image: "/banners/swachh_bharat.jpg",
    ministry: "स्वच्छ भारत मिशन (शहरी 2.0) | SWACHH BHARAT MISSION URBAN",
    hindiTitle: "स्वच्छ गुरुग्राम, हरित भारत",
    englishTitle: "AI-Powered Civic Waste & Sanitation Redressal Drive",
    subtitle: "Direct Municipal Dispatch to MCG Sanitation Division • Real-Time Solid Waste Management 2026",
    primaryActionText: "Report Garbage Dump",
    secondaryActionText: "View Sanitation Hotspots",
    actionType: "garbage",
  },
  {
    id: "slide-2",
    image: "/banners/smart_road.jpg",
    ministry: "स्मार्ट सिटीज मिशन | SMART CITIES MISSION (MoHUA)",
    hindiTitle: "गड्ढा मुक्त सुरक्षित सड़कें",
    englishTitle: "Zero Pothole City Initiative — Multi-Factor AI Risk Assessment",
    subtitle: "72-Hour Statutory Asphalt Repair Guarantee under Municipal Citizen Charter 2024",
    primaryActionText: "Report Road Pothole",
    secondaryActionText: "Read Citizen Charter",
    actionType: "pothole",
  },
  {
    id: "slide-3",
    image: "/banners/command_center.jpg",
    ministry: "डिजिटल इंडिया | DIGITAL INDIA CIVIC GOVERNANCE",
    hindiTitle: "एकीकृत कमान एवं नियंत्रण केंद्र",
    englishTitle: "Integrated Command & Control Centre (ICCC) — Transparent Municipal Redressal",
    subtitle: "Verified Authority Routing • No Intermediaries • Multimodal Computer Vision Audits",
    primaryActionText: "Interactive Test Matrix",
    secondaryActionText: "Track Complaint Status",
    actionType: "matrix",
  },
  {
    id: "slide-4",
    image: "/banners/street_lighting.jpg",
    ministry: "राष्ट्रीय मार्ग प्रकाश कार्यक्रम | NATIONAL STREET LIGHTING PROGRAMME",
    hindiTitle: "सुरक्षित रात्रि मार्ग एवं प्रकाश व्यवस्था",
    englishTitle: "Safe Transit Corridors — 24x7 Night Illumination & Electrical Safety Monitoring",
    subtitle: "Automated Defect Flagging for Extinguished Luminaires and Exposed Wiring Hazards",
    primaryActionText: "Report Streetlight Issue",
    secondaryActionText: "View Ward Zones",
    actionType: "streetlight",
  },
];

interface GovCarouselProps {
  onNavigateReport: () => void;
  onNavigateTracking: () => void;
  onNavigateMatrix: () => void;
}

export default function GovCarousel({
  onNavigateReport,
  onNavigateTracking,
  onNavigateMatrix,
}: GovCarouselProps) {
  const [currentIdx, setCurrentIdx] = useState<number>(0);
  const [isPaused, setIsPaused] = useState<boolean>(false);

  useEffect(() => {
    if (isPaused) return;
    const timer = setInterval(() => {
      setCurrentIdx((prev) => (prev + 1) % SLIDES.length);
    }, 6000);
    return () => clearInterval(timer);
  }, [isPaused]);

  const nextSlide = () => {
    setCurrentIdx((prev) => (prev + 1) % SLIDES.length);
  };

  const prevSlide = () => {
    setCurrentIdx((prev) => (prev - 1 + SLIDES.length) % SLIDES.length);
  };

  const handleAction = (type: "pothole" | "garbage" | "streetlight" | "matrix" | "tracking") => {
    if (type === "matrix") {
      onNavigateMatrix();
    } else if (type === "tracking") {
      onNavigateTracking();
    } else {
      onNavigateReport();
    }
  };

  const activeSlide = SLIDES[currentIdx];

  return (
    <div className="relative rounded-3xl overflow-hidden border border-slate-700/80 shadow-2xl bg-slate-950 group">
      {/* Aspect Container */}
      <div className="relative h-[380px] sm:h-[460px] lg:h-[520px] w-full overflow-hidden">
        {/* Slides Images */}
        {SLIDES.map((slide, idx) => (
          <div
            key={slide.id}
            className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${
              idx === currentIdx ? "opacity-100 z-10" : "opacity-0 z-0 pointer-events-none"
            }`}
          >
            {/* Background Image */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={slide.image}
              alt={slide.englishTitle}
              className="w-full h-full object-cover object-center transform scale-105 transition-transform duration-10000"
            />

            {/* Dark Professional Civic Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/80 to-slate-900/40" />
            <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/70 to-transparent" />
          </div>
        ))}

        {/* Slide Content Overlay */}
        <div className="absolute inset-0 z-20 flex flex-col justify-end p-6 sm:p-10 lg:p-12 max-w-4xl space-y-4 pointer-events-auto">
          {/* Official Ministry Badge */}
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900/90 border border-amber-500/40 text-amber-300 text-xs font-semibold backdrop-blur-md shadow-lg w-fit">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="tracking-wide uppercase text-[11px] sm:text-xs">{activeSlide.ministry}</span>
          </div>

          {/* Dual Language Heading */}
          <div className="space-y-1">
            <p className="text-emerald-400 font-extrabold text-lg sm:text-2xl tracking-wide drop-shadow-md">
              {activeSlide.hindiTitle}
            </p>
            <h2 className="text-2xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-tight drop-shadow-lg">
              {activeSlide.englishTitle}
            </h2>
          </div>

          {/* Subtitle */}
          <p className="text-slate-300 text-xs sm:text-sm lg:text-base font-medium max-w-2xl leading-relaxed drop-shadow-md">
            {activeSlide.subtitle}
          </p>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={() => handleAction(activeSlide.actionType)}
              className="px-6 py-3 rounded-xl font-bold text-xs sm:text-sm bg-gradient-to-r from-amber-400 via-amber-300 to-yellow-400 hover:from-amber-300 hover:to-yellow-300 text-slate-950 shadow-xl shadow-amber-500/25 hover:shadow-amber-500/40 transition-all flex items-center space-x-2 cursor-pointer font-sans uppercase tracking-wider"
            >
              <Sparkles className="w-4 h-4 fill-slate-950" />
              <span>{activeSlide.primaryActionText}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={onNavigateReport}
              className="px-5 py-3 rounded-xl font-semibold text-xs sm:text-sm bg-slate-900/90 hover:bg-slate-800 text-white border border-slate-700/90 backdrop-blur-md transition-all flex items-center space-x-2 cursor-pointer"
            >
              <span>{activeSlide.secondaryActionText}</span>
            </button>
          </div>
        </div>

        {/* Carousel Controls: Arrows & Pause/Play */}
        <div className="absolute bottom-6 right-6 sm:bottom-10 sm:right-10 z-30 flex items-center space-x-2">
          {/* Pause / Play */}
          <button
            onClick={() => setIsPaused(!isPaused)}
            className="w-9 h-9 rounded-full bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center backdrop-blur-md transition-colors cursor-pointer"
            title={isPaused ? "Resume Slideshow" : "Pause Slideshow"}
          >
            {isPaused ? <Play className="w-3.5 h-3.5 ml-0.5" /> : <Pause className="w-3.5 h-3.5" />}
          </button>

          {/* Prev */}
          <button
            onClick={prevSlide}
            className="w-9 h-9 rounded-full bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center backdrop-blur-md transition-colors cursor-pointer"
            title="Previous Slide"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          {/* Counter */}
          <div className="px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-700 font-mono text-xs font-bold text-slate-300 backdrop-blur-md">
            0{currentIdx + 1} / 0{SLIDES.length}
          </div>

          {/* Next */}
          <button
            onClick={nextSlide}
            className="w-9 h-9 rounded-full bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center backdrop-blur-md transition-colors cursor-pointer"
            title="Next Slide"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {/* Slide Indicator Dots at Bottom Center */}
        <div className="absolute top-4 right-4 sm:top-6 sm:right-6 z-30 flex items-center space-x-1.5 bg-slate-950/70 p-1.5 rounded-full border border-slate-800 backdrop-blur-md">
          {SLIDES.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentIdx(idx)}
              className={`h-2 rounded-full transition-all cursor-pointer ${
                idx === currentIdx ? "w-6 bg-gradient-to-r from-amber-400 to-emerald-400" : "w-2 bg-slate-700 hover:bg-slate-500"
              }`}
              title={`Go to slide ${idx + 1}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
