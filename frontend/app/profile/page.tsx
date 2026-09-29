"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { MasteryBar } from "@/components/ui";
import { getCurrentUser } from "@/services/auth";
import { getKnowledgeProfile } from "@/services/learning";
import type { UserRead } from "@/types/auth";
import type { KnowledgeProfile } from "@/types/viva";

export default function ProfilePage() {
  const [user, setUser] = useState<UserRead | null>(null);
  const [profile, setProfile] = useState<KnowledgeProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getCurrentUser(), getKnowledgeProfile()])
      .then(([u, p]) => {
        setUser(u);
        setProfile(p);
      })
      .catch(() => setError("Could not load your profile."));
  }, []);

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="mb-6 text-2xl font-bold">Learning Profile</h1>
        {error && <p className="text-red-400">{error}</p>}

        {user && (
          <div className="mb-8 rounded-xl border border-neutral-800 p-5">
            <p className="font-medium">{user.full_name || user.email}</p>
            <p className="text-sm text-neutral-500">{user.email}</p>
            <p className="mt-1 text-xs text-neutral-600">Member since {new Date(user.created_at).toLocaleDateString()}</p>
          </div>
        )}

        {profile && (
          <>
            <section className="mb-6">
              <h2 className="mb-3 text-lg font-semibold">Strong concepts</h2>
              {profile.strong_concepts.length === 0 ? (
                <p className="text-sm text-neutral-500">None yet.</p>
              ) : (
                profile.strong_concepts.map((c) => <MasteryBar key={c.concept_id} label={c.concept_name} score={c.mastery_score} />)
              )}
            </section>
            <section className="mb-6">
              <h2 className="mb-3 text-lg font-semibold">Weak concepts</h2>
              {profile.weak_concepts.length === 0 ? (
                <p className="text-sm text-neutral-500">None — nice work.</p>
              ) : (
                profile.weak_concepts.map((c) => <MasteryBar key={c.concept_id} label={c.concept_name} score={c.mastery_score} />)
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
