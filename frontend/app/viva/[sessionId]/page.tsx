"use client";

import { useParams, useSearchParams } from "next/navigation";
import { useRef, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { submitAnswer } from "@/services/viva";
import type { EvaluationRead, QuestionRead } from "@/types/viva";

export default function VivaSessionPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const sessionId = params.sessionId as string;

  const [question, setQuestion] = useState<QuestionRead>({
    id: searchParams.get("questionId") ?? "",
    question_text: searchParams.get("q") ?? "",
    difficulty: (searchParams.get("difficulty") as any) ?? "easy",
    sequence_number: 1,
    source_label: null,
  });
  const [answer, setAnswer] = useState("");
  const [wasSpoken, setWasSpoken] = useState(false);
  const [recording, setRecording] = useState(false);
  const [evaluation, setEvaluation] = useState<EvaluationRead | null>(null);
  const [completed, setCompleted] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  function speechSupported(): boolean {
    return typeof window !== "undefined" && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);
  }

  function toggleRecording() {
    if (recording) {
      recognitionRef.current?.stop();
      setRecording(false);
      return;
    }
    const SpeechRecognitionImpl = (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognitionImpl();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = true;
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((r: any) => r[0].transcript)
        .join(" ");
      setAnswer((prev) => (prev ? prev + " " + transcript : transcript));
      setWasSpoken(true);
    };
    recognition.onerror = () => setRecording(false);
    recognition.onend = () => setRecording(false);
    recognitionRef.current = recognition;
    recognition.start();
    setRecording(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!answer.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const result = await submitAnswer(sessionId, question.id, answer, wasSpoken);
      setEvaluation(result.evaluation);
      setCompleted(result.session_completed);
      if (result.next_question) {
        setQuestion(result.next_question);
      }
      setAnswer("");
      setWasSpoken(false);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Could not submit your answer.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="mb-6 text-2xl font-bold">AI Viva</h1>

        {evaluation && (
          <div className="mb-6 rounded-xl border border-neutral-800 p-4">
            <p className="mb-2 font-medium">Score: {evaluation.score.toFixed(1)}/10</p>
            <p className="mb-2 text-sm text-neutral-300">{evaluation.feedback}</p>
            {evaluation.correct_concepts.length > 0 && (
              <p className="text-xs text-green-400">✓ Covered: {evaluation.correct_concepts.join(", ")}</p>
            )}
            {evaluation.missing_concepts.length > 0 && (
              <p className="text-xs text-yellow-400">Missing: {evaluation.missing_concepts.join(", ")}</p>
            )}
            {evaluation.incorrect_claims.length > 0 && (
              <p className="text-xs text-red-400">✗ Incorrect: {evaluation.incorrect_claims.join(", ")}</p>
            )}
          </div>
        )}

        {completed ? (
          <div className="rounded-xl border border-green-800 bg-green-950/30 p-6 text-center">
            <p className="text-lg font-medium">Viva session complete.</p>
            <p className="mt-1 text-sm text-neutral-400">Check your dashboard to see updated mastery scores.</p>
          </div>
        ) : (
          <>
            <div className="mb-4 rounded-xl border border-neutral-800 p-5">
              <p className="mb-1 text-xs uppercase tracking-wide text-neutral-500">
                {question.difficulty} {question.source_label ? `· ${question.source_label}` : ""}
              </p>
              <p className="text-lg">{question.question_text}</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
              <textarea
                value={answer}
                onChange={(e) => {
                  setAnswer(e.target.value);
                  setWasSpoken(false);
                }}
                placeholder="Type your answer, or use the mic button below..."
                rows={5}
                className="w-full rounded-lg border border-neutral-700 bg-neutral-900 px-4 py-2"
                disabled={busy}
              />
              {speechSupported() && (
                <button
                  type="button"
                  onClick={toggleRecording}
                  className={`rounded-lg px-4 py-2 text-sm font-medium ${
                    recording ? "bg-red-600 hover:bg-red-700" : "border border-neutral-700 hover:bg-neutral-900"
                  }`}
                >
                  {recording ? "Stop recording" : "🎤 Answer by voice"}
                </button>
              )}
              {error && <p className="text-sm text-red-400">{error}</p>}
              <button
                type="submit"
                disabled={busy}
                className="block rounded-lg bg-brand-500 px-6 py-2 font-medium hover:bg-brand-600 disabled:opacity-50"
              >
                {busy ? "Evaluating..." : "Submit answer"}
              </button>
            </form>
            {!speechSupported() && (
              <p className="mt-3 text-xs text-neutral-500">
                Voice answering uses your browser's built-in speech recognition (Chrome/Edge) — not supported in
                this browser, so type your answer instead.
              </p>
            )}
          </>
        )}
      </main>
    </div>
  );
}
