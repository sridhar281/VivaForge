"use client";

import Link from "next/link";
import { useState } from "react";

const STEPS = [
  "Upload a lecture (video, audio, PDF or slides)",
  "AI transcribes and understands the content",
  "Get structured notes, concepts and a knowledge graph",
  "Take an adaptive AI viva — the questions get harder as you improve",
  "See exactly which concepts you're weak in",
  "Follow a personalized revision plan",
];

const TECH = ["Next.js", "FastAPI", "PostgreSQL", "Chroma", "Whisper", "Groq", "ReportLab"];

type FeatureKey = "summary" | "viva" | "graph" | "flashcards" | "revision";

const FEATURES: Record<
  FeatureKey,
  { label: string; blurb: string }
> = {
  summary: {
    label: "Structured summary",
    blurb: "Topic-wise notes, definitions and examples — reorganized from the source, not a transcript dump.",
  },
  viva: {
    label: "AI viva",
    blurb: "A live oral exam. Answer gets graded on correctness and completeness, then the next question adapts.",
  },
  graph: {
    label: "Knowledge graph",
    blurb: "See how concepts relate — what's a prerequisite for what, what depends on what.",
  },
  flashcards: {
    label: "Flashcards",
    blurb: "Generated straight from your material. Mark a card mastered or difficult and it feeds back into your score.",
  },
  revision: {
    label: "Revision plan",
    blurb: "A short, prioritized list built from your actual weak spots — not a generic study checklist.",
  },
};

function FeaturePreview({ feature }: { feature: FeatureKey }) {
  if (feature === "summary") {
    return (
      <div className="space-y-3 text-sm">
        <p className="text-xs text-neutral-500">Executive summary</p>
        <div className="h-2 w-5/6 rounded bg-neutral-800" />
        <div className="h-2 w-full rounded bg-neutral-800" />
        <div className="h-2 w-2/3 rounded bg-neutral-800" />
        <p className="pt-2 text-xs text-neutral-500">Key concepts</p>
        <div className="flex flex-wrap gap-2">
          {["Normalization", "ACID", "Indexing"].map((c) => (
            <span key={c} className="rounded-full border border-neutral-700 px-3 py-1 text-xs text-neutral-300">
              {c}
            </span>
          ))}
        </div>
      </div>
    );
  }
  if (feature === "viva") {
    return (
      <div className="space-y-3 text-sm">
        <div className="flex items-center justify-between">
          <span className="rounded-full bg-neutral-800 px-2 py-0.5 text-xs text-neutral-400">medium</span>
          <span className="text-xs text-neutral-500">02:14 – 03:01</span>
        </div>
        <p className="text-neutral-200">"Why does normalization reduce redundancy, and what's the trade-off?"</p>
        <div className="rounded-lg border border-neutral-800 p-3 text-xs text-neutral-400">
          Your answer: "It splits data into related tables to avoid repeating values..."
        </div>
        <div className="flex items-center gap-2">
          <div className="h-1.5 flex-1 rounded-full bg-neutral-800">
            <div className="h-1.5 w-[78%] rounded-full bg-brand-500" />
          </div>
          <span className="text-xs text-neutral-400">7.8 / 10</span>
        </div>
      </div>
    );
  }
  if (feature === "graph") {
    return (
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <span className="rounded-full border border-neutral-700 px-3 py-1.5 text-neutral-200">Normalization</span>
        <span className="text-xs text-neutral-600">prerequisite of</span>
        <span className="rounded-full border border-neutral-700 px-3 py-1.5 text-neutral-200">2NF</span>
        <span className="w-full" />
        <span className="rounded-full border border-neutral-700 px-3 py-1.5 text-neutral-200">ACID</span>
        <span className="text-xs text-neutral-600">related to</span>
        <span className="rounded-full border border-neutral-700 px-3 py-1.5 text-neutral-200">Transactions</span>
      </div>
    );
  }
  if (feature === "flashcards") {
    return (
      <div className="flex min-h-[120px] flex-col items-center justify-center gap-2 rounded-lg border border-neutral-800 p-6 text-center">
        <span className="text-sm text-neutral-300">What is ACID?</span>
        <span className="text-xs text-neutral-600">tap to flip</span>
      </div>
    );
  }
  return (
    <ol className="space-y-2 text-sm text-neutral-300">
      <li className="flex items-center justify-between border-b border-neutral-800 pb-2">
        <span>1. Normalization</span>
        <span className="text-xs text-neutral-500">7 min</span>
      </li>
      <li className="flex items-center justify-between border-b border-neutral-800 pb-2">
        <span>2. Functional dependencies</span>
        <span className="text-xs text-neutral-500">7 min</span>
      </li>
      <li className="flex items-center justify-between pb-2">
        <span>3. Transactions</span>
        <span className="text-xs text-neutral-500">7 min</span>
      </li>
    </ol>
  );
}

