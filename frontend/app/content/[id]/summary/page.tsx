"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { getSummary } from "@/services/content";
import type { SummaryRead } from "@/types/content";

export default function SummaryPage() {
  const { id } = useParams<{ id: string }>();
  const [summary, setSummary] = useState<SummaryRead | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSummary(id).then(setSummary).catch((e) => setError(e?.response?.data?.detail ?? "Could not load summary."));
  }, [id]);

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-10">
        <h1 className="mb-6 text-2xl font-bold">Summary</h1>
        {error && <p className="text-red-400">{error}</p>}
        {!summary && !error && <p className="text-neutral-400">Loading…</p>}
        {summary && (
          <div className="space-y-8">
            <section>
              <h2 className="mb-2 text-lg font-semibold">Executive Summary</h2>
              <p className="text-neutral-300">{summary.executive_summary}</p>
            </section>

            <section>
              <h2 className="mb-2 text-lg font-semibold">Topic-wise Summary</h2>
              {summary.topic_summaries.map((t, i) => (
                <div key={i} className="mb-3">
                  <p className="font-medium">{t.topic}</p>
                  <p className="text-sm text-neutral-400">{t.summary}</p>
                </div>
              ))}
            </section>

            <section>
              <h2 className="mb-2 text-lg font-semibold">Definitions</h2>
              {summary.definitions.map((d, i) => (
                <p key={i} className="mb-1 text-sm">
                  <span className="font-medium">{d.term}:</span> <span className="text-neutral-400">{d.definition}</span>
                </p>
              ))}
            </section>

            <section>
              <h2 className="mb-2 text-lg font-semibold">Examples</h2>
              <ul className="list-disc space-y-1 pl-5 text-sm text-neutral-400">
                {summary.examples.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </section>

            <section>
              <h2 className="mb-2 text-lg font-semibold">Quick Revision Notes</h2>
              <ul className="list-disc space-y-1 pl-5 text-sm text-neutral-400">
                {summary.quick_revision_notes.map((n, i) => (
                  <li key={i}>{n}</li>
                ))}
              </ul>
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
