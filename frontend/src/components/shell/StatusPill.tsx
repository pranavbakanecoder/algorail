"use client";

import { useEffect, useState } from "react";

export default function StatusPill() {
    const [status, setStatus] = useState<"checking" | "healthy" | "down">("checking");

    useEffect(() => {
        let mounted = true;
        async function check() {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000"}/api/status`, { cache: "no-store" });
                if (!mounted) return;
                setStatus(res.ok ? "healthy" : "down");
            } catch {
                if (!mounted) return;
                setStatus("down");
            }
        }
        check();
        const id = setInterval(check, 10000);
        return () => {
            mounted = false;
            clearInterval(id);
        };
    }, []);

    const cls =
        status === "healthy"
            ? "bg-emerald-500/20 text-emerald-300 border-emerald-600/40"
            : status === "checking"
                ? "bg-amber-500/20 text-amber-300 border-amber-600/40"
                : "bg-rose-500/20 text-rose-300 border-rose-600/40";

    const label = status === "healthy" ? "Backend: Healthy" : status === "checking" ? "Backend: Checking" : "Backend: Down";

    return (
        <span className={`text-xs px-2 py-0.5 rounded-full border ${cls}`}>{label}</span>
    );
}


