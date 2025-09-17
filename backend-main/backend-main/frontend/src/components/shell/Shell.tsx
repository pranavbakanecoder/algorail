"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import StatusPill from "./StatusPill";

const nav = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/manage", label: "Manage" },
    { href: "/ai", label: "AI" },
];

export default function Shell({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    return (
        <div className="min-h-screen grid grid-cols-1 lg:grid-cols-[260px_1fr]">
            <aside className="hidden lg:block border-r border-neutral-800/80 bg-neutral-950/60">
                <div className="px-5 py-5 border-b border-neutral-800/80">
                    <div className="text-xl font-semibold tracking-tight">AlgoRail</div>
                    <div className="text-xs text-neutral-400">Controller Console</div>
                </div>
                <nav className="px-2 py-4 space-y-1">
                    {nav.map((item) => {
                        const active = pathname?.startsWith(item.href);
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`block rounded-md px-3 py-2 text-sm transition-colors ${active
                                    ? "bg-emerald-600/20 text-emerald-300 border border-emerald-600/30"
                                    : "text-neutral-300 hover:bg-neutral-900 hover:text-neutral-100"
                                    }`}
                            >
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>
            </aside>
            <div className="flex flex-col">
                <header className="sticky top-0 z-20 backdrop-blur supports-[backdrop-filter]:bg-neutral-950/60 bg-neutral-950/40 border-b border-neutral-800/80">
                    <div className="mx-auto max-w-7xl px-4 md:px-6 py-3 flex items-center justify-between">
                        <div className="text-sm text-neutral-400 flex items-center gap-3">
                            <span>{formatPath(pathname || "/")}</span>
                            <StatusPill />
                        </div>
                        <div className="text-sm text-neutral-400"><ClientClock /></div>
                    </div>
                </header>
                <main className="flex-1">{children}</main>
            </div>
        </div>
    );
}

function formatPath(p: string) {
    if (p === "/") return "Home";
    return p
        .replace(/^\//, "")
        .split("/")
        .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
        .join(" / ");
}


function ClientClock() {
    const [now, setNow] = useState<string>("");
    useEffect(() => {
        const update = () => setNow(new Date().toLocaleString());
        update();
        const id = setInterval(update, 60_000);
        return () => clearInterval(id);
    }, []);
    return <>{now}</>;
}


