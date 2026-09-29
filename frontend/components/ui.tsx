import type { ProcessingStatus } from "@/types/content";

const STATUS_COLORS: Record<ProcessingStatus, string> = {
  uploaded: "bg-neutral-700 text-neutral-200",
  processing: "bg-yellow-900 text-yellow-300",
  transcribing: "bg-yellow-900 text-yellow-300",
  understanding: "bg-yellow-900 text-yellow-300",
  generating: "bg-yellow-900 text-yellow-300",
  completed: "bg-green-900 text-green-300",
  failed: "bg-red-900 text-red-300",
};

export function StatusBadge({ status }: { status: ProcessingStatus }) {
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-medium ${STATUS_COLORS[status]}`}>
      {status}
    </span>
  );
}

export function MasteryBar({ label, score }: { label: string; score: number | null }) {
  const pct = score ?? 0;
  const color = pct >= 75 ? "bg-green-500" : pct >= 50 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="mb-3">
      <div className="mb-1 flex justify-between text-sm">
        <span>{label}</span>
        <span className="text-neutral-400">{score === null ? "Not attempted" : `${pct}%`}</span>
      </div>
      <div className="h-2 w-full rounded-full bg-neutral-800">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
