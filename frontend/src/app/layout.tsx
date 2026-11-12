import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CivicSense AI — Civic Complaint Portal",
  description: "Multimodal AI civic complaint generation, road damage detection, and municipal grievance routing.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased font-sans">
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900">{children}</body>
    </html>
  );
}
