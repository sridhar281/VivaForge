"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { getCurrentUser } from "@/services/auth";
import type { UserRead } from "@/types/auth";

export default function SettingsPage() {
  const [user, setUser] = useState<UserRead | null>(null);

  useEffect(() => {
    getCurrentUser().then(setUser).catch(() => {});
  }, []);

  return (
    <div>
      <Navbar />
      <main className="mx-auto max-w-lg px-6 py-10">
        <h1 className="mb-6 text-2xl font-bold">Settings</h1>

        <div className="rounded-xl border border-neutral-800 p-5">
          <p className="mb-1 text-sm text-neutral-500">Account email</p>
          <p className="font-medium">{user?.email ?? "…"}</p>
        </div>

        <div className="mt-6 rounded-xl border border-dashed border-neutral-800 p-5 text-sm text-neutral-500">
          Notification preferences, account deletion, and export settings aren't implemented yet — flagged here
          honestly as a future feature rather than a button that does nothing.
        </div>
      </main>
    </div>
  );
}
