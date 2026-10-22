"use client";

import React from "react";
import { ShieldCheck, Building2, ExternalLink } from "lucide-react";

export default function GovPartnersRibbon() {
  const partners = [
    {
      name: "डिजिटल इंडिया",
      englishName: "Digital India",
      tagline: "Power To Empower",
      color: "from-blue-600 to-indigo-600",
      accent: "border-blue-500/30 text-blue-400",
      link: "https://digitalindia.gov.in/",
    },
    {
      name: "स्वच्छ भारत मिशन",
      englishName: "Swachh Bharat",
      tagline: "एक कदम स्वच्छता की ओर",
      color: "from-emerald-600 to-teal-600",
      accent: "border-emerald-500/30 text-emerald-400",
      link: "https://swachhbharatmission.ddws.gov.in/",
    },
    {
      name: "मेरी सरकार",
      englishName: "MyGov India",
      tagline: "Citizen Engagement Platform",
      color: "from-amber-600 to-orange-600",
      accent: "border-amber-500/30 text-amber-400",
      link: "https://mygov.in/",
    },
    {
      name: "स्मार्ट सिटीज मिशन",
      englishName: "Smart Cities",
      tagline: "Ministry of Housing & Urban Affairs",
      color: "from-cyan-600 to-blue-600",
      accent: "border-cyan-500/30 text-cyan-400",
      link: "https://smartcities.gov.in/",
    },
    {
      name: "सीएम विंडो हरियाणा",
      englishName: "CM Window",
      tagline: "Grievance Redressal System",
      color: "from-rose-600 to-red-600",
      accent: "border-rose-500/30 text-rose-400",
      link: "https://cmharyanacell.nic.in/",
    },
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 sm:p-5 shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-3">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-amber-400" />
          <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            National E-Governance & Mission Integrations
          </span>
        </div>
        <span className="text-[11px] text-slate-500 hidden sm:inline">
          Official Government Portals & Initiatives
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {partners.map((p, idx) => (
          <a
            key={idx}
            href={p.link}
            target="_blank"
            rel="noopener noreferrer"
            className="group bg-slate-950/70 border border-slate-800 hover:border-slate-700 rounded-xl p-3 flex flex-col justify-between transition-all hover:scale-[1.02] hover:bg-slate-900/80"
          >
            <div>
              <div className="flex items-center justify-between">
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${p.accent}`}>
                  GOI
                </span>
                <ExternalLink className="w-3 h-3 text-slate-600 group-hover:text-slate-400 transition-colors" />
              </div>
              <p className="mt-2 text-xs font-bold text-white group-hover:text-amber-300 transition-colors">
                {p.englishName}
              </p>
              <p className="text-[11px] text-slate-400 font-medium">
                {p.name}
              </p>
            </div>
            <p className="mt-2 text-[10px] text-slate-500 italic truncate">
              {p.tagline}
            </p>
          </a>
        ))}
      </div>
    </div>
  );
}
