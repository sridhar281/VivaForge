import Link from "next/link";

const WORKFLOW = [
  "Upload a lecture (video, audio, PDF or slides)",
  "AI transcribes and understands the content",
  "Get structured notes, concepts and a knowledge graph",
  "Take an adaptive AI viva — the questions get harder as you improve",
  "See exactly which concepts you're weak in",
  "Follow a personalized revision plan",
];

const FEATURES = [
  { title: "Structured Summaries", desc: "Topic-wise notes, definitions, examples — not just a transcript dump." },
  { title: "Source-Grounded Viva PDF", desc: "Easy → medium → hard question chains, every one traceable back to a timestamp or page." },
  { title: "AI Viva Simulator", desc: "A live adaptive oral exam that gets harder or easier based on how you answer." },
  { title: "Explain-It-Back", desc: "Explain a concept in your own words; the AI tells you exactly what you missed." },
  { title: "Knowledge Graph", desc: "See how concepts relate — prerequisites, dependencies, examples." },
  { title: "Personalized Revision", desc: "A daily plan built from your actual weak spots, not a generic checklist." },
];

const TECH = ["Next.js", "FastAPI", "PostgreSQL", "Chroma", "Whisper", "Groq", "ReportLab"];

export default function LandingPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <section className="text-center">
        <h1 className="text-5xl font-bold tracking-tight">
          Turn any lecture into your <span className="text-brand-400">personal AI tutor</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-neutral-400">
          Most tools tell you what was in the video. VivaForge tells you whether you actually
          understood it — then builds a viva, a knowledge graph, and a revision plan around your gaps.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link href="/register" className="rounded-lg bg-brand-500 px-6 py-3 font-medium hover:bg-brand-600">
            Get started
          </Link>
          <Link href="/login" className="rounded-lg border border-neutral-700 px-6 py-3 font-medium hover:bg-neutral-900">
            Log in
          </Link>
        </div>
      </section>

      <section className="mt-24">
        <h2 className="mb-8 text-center text-2xl font-semibold">How it works</h2>
        <ol className="mx-auto max-w-xl space-y-4">
          {WORKFLOW.map((step, i) => (
            <li key={i} className="flex gap-4">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-500 text-sm font-bold">
                {i + 1}
              </span>
              <span className="text-neutral-300">{step}</span>
            </li>
          ))}
        </ol>
      </section>

      <section className="mt-24">
        <h2 className="mb-8 text-center text-2xl font-semibold">What you get</h2>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="rounded-xl border border-neutral-800 p-6">
              <h3 className="mb-2 font-semibold">{f.title}</h3>
              <p className="text-sm text-neutral-400">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-24 text-center">
        <h2 className="mb-6 text-2xl font-semibold">Built with</h2>
        <div className="flex flex-wrap justify-center gap-3">
          {TECH.map((t) => (
            <span key={t} className="rounded-full border border-neutral-800 px-4 py-2 text-sm text-neutral-400">
              {t}
            </span>
          ))}
        </div>
      </section>

      <section className="mt-24 rounded-2xl bg-brand-900/20 p-12 text-center">
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
