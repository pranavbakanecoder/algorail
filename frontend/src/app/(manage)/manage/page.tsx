"use client";

import { Card } from "@/components/ui";
import Link from "next/link";
import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

type Train = { train_id: string; priority: number; train_type: string };
type Section = { section_id: string; length_km?: number };
type Disruption = { disruption_id: string; section_id: string; description?: string };

export default function ManagePage() {
    const [trains, setTrains] = useState<Train[]>([]);
    const [sections, setSections] = useState<Section[]>([]);
    const [disruptions, setDisruptions] = useState<Disruption[]>([]);

    useEffect(() => {
        Promise.all([
            fetch(`${API_BASE}/trains/`).then((r) => r.json()).catch(() => []),
            fetch(`${API_BASE}/sections/`).then((r) => r.json()).catch(() => []),
            fetch(`${API_BASE}/disruptions/`).then((r) => r.json()).catch(() => []),
        ]).then(([t, s, d]) => {
            setTrains(t || []);
            setSections(s || []);
            setDisruptions(d || []);
        });
    }, []);

    return (
        <div className="px-6 py-8 mx-auto max-w-7xl">
            <div className="mb-8 flex items-center justify-between">
                <h1 className="text-2xl md:text-3xl font-semibold">Data Management</h1>
                <Link href="/" className="text-sm text-neutral-400 hover:text-neutral-200">Home</Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card title="Trains" right={<input placeholder="Filter by ID" className="rounded-md bg-neutral-900 border border-neutral-800 px-2 py-1 text-sm" onChange={(e) => setTrains((prev) => prev.filter(t => t.train_id.toLowerCase().includes(e.target.value.toLowerCase())))} />}>
                    <SimpleTable
                        headers={["Train ID", "Priority", "Type"]}
                        rows={trains.map((t) => [t.train_id, String(t.priority ?? "-"), t.train_type ?? "-"])}
                    />
                </Card>
                <Card title="Sections">
                    <SimpleTable
                        headers={["Section", "Length (km)"]}
                        rows={sections.map((s) => [s.section_id, String((s as any).length_km ?? "-")])}
                    />
                </Card>
                <Card title="Disruptions">
                    <SimpleTable
                        headers={["ID", "Section", "Description"]}
                        rows={disruptions.map((d) => [d.disruption_id ?? "-", d.section_id, (d as any).description ?? "-"])}
                    />
                </Card>
            </div>
        </div>
    );
}

// Panel replaced by Card component

function SimpleTable({ headers, rows }: { headers: string[]; rows: (string | number)[][] }) {
    return (
        <div className="overflow-x-auto">
            <table className="w-full text-sm">
                <thead className="text-neutral-400">
                    <tr>
                        {headers.map((h) => (
                            <th key={h} className="text-left py-2 pr-4">{h}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((r, i) => (
                        <tr key={i} className="border-t border-neutral-800">
                            {r.map((c, j) => (
                                <td key={j} className="py-2 pr-4">{c}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}


