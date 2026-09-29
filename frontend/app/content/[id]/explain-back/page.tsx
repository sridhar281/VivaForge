"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { getExplainBackPrompt, submitExplainBack } from "@/services/learning";
import type { ExplainBackPrompt, ExplainBackResult } from "@/types/viva";

export default function ExplainBackPage() {
  const { id } = useParams<{ id: string }>();
  const [prompt, setPrompt] = useState<ExplainBackPrompt | null>(null);
  const [explanation, setExplanation] = useState("");
  const [result, setResult] = useState<ExplainBackResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getExplainBackPrompt(id)
      .then(setPrompt)
      .catch((e) => setError(e?.response?.data?.detail ?? "Could not load a concept to explain."));
  }, [id]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!prompt || !explanation.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const r = await submitExplainBack(id, prompt.concept_id, explanation);
      setResult(r);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Could not evaluate your explanation.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="mb-2 text-2xl font-bold">Explain It Back</h1>
        <p className="mb-6 text-sm text-neutral-400">
          Explain the concept below in your own words — no hints, just what you remember.
        </p>
        {error && <p className="text-red-400">{error}</p>}

        {prompt && (
          <>
            <div className="mb-4 rounded-xl border border-neutral-800 p-5">
              <p className="text-lg font-medium">{prompt.prompt_text}</p>
            </div>

            {!result ? (
              <form onSubmit={handleSubmit} className="space-y-3">
                <textarea
                  value={explanation}
                  onChange={(e) => setExplanation(e.target.value)}
                  rows={6}
                  placeholder="Type your explanation..."
                  className="w-full rounded-lg border border-neutral-700 bg-neutral-900 px-4 py-2"
                  disabled={busy}
                />
                <button
                  type="submit"
                  disabled={busy}
                  className="rounded-lg bg-brand-500 px-6 py-2 font-medium hover:bg-brand-600 disabled:opacity-50"
                >
                  {busy ? "Evaluating..." : "Submit"}
                </button>
              </form>
            ) : (
              <div className="rounded-xl border border-neutral-800 p-5">
                <p className="mb-3 font-medium">Concept mastery: {result.mastery_percent.toFixed(0)}%</p>
                {result.covered_points.length > 0 && (
                  <div className="mb-2">
                    <p className="text-sm text-green-400">Covered:</p>
                    <ul className="list-disc pl-5 text-sm text-neutral-300">
                      {result.covered_points.map((p, i) => (
                        <li key={i}>✓ {p}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.missing_points.length > 0 && (
                  <div className="mb-2">
                    <p className="text-sm text-yellow-400">Missing:</p>
                    <ul className="list-disc pl-5 text-sm text-neutral-300">
                      {result.missing_points.map((p, i) => (
                        <li key={i}>✗ {p}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.incorrect_points.length > 0 && (
                  <div className="mb-2">
                    <p className="text-sm text-red-400">Incorrect:</p>
                    <ul className="list-disc pl-5 text-sm text-neutral-300">
                      {result.incorrect_points.map((p, i) => (
                        <li key={i}>✗ {p}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <p className="mt-4 text-sm text-brand-400">{result.recommendation}</p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
