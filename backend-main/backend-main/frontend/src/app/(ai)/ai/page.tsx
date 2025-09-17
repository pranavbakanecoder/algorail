"use client";

import { Card } from "@/components/ui";
import Link from "next/link";
import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export default function AIPage() {
    const [payload, setPayload] = useState(
        JSON.stringify(
            {
                trains: [
                    {
                        train_id: "T001",
                        priority: 5,
                        train_type: "Express",
                        length: 500,
                        delay: 2,
                        passenger_load: 800,
                        energy_efficiency: 0.9,
                    },
                ],
                conflicts: [
                    {
                        section_id: "S03",
                        competing_trains: ["T001", "T002"],
                        signal_state: "Green",
                        weather_condition: "Clear",
                        platform_availability: { A: true, B: false },
                        track_capacity: 2,
                    },
                ],
            },
            null,
            2
        )
    );
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any | null>(null);
    const [error, setError] = useState<string | null>(null);

    const submit = async () => {
        setError(null);
        try {
            setLoading(true);
            const res = await fetch(`${API_BASE}/api/ai_decision/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: payload,
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const json = await res.json();
            setResult(json);
        } catch (e: any) {
            setError(e.message || "Failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="px-6 py-8 mx-auto max-w-7xl">
            <div className="mb-8 flex items-center justify-between">
                <h1 className="text-2xl md:text-3xl font-semibold">AI Decision Engine</h1>
                <Link href="/" className="text-sm text-neutral-400 hover:text-neutral-200">Home</Link>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card title="Request" right={<button onClick={() => navigator.clipboard.writeText(payload)} className="text-xs px-2 py-1 rounded-md border border-neutral-800 hover:bg-neutral-900">Copy</button>}>
                    <textarea
                        className="w-full h-[420px] rounded-md bg-neutral-950 border border-neutral-800 p-3 font-mono text-sm"
                        value={payload}
                        onChange={(e) => setPayload(e.target.value)}
                    />
                    <div className="mt-3 flex items-center gap-3">
                        <button onClick={submit} disabled={loading} className="rounded-md bg-emerald-600 hover:bg-emerald-500 disabled:opacity-60 px-4 py-2 font-medium">
                            {loading ? "Submitting…" : "Submit to AI"}
                        </button>
                        {error && <div className="text-rose-400 text-sm">{error}</div>}
                    </div>
                </Card>

                <Card title="Response">
                    <pre className="whitespace-pre-wrap break-words text-sm text-neutral-300">
                        {result ? JSON.stringify(result, null, 2) : "No response yet"}
                    </pre>
                </Card>
            </div>
        </div>
    );
}


