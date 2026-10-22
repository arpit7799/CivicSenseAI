// =============================================================================
// CivicSense AI — Sample Civic Test Imagery & Presets
// =============================================================================

export interface SampleImage {
  id: string;
  title: string;
  category: string;
  expectedBehavior: string;
  description: string;
  latitude: number;
  longitude: number;
  imageUrl: string;
}

// Generate realistic data URLs for direct testing in browser
function generateSampleDataUrl(type: "pothole" | "garbage" | "streetlight" | "clean" | "blurry"): string {
  if (typeof document === "undefined") return "";

  const canvas = document.createElement("canvas");
  canvas.width = 640;
  canvas.height = 640;
  const ctx = canvas.getContext("2d");
  if (!ctx) return "";

  // Base asphalt background
  ctx.fillStyle = "#4a4a50";
  ctx.fillRect(0, 0, 640, 640);

  // Road noise texture
  for (let i = 0; i < 5000; i++) {
    const x = Math.random() * 640;
    const y = Math.random() * 640;
    const shade = Math.floor(Math.random() * 60 + 50);
    ctx.fillStyle = `rgb(${shade},${shade},${shade})`;
    ctx.fillRect(x, y, 2, 2);
  }

  // Yellow road lane line
  ctx.fillStyle = "#eab308";
  ctx.fillRect(40, 0, 16, 640);

  if (type === "pothole") {
    // Render deep dark road cavity with cracked borders
    ctx.beginPath();
    ctx.ellipse(320, 320, 140, 100, Math.PI / 12, 0, 2 * Math.PI);
    ctx.fillStyle = "#1e1e24";
    ctx.fill();
    ctx.lineWidth = 6;
    ctx.strokeStyle = "#111116";
    ctx.stroke();

    // Inner shadow & deep fracture
    ctx.beginPath();
    ctx.ellipse(310, 310, 80, 50, 0, 0, 2 * Math.PI);
    ctx.fillStyle = "#0a0a0d";
    ctx.fill();
  } else if (type === "garbage") {
    // Render scattered waste debris cluster
    const colors = ["#ef4444", "#3b82f6", "#22c55e", "#f3f4f6", "#1f2937", "#d97706"];
    for (let i = 0; i < 60; i++) {
      const x = 200 + Math.random() * 240;
      const y = 200 + Math.random() * 240;
      const w = 20 + Math.random() * 35;
      const h = 20 + Math.random() * 35;
      ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
      ctx.beginPath();
      ctx.arc(x, y, w / 2, 0, 2 * Math.PI);
      ctx.fill();
    }
  } else if (type === "streetlight") {
    // Render metallic pole with bent arm and broken luminaire
    ctx.fillStyle = "#9ca3af";
    ctx.fillRect(300, 100, 24, 450);
    ctx.fillStyle = "#6b7280";
    ctx.fillRect(300, 100, 160, 18);
    // Broken lamp head dangling
    ctx.fillStyle = "#374151";
    ctx.fillRect(440, 118, 30, 45);
    ctx.strokeStyle = "#dc2626";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(455, 163);
    ctx.lineTo(450, 190);
    ctx.stroke();
  } else if (type === "blurry") {
    // Blurry blurred image
    ctx.filter = "blur(18px)";
    ctx.fillStyle = "#3b82f6";
    ctx.fillRect(150, 150, 340, 340);
  }
  // "clean" is just the asphalt road with lane marker (no civic defects)

  return canvas.toDataURL("image/jpeg", 0.9);
}

export function getSamplePresets(): SampleImage[] {
  return [
    {
      id: "pothole-gurugram",
      title: "Deep Pothole (Sector 34, Gurugram)",
      category: "Road Damage",
      expectedBehavior: "Detects pothole with high confidence, triggers HIGH/CRITICAL severity, routes to MCG.",
      description: "Severe crater formed on central arterial road presenting immediate commuter accident risk.",
      latitude: 28.4595,
      longitude: 77.0266,
      imageUrl: "",
    },
    {
      id: "garbage-dump",
      title: "Overflowing Garbage Dump",
      category: "Sanitation",
      expectedBehavior: "Identifies garbage accumulation, calculates compounding sanitation factor, drafts cleanup order.",
      description: "Uncollected municipal waste and plastic accumulation spilling across pedestrian sidewalk.",
      latitude: 28.4610,
      longitude: 77.0315,
      imageUrl: "",
    },
    {
      id: "broken-streetlight",
      title: "Broken Streetlight & Exposed Wiring",
      category: "Electrical Safety",
      expectedBehavior: "Detects broken streetlight fixture, assigns safety priority, matches municipal electrical wing.",
      description: "Extinguished lamp head and dangling live cable near transit crossing.",
      latitude: 28.4720,
      longitude: 77.0420,
      imageUrl: "",
    },
    {
      id: "clean-road",
      title: "Clean Roadway (Non-Civic Test)",
      category: "Short-Circuit Rejection",
      expectedBehavior: "Rejects with 'rejected_no_civic_issue' status and skips downstream LLM/RAG gracefully.",
      description: "Normal maintained asphalt with no visible potholes or garbage piles.",
      latitude: 28.4595,
      longitude: 77.0266,
      imageUrl: "",
    },
  ];
}

export function getPresetDataUrl(type: "pothole" | "garbage" | "streetlight" | "clean" | "blurry"): string {
  return generateSampleDataUrl(type);
}
