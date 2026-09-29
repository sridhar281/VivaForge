"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { getRevisionVideo } from "@/services/learning";
import type { RevisionScene } from "@/types/content";

export default function RevisionVideoPage() {
  const { id } = useParams<{ id: string }>();
  const [scenes, setScenes] = useState<RevisionScene[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getRevisionVideo(id)
      .then(setScenes)
      .catch((e) => setError(e?.response?.data?.detail ?? "Could not load the revision reel."));
  }, [id]);

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="mb-2 text-2xl font-bold">Revision Reel</h1>
        <p className="mb-6 text-sm text-neutral-400">
          A scene-by-scene 60-90 second revision script — narration, on-screen subtitle text, and the source each
          scene is grounded in. (Rendered as a reel, not an auto-generated video file — see the README for why.)
        </p>
        {error && <p className="text-red-400">{error}</p>}

        <div className="space-y-4">
          {scenes.map((s, i) => (
            <div key={i} className="rounded-xl border border-neutral-800 p-5">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-medium text-brand-400">{s.concept}</span>
                {s.source_label && <span className="text-xs text-neutral-500">{s.source_label}</span>}
              </div>
              <p className="text-neutral-200">{s.narration}</p>
              <p className="mt-2 border-t border-neutral-800 pt-2 text-sm italic text-neutral-500">
                "{s.subtitle_text}"
              </p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