export default function LandingPage() {
  const [activeFeature, setActiveFeature] = useState<FeatureKey>("viva");

  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <section className="grid grid-cols-1 items-center gap-10 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <h1 className="text-5xl font-semibold tracking-tight">
            Turn any lecture into your personal AI tutor.
          </h1>
          <p className="mt-6 max-w-xl text-lg text-neutral-400">
            Most tools tell you what was in the video. VivaForge tells you whether you actually
            understood it — then builds a viva, a knowledge graph, and a revision plan around your gaps.
          </p>
          <div className="mt-8 flex gap-4">
            <Link href="/register" className="rounded-lg bg-brand-500 px-6 py-3 font-medium hover:bg-brand-600">
              Get started
            </Link>
            <Link href="/login" className="rounded-lg border border-neutral-700 px-6 py-3 font-medium hover:bg-neutral-900">
              Log in
            </Link>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="rounded-2xl border border-neutral-800 bg-neutral-950 p-5">
            <FeaturePreview feature="viva" />
          </div>
        </div>
      </section>

      <section className="mt-28">
        <h2 className="mb-10 text-xl font-medium">How it works</h2>
        <ol className="mx-auto max-w-xl border-l border-neutral-800">
          {STEPS.map((step, i) => (
            <li key={i} className="relative pb-8 pl-8 last:pb-0">
              <span className="absolute -left-[13px] top-0 text-sm text-neutral-600">{i + 1}</span>
              <span className="text-neutral-300">{step}</span>
            </li>
          ))}
        </ol>
      </section>

      <section className="mt-28">
        <h2 className="mb-10 text-xl font-medium">What you get</h2>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-5">
          <div className="md:col-span-2">
            <div className="space-y-1">
              {(Object.keys(FEATURES) as FeatureKey[]).map((key) => (
                <button
                  key={key}
                  onClick={() => setActiveFeature(key)}
                  className={`block w-full rounded-lg px-4 py-3 text-left text-sm transition ${
                    activeFeature === key
                      ? "bg-neutral-900 text-white"
                      : "text-neutral-400 hover:bg-neutral-950 hover:text-neutral-200"
                  }`}
                >
                  {FEATURES[key].label}
                </button>
              ))}
            </div>
          </div>
          <div className="md:col-span-3">
            <div className="rounded-2xl border border-neutral-800 p-6">
              <p className="mb-5 text-sm text-neutral-400">{FEATURES[activeFeature].blurb}</p>
              <FeaturePreview feature={activeFeature} />
            </div>
          </div>
        </div>
      </section>

      <section className="mt-28 text-center">
        <h2 className="mb-6 text-xl font-medium">Built with</h2>
        <div className="flex flex-wrap justify-center gap-3">
          {TECH.map((t) => (
            <span key={t} className="rounded-full border border-neutral-800 px-4 py-2 text-sm text-neutral-400">
              {t}
            </span>
          ))}
        </div>
      </section>

      <section className="mt-28 rounded-2xl bg-brand-900/20 p-12 text-center">
        <h2 className="text-2xl font-semibold">Ready to find out what you actually know?</h2>
        <Link
          href="/register"
          className="mt-6 inline-block rounded-lg bg-brand-500 px-6 py-3 font-medium hover:bg-brand-600"
        >
          Upload your first lecture
        </Link>
      </section>
    </main>
  );
}
