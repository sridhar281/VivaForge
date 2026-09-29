"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { getFlashcards, markFlashcard } from "@/services/learning";
import type { FlashcardRead } from "@/types/content";

export default function FlashcardsPage() {
  const { id } = useParams<{ id: string }>();
  const [cards, setCards] = useState<FlashcardRead[]>([]);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getFlashcards(id)
      .then(setCards)
      .catch((e) => setError(e?.response?.data?.detail ?? "Could not load flashcards."));
  }, [id]);

  const card = cards[index];

  function next() {
    setFlipped(false);
    setIndex((i) => Math.min(i + 1, cards.length - 1));
  }
  function prev() {
    setFlipped(false);
    setIndex((i) => Math.max(i - 1, 0));
  }
  async function mark(status: "mastered" | "difficult") {
    if (!card) return;
    await markFlashcard(id, card.concept, status);
    next();
  }

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-lg px-6 py-10">
        <h1 className="mb-6 text-2xl font-bold">Flashcards</h1>
        {error && <p className="text-red-400">{error}</p>}
        {!card && !error && <p className="text-neutral-400">Loading…</p>}

        {card && (
          <>
            <p className="mb-2 text-sm text-neutral-500">
              Card {index + 1} of {cards.length} · {card.concept}
            </p>
            <button
              onClick={() => setFlipped((f) => !f)}
              className="flex min-h-[180px] w-full items-center justify-center rounded-xl border border-neutral-800 p-6 text-center text-lg hover:border-neutral-600"
            >
              {flipped ? card.back : card.front}
            </button>
            <p className="mt-2 text-center text-xs text-neutral-500">Click card to flip</p>

            <div className="mt-6 flex justify-between">
              <button onClick={prev} disabled={index === 0} className="text-sm text-neutral-400 disabled:opacity-30">
                ← Previous
              </button>
              <button onClick={next} disabled={index === cards.length - 1} className="text-sm text-neutral-400 disabled:opacity-30">
                Next →
              </button>
            </div>

            <div className="mt-6 flex gap-3">
              <button
                onClick={() => mark("difficult")}
                className="flex-1 rounded-lg border border-red-900 py-2 text-sm text-red-400 hover:bg-red-950/30"
              >
                Mark difficult
              </button>
              <button
                onClick={() => mark("mastered")}
                className="flex-1 rounded-lg border border-green-900 py-2 text-sm text-green-400 hover:bg-green-950/30"
              >
                Mark mastered
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
