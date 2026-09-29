"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { MasteryBar } from "@/components/ui";
import { getGraph } from "@/services/learning";
import type { GraphRead } from "@/types/content";

export default function GraphPage() {
  const { id } = useParams<{ id: string }>();
  const [graph, setGraph] = useState<GraphRead | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getGraph(id).then(setGraph).catch(() => setError("Could not load the knowledge graph."));
  }, [id]);

  const nodeName = (nodeId: string) => graph?.nodes.find((n) => n.id === nodeId)?.name ?? nodeId;

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-10">
        <h1 className="mb-2 text-2xl font-bold">Knowledge Graph</h1>
        <p className="mb-6 text-sm text-neutral-400">
          Click a concept to see its explanation and your mastery. Relationships are listed below.
        </p>
        {error && <p className="text-red-400">{error}</p>}

        {graph && (
          <>
            <div className="space-y-2">
              {graph.nodes.map((n) => (
                <details key={n.id} className="rounded-xl border border-neutral-800 p-4">
                  <summary className="cursor-pointer font-medium">{n.name}</summary>
                  <div className="mt-3">
                    {n.explanation && <p className="mb-3 text-sm text-neutral-400">{n.explanation}</p>}
                    <MasteryBar label="Your mastery" score={n.mastery_score} />
                  </div>
                </details>
              ))}
            </div>

            {graph.edges.length > 0 && (
              <div className="mt-8">
                <h2 className="mb-3 text-lg font-semibold">Relationships</h2>
                <ul className="space-y-1 text-sm text-neutral-400">
                  {graph.edges.map((e, i) => (
                    <li key={i}>
                      <span className="text-neutral-200">{nodeName(e.source)}</span>{" "}
                      <span className="text-brand-400">{e.relation_type}</span>{" "}
                      <span className="text-neutral-200">{nodeName(e.target)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
