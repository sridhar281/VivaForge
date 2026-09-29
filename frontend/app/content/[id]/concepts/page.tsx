"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { getConcepts } from "@/services/content";
import type { ConceptRead } from "@/types/content";

export default function ConceptsPage() {
  const { id } = useParams<{ id: string }>();
  const [concepts, setConcepts] = useState<ConceptRead[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getConcepts(id).then(setConcepts).catch(() => setError("Could not load concepts."));
  }, [id]);

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-10">
        <h1 className="mb-6 text-2xl font-bold">Concepts</h1>
        {error && <p className="text-red-400">{error}</p>}
        <div className="space-y-4">
          {concepts.map((c) => (
            <div key={c.id} className="rounded-xl border border-neutral-800 p-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">{c.name}</h3>
                {c.source_label && (
                  <span className="rounded-full bg-neutral-800 px-2 py-0.5 text-xs text-neutral-400">
                    Source: {c.source_label}
                  </span>
                )}
              </div>
              {c.explanation && <p className="mt-1 text-sm text-neutral-400">{c.explanation}</p>}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
