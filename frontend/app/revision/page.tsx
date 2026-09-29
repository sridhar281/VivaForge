"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { getRevisionPlan, regenerateRevisionPlan } from "@/services/learning";
import type { RevisionPlan } from "@/types/viva";

export default function RevisionPage() {
  const [plan, setPlan] = useState<RevisionPlan | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getRevisionPlan().then(setPlan).catch(() => setError("Could not load your revision plan."));
  }, []);

  async function regenerate() {
    setBusy(true);
    try {
      setPlan(await regenerateRevisionPlan());
    } catch {
      setError("Could not regenerate your revision plan.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Today's Revision</h1>
          <button
            onClick={regenerate}
            disabled={busy}
            className="rounded-lg border border-neutral-700 px-4 py-2 text-sm hover:bg-neutral-900 disabled:opacity-50"
          >
            {busy ? "Regenerating..." : "Regenerate"}
          </button>
        </div>
        {error && <p className="text-red-400">{error}</p>}

        {plan && plan.items.length === 0 && (
          <p className="text-neutral-400">No weak concepts detected yet — take a viva or two first.</p>
        )}

        {plan && plan.items.length > 0 && (
          <>
            <p className="mb-4 text-sm text-neutral-400">Estimated {plan.estimated_minutes} minutes total</p>
            <ol className="space-y-3">
              {plan.items.map((item, i) => (
                <li key={item.concept_id} className="flex items-center justify-between rounded-xl border border-neutral-800 p-4">
                  <div>
                    <p className="font-medium">
                      {i + 1}. {item.concept_name}
                    </p>
                    <p className="text-xs text-neutral-500">
                      {item.mastery_score === null ? "Not yet attempted" : `Currently ${item.mastery_score}%`}
                    </p>
                  </div>
                  <span className="text-xs text-neutral-500">{item.estimated_minutes} min</span>
                </li>
              ))}
            </ol>
          </>
        )}
      </main>
    </div>
  );
}
