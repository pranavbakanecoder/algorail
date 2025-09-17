import React from "react";

export function Card(props: { title?: string; children: React.ReactNode; className?: string; right?: React.ReactNode }) {
    return (
        <div className={`rounded-xl border border-neutral-800 glass ${props.className || ""}`}>
            {(props.title || props.right) && (
                <div className="px-4 py-3 border-b border-neutral-800 flex items-center justify-between">
                    <div className="text-sm font-medium">{props.title}</div>
                    <div>{props.right}</div>
                </div>
            )}
            <div className="p-4">{props.children}</div>
        </div>
    );
}

export function KPI(props: { label: string; value: string; trend?: string; variant?: "emerald" | "sky" | "violet" | "amber" | "rose" }) {
    const variant = props.variant || "emerald";
    const variantClasses: Record<string, string> = {
        emerald: "ring-emerald-500/30 bg-[radial-gradient(60%_80%_at_0%_0%,rgba(16,185,129,0.12),transparent_60%)]",
        sky: "ring-sky-400/30 bg-[radial-gradient(60%_80%_at_100%_0%,rgba(56,189,248,0.12),transparent_60%)]",
        violet: "ring-violet-400/30 bg-[radial-gradient(60%_80%_at_0%_100%,rgba(167,139,250,0.12),transparent_60%)]",
        amber: "ring-amber-400/30 bg-[radial-gradient(60%_80%_at_100%_100%,rgba(251,191,36,0.12),transparent_60%)]",
        rose: "ring-rose-400/30 bg-[radial-gradient(60%_80%_at_50%_50%,rgba(244,63,94,0.10),transparent_60%)]",
    };
    return (
        <div className={`rounded-xl border border-neutral-800 glass p-4 ring-1 ${variantClasses[variant]}`}>
            <div className="text-neutral-300 text-xs uppercase tracking-wide">{props.label}</div>
            <div className="text-2xl md:text-3xl font-semibold mt-1 gradient-text">{props.value}</div>
            {props.trend && <div className="text-xs text-neutral-500 mt-1">{props.trend}</div>}
        </div>
    );
}

export function Badge(props: { children: React.ReactNode; className?: string }) {
    return <span className={`text-xs px-2 py-0.5 rounded-full border ${props.className || ""}`}>{props.children}</span>;
}

export function Skeleton({ className }: { className?: string }) {
    return <div className={`animate-pulse bg-neutral-800/60 rounded-md ${className || "h-4"}`} />;
}


