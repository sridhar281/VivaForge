"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { getStatus, triggerProcessing, uploadContent } from "@/services/content";
import type { ContentRead } from "@/types/content";

const ALLOWED = [".mp4", ".mp3", ".wav", ".pdf", ".ppt", ".pptx"];

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function pollStatus(contentId: string) {
    const poll = async () => {
      const c: ContentRead = await getStatus(contentId);
      setStatus(c.status);
      if (c.status === "completed") {
        router.push(`/content/${contentId}`);
        return;
      }
      if (c.status === "failed") {
        setError(c.status_message ?? "Processing failed.");
        setBusy(false);
        return;
      }
      setTimeout(poll, 4000);
    };
    poll();
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setError(null);
    setBusy(true);
    try {
      const content = await uploadContent(file, title || undefined);
      setStatus("uploaded");
      await triggerProcessing(content.id);
      setStatus("processing");
      pollStatus(content.id);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Upload failed.");
      setBusy(false);
    }
  }

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-lg px-6 py-10">
        <h1 className="mb-2 text-2xl font-bold">Upload content</h1>
        <p className="mb-6 text-sm text-neutral-400">
          Supported: {ALLOWED.join(", ")}. Processing runs in the background — you can watch the status here.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Title (optional — defaults to filename)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded-lg border border-neutral-700 bg-neutral-900 px-4 py-2"
            disabled={busy}
          />
          <input
            type="file"
            accept={ALLOWED.join(",")}
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="w-full text-sm"
            disabled={busy}
          />
          {error && <p className="text-sm text-red-400">{error}</p>}
          <button
            type="submit"
            disabled={!file || busy}
            className="w-full rounded-lg bg-brand-500 py-2 font-medium hover:bg-brand-600 disabled:opacity-50"
          >
            {busy ? "Uploading..." : "Upload & process"}
          </button>
        </form>

        {status && (
          <div className="mt-6 rounded-lg border border-neutral-800 p-4 text-sm">
            <p>
              Status: <span className="font-medium">{status}</span>
            </p>
            {busy && status !== "failed" && (
              <p className="mt-1 text-neutral-500">
                This can take a few minutes for video (transcription is the slowest step).
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
