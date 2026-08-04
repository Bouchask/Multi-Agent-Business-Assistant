import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Antigravity Gemini | Enterprise Multi-Agent OS",
  description: "Advanced Autonomous Supervisor Routing, Google Calendar Sync, and Qdrant Vector Analytics with cutting-edge Google Gemini Aesthetics.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0d0f12] text-slate-100 antialiased selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}
