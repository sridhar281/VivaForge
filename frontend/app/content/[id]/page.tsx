"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { StatusBadge } from "@/components/ui";
import { getContent, triggerProcessing } from "@/services/content";
import { generateVivaPdf, artifactDownloadUrl, startVivaSession } from "@/services/viva";
import type { ContentRead } from "@/types/content";

const TABS = [
  { key: "summary", label: "Summary" },
  { key: "concepts", label: "Concepts" },
  { key: "graph", label: "Knowledge Graph" },
  { key: "flashcards", label: "Flashcards" },
  { key: "explain-back", label: "Explain It Back" },
  { key: "revision-video", label: "Revision Video" },
];

export default function ContentWorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [content, setContent] = useState<ContentRead | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getContent(id).then(setContent).catch(() => setError("Could not load this content."));
  }, [id]);

  async function handleGeneratePdf() {
    setBusy(true);
    try {
      const { artifact_id } = await generateVivaPdf(id);
      window.open(artifactDownloadUrl(artifact_id), "_blank");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Could not generate the viva PDF.");
    } finally {
      setBusy(false);
    }
  }

  async function handleStartViva() {
    setBusy(true);
    try {
      const session = await startVivaSession(id);
      router.push(`/viva/${session.session_id}?contentId=${id}&questionId=${session.first_question.id}&q=${encodeURIComponent(session.first_question.question_text)}&difficulty=${session.first_question.difficulty}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Could not start a viva session.");
    } finally {
      setBusy(false);
    }
  }

  if (error) return <ErrorShell error={error} />;
  if (!content) return <LoadingShell />;

  if (content.status !== "completed") {
    return (
      <div>
        <Navbar />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <h1 className="mb-2 text-2xl font-bold">{content.title}</h1>
          <div className="mt-4 flex items-center gap-3">
            <StatusBadge status={content.status} />
            {content.status_message && <span className="text-sm text-red-400">{content.status_message}</span>}
          </div>
          {content.status === "failed" && (
            <button
              onClick={() => triggerProcessing(id).then(() => location.reload())}
              className="mt-6 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium hover:bg-brand-600"
            >
              Retry processing
            </button>
          )}
          {content.status !== "failed" && (
            <p className="mt-4 text-sm text-neutral-400">
              Still processing — refresh this page in a moment, or watch progress from the upload page.
            </p>
          )}
        </main>
      </div>
    );
  }

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold">{content.title}</h1>
          <StatusBadge status={content.status} />
        </div>

        <div className="mb-8 flex flex-wrap gap-3">
          <button
            onClick={handleStartViva}
            disabled={busy}
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium hover:bg-brand-600 disabled:opacity-50"
          >
            Start AI Viva
          </button>
          <button
            onClick={handleGeneratePdf}
            disabled={busy}
            className="rounded-lg border border-neutral-700 px-4 py-2 text-sm font-medium hover:bg-neutral-900 disabled:opacity-50"
          >
            Download Viva PDF
          </button>
        </div>

        <div className="mb-6 flex flex-wrap gap-2 border-b border-neutral-800 pb-4">
          {TABS.map((tab) => (
            <Link
              key={tab.key}
              href={`/content/${id}/${tab.key}`}
              className="rounded-lg border border-neutral-800 px-3 py-1.5 text-sm hover:border-neutral-600"
            >
              {tab.label}
            </Link>
          ))}
        </div>

        <p className="text-sm text-neutral-400">
          Pick a tab above, or start the AI viva / download the viva PDF using the buttons above.
        </p>
      </main>
    </div>
  );
}

function LoadingShell() {
  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10 text-neutral-400">Loading…</main>
    </div>
  );
}

function ErrorShell({ error }: { error: string }) {
  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10 text-red-400">{error}</main>
    </div>
  );
}
