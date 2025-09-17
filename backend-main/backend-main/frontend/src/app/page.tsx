"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <header className="mb-10">
          <h1 className="text-3xl md:text-5xl font-semibold tracking-tight">AlgoRail Controller</h1>
          <p className="mt-3 text-neutral-400 max-w-2xl">
            Real-time railway control and optimization dashboard powered by your FastAPI backend.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card title="Controller Dashboard" desc="Live trains, conflicts, KPIs, and optimization controls" href="/dashboard" />
          <Card title="Data Management" desc="Manage trains, sections, and disruptions" href="/manage" />
          <Card title="AI Decisions" desc="Submit scenarios to AI decision engine" href="/ai" />
        </div>
      </div>
    </div>
  );
}

function Card({ title, desc, href }: { title: string; desc: string; href: string }) {
  return (
    <Link
      href={href}
      className="group rounded-xl border border-neutral-800 bg-neutral-900/40 hover:bg-neutral-900 transition-colors p-6 flex flex-col gap-2"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-lg md:text-xl font-medium">{title}</h2>
        <span className="text-neutral-400 group-hover:text-neutral-200">→</span>
      </div>
      <p className="text-sm text-neutral-400">{desc}</p>
    </Link>
  );
}
