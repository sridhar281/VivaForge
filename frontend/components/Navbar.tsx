"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { logout } from "@/services/auth";

const LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/upload", label: "Upload" },
  { href: "/revision", label: "Revision" },
  { href: "/profile", label: "Profile" },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <nav className="flex items-center justify-between border-b border-neutral-800 px-6 py-4">
      <Link href="/dashboard" className="text-lg font-bold text-brand-400">
        VivaForge
      </Link>
      <div className="flex items-center gap-6 text-sm">
        {LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={pathname?.startsWith(link.href) ? "text-white" : "text-neutral-400 hover:text-white"}
          >
            {link.label}
          </Link>
        ))}
        <button
          onClick={() => {
            logout();
            router.push("/login");
          }}
          className="text-neutral-400 hover:text-white"
        >
          Log out
        </button>
      </div>
    </nav>
  );
}
