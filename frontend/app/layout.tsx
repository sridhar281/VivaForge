import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VivaForge — Turn any lecture into your personal AI tutor",
  description:
    "AI-powered video-to-learning, viva & knowledge-gap platform. Upload lectures, get structured notes, adaptive viva sessions, and a personalized revision plan.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
