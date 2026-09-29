"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { MasteryBar, StatusBadge } from "@/components/ui";
import { getKnowledgeProfile, getRevisionPlan } from "@/services/learning";
import { listContent } from "@/services/content";
import type { ContentRead } from "@/types/content";
import type { KnowledgeProfile, RevisionPlan } from "@/types/viva";

export default function DashboardPage() {
  const [content, setContent] = useState<ContentRead[]>([]);
  const [profile, setProfile] = useState<KnowledgeProfile | null>(null);
  const [plan, setPlan] = useState<RevisionPlan | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([listContent(), getKnowledgeProfile(), getRevisionPlan()])
      .then(([c, p, r]) => {
        setContent(c);
        setProfile(p);
        setPlan(r);
      })
      .catch(() => setError("Could not load dashboard data. Is the backend running?"));
  }, []);

  const allScored = profile ? [...profile.strong_concepts, ...profile.weak_concepts] : [];

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <h1 className="mb-6 text-2xl font-bold">Dashboard</h1>
        {error && <p className="mb-6 text-red-400">{error}</p>}

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <section className="lg:col-span-2">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Your content</h2>
              <Link href="/upload" className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium hover:bg-brand-600">
                Upload new
              </Link>
            </div>
            {content.length === 0 ? (
              <p className="text-neutral-400">No content uploaded yet.</p>
            ) : (
              <div className="space-y-3">
                {content.map((c) => (
                  <Link
                    key={c.id}
                    href={`/content/${c.id}`}
                    className="flex items-center justify-between rounded-xl border border-neutral-800 p-4 hover:border-neutral-600"
                  >
                    <div>
                      <p className="font-medium">{c.title}</p>
                      <p className="text-xs text-neutral-500">{c.content_type.toUpperCase()}</p>
                    </div>
                    <StatusBadge status={c.status} />
                  </Link>
                ))}
              </div>
            )}
          </section>

          <section>
            <h2 className="mb-4 text-lg font-semibold">Knowledge Mastery</h2>
            {allScored.length === 0 ? (
              <p className="text-neutral-400">Take a viva to start tracking mastery.</p>
            ) : (
              allScored.map((c) => <MasteryBar key={c.concept_id} label={c.concept_name} score={c.mastery_score} />)
            )}

            <h2 className="mb-4 mt-8 text-lg font-semibold">Today's Revision</h2>
            {plan && plan.items.length > 0 ? (
              <div>
                <ol className="list-decimal space-y-1 pl-5 text-sm text-neutral-300">
                  {plan.items.map((i) => (
                    <li key={i.concept_id}>{i.concept_name}</li>
                  ))}
                </ol>
                <p className="mt-2 text-xs text-neutral-500">Estimated {plan.estimated_minutes} minutes</p>
                <Link href="/revision" className="mt-3 inline-block text-sm text-brand-400">
                  Go to revision →
                </Link>
              </div>
            ) : (
              <p className="text-neutral-400">No weak spots detected yet — nice work.</p>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
