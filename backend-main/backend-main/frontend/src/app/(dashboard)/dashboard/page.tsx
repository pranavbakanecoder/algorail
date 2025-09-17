"use client";

import DelayChart from "@/components/charts/DelayChart";
import LiveMap from "@/components/maps/LiveMap";
import { Badge, Card, KPI as KPITile } from "@/components/ui";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type LiveTrain = {
    train_id: string;
    current_section: string;
    position_km: number;
    speed_kmph: number;
    delay_minutes: number;
};

type Section = {
    section_id: string;
    from_station?: string;
    to_station?: string;
    length_km?: number;
};

type ConflictAlert = {
    alert_id: string;
    section_id: string;
    conflicting_trains: string[];
    alert_type: string;
    severity_level: number;
    timestamp: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export default function ControllerDashboard() {
    const [liveTrains, setLiveTrains] = useState<LiveTrain[]>([]);
    const [alerts, setAlerts] = useState<ConflictAlert[]>([]);
    const [sections, setSections] = useState<Section[]>([]);
    const [loading, setLoading] = useState(true);
    const [optimizing, setOptimizing] = useState(false);
    const [optMethod, setOptMethod] = useState("milp");
    const [optResult, setOptResult] = useState<any | null>(null);
    const [kpis, setKpis] = useState<{ total_trains: number; delayed_trains: number; average_delay_minutes: number; throughput_trains_per_hour: number; section_utilization_pct: number } | null>(null);

    useEffect(() => {
        let mounted = true;
        const fetchAll = async () => {
            try {
                setLoading(true);
                const [liveRes, alertRes] = await Promise.all([
                    fetch(`${API_BASE}/live-trains/`).then((r) => r.json()),
                    fetch(`${API_BASE}/conflict-alerts/`).then((r) => r.json()),
                ]);
                if (!mounted) return;
                setLiveTrains(liveRes);
                setAlerts(alertRes);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchAll();
        const id = setInterval(fetchAll, 5000);
        return () => {
            mounted = false;
            clearInterval(id);
        };
    }, []);

    // Fetch sections once
    useEffect(() => {
        let mounted = true;
        fetch(`${API_BASE}/sections/`).then((r) => r.json()).then((s) => { if (mounted) setSections(s || []); }).catch(() => { });
        return () => { mounted = false };
    }, []);

    // Fetch backend KPIs periodically
    useEffect(() => {
        let mounted = true;
        const fetchKpis = async () => {
            try {
                const res = await fetch(`${API_BASE}/kpis/current`);
                const json = await res.json();
                if (!mounted) return;
                setKpis(json);
            } catch {}
        };
        fetchKpis();
        const t = setInterval(fetchKpis, 10000);
        return () => { mounted = false; clearInterval(t); };
    }, []);

    const localKpis = useMemo(() => {
        const total = liveTrains.length;
        const delayed = liveTrains.filter((t) => t.delay_minutes > 0).length;
        const avgDelay = total
            ? Math.round(
                liveTrains.reduce((acc, t) => acc + t.delay_minutes, 0) / total
            )
            : 0;
        return { total, delayed, avgDelay };
    }, [liveTrains]);

    const runOptimization = async () => {
        try {
            setOptimizing(true);
            // Use fast endpoint for MILP to reduce timeouts/network issues
            let url = `${API_BASE}/optimize/?method=${optMethod}`;
            if (optMethod === "milp") url = `${API_BASE}/optimize/quick/`;
            if (optMethod === "test") url = `${API_BASE}/optimize/test/`;
            const res = await fetch(url, { headers: { "Accept": "application/json" } });
            setOptResult(await res.json());
        } catch (e) {
            console.error("Optimization request failed", e);
            setOptResult({ error: "Optimization request failed. Please try again or switch method." });
        } finally {
            setOptimizing(false);
        }
    };

    return (
        <div className="px-6 py-8 mx-auto max-w-7xl">
            <div className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl md:text-3xl font-semibold">Controller Dashboard</h1>
                    <p className="text-neutral-400 mt-1">Live overview and optimization controls</p>
                </div>
                <Link href="/" className="text-sm text-neutral-400 hover:text-neutral-200">
                    Home
                </Link>
            </div>

            <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <KPITile label="Live Trains" value={(kpis?.total_trains ?? localKpis.total).toString()} trend={`${kpis?.delayed_trains ?? localKpis.delayed} delayed`} variant="emerald" />
                <KPITile label="Average Delay (min)" value={(kpis?.average_delay_minutes ?? localKpis.avgDelay).toString()} variant="amber" />
                <KPITile label="Throughput (tph)" value={(kpis?.throughput_trains_per_hour ?? 0).toString()} variant="sky" />
                <KPITile label="Section Utilization (%)" value={(kpis?.section_utilization_pct ?? 0).toString()} variant="violet" />
            </section>

            <section className="mt-8">
                <Card title="Delay Distribution (min)">
                    <DelayChart delays={liveTrains.map((t) => t.delay_minutes)} />
                </Card>
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-2" title="Live Trains" right={<span className="text-xs text-neutral-500">Auto-refresh 5s</span>}>
                    {!loading && (
                        <div className="mb-4">
                            <LiveMap stations={[]} trains={liveTrains} />
                        </div>
                    )}
                    {loading ? (
                        <div className="text-neutral-400">Loading…</div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="text-neutral-400">
                                    <tr>
                                        <th className="text-left py-2">Train</th>
                                        <th className="text-left py-2">Section</th>
                                        <th className="text-left py-2">Position (km)</th>
                                        <th className="text-left py-2">Speed (km/h)</th>
                                        <th className="text-left py-2">Delay (min)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {liveTrains.map((t) => (
                                        <tr key={t.train_id} className="border-t border-neutral-800">
                                            <td className="py-2 font-medium">{t.train_id}</td>
                                            <td className="py-2">{t.current_section}</td>
                                            <td className="py-2">{t.position_km.toFixed(1)}</td>
                                            <td className="py-2">{t.speed_kmph.toFixed(0)}</td>
                                            <td className={`py-2 ${t.delay_minutes > 0 ? "text-amber-400" : "text-neutral-300"}`}>
                                                {t.delay_minutes}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </Card>

                <Card title="Conflict Alerts">
                    <div className="space-y-3">
                        {alerts.map((a) => (
                            <div key={a.alert_id} className="rounded-lg border border-neutral-800 p-3">
                                <div className="flex items-center justify-between">
                                    <div className="font-medium">{a.alert_type}</div>
                                    <Badge className={severityToClass(a.severity_level)}>Severity {a.severity_level}</Badge>
                                </div>
                                <div className="text-sm text-neutral-400 mt-1">
                                    Section {a.section_id} • Trains {a.conflicting_trains.join(", ")} • {new Date(a.timestamp).toLocaleTimeString()}
                                </div>
                                <AutoRecommendation competing={a.conflicting_trains} trains={liveTrains} />
                                <AlertActions alert={a} trains={liveTrains} />
                            </div>
                        ))}
                        {alerts.length === 0 && <div className="text-neutral-400">No alerts</div>}
                    </div>
                </Card>
            </section>

            <section className="mt-8">
                <Card title="Optimization" right={<span className="text-xs text-neutral-500">MILP • RL • Hybrid</span>}>
                    <div>
                        <p className="text-neutral-400 text-sm">Run schedulers: MILP, RL, or comprehensive hybrid</p>
                    </div>
                    <div className="mt-3 flex items-center gap-3">
                        <select
                            value={optMethod}
                            onChange={(e) => setOptMethod(e.target.value)}
                            className="rounded-md bg-neutral-900 border border-neutral-800 px-3 py-2"
                        >
                            <option value="milp">MILP (fast)</option>
                            <option value="rl">Reinforcement Learning</option>
                            <option value="comprehensive_hybrid">Comprehensive Hybrid</option>
                        </select>
                        <button
                            onClick={runOptimization}
                            disabled={optimizing}
                            className="rounded-md bg-emerald-600 hover:bg-emerald-500 disabled:opacity-60 px-4 py-2 font-medium"
                        >
                            {optimizing ? "Running…" : "Run"}
                        </button>
                    </div>
                    {optResult?.data && (
                        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
                            {typeof optResult.data.throughput !== "undefined" && (
                                <KPITile label="Optimized Throughput" value={`${optResult.data.throughput}`} variant="emerald" />
                            )}
                            {typeof optResult.data.total_delay !== "undefined" && (
                                <KPITile label="Total Delay (min)" value={`${Math.round(optResult.data.total_delay)}`} variant="amber" />
                            )}
                            {typeof optResult.data.computation_time !== "undefined" && (
                                <KPITile label="Compute Time (s)" value={`${optResult.data.computation_time}`} variant="sky" />
                            )}
                        </div>
                    )}
                </Card>

                {optResult && (
                    <div className="mt-4 text-sm">
                        <pre className="whitespace-pre-wrap break-words text-neutral-300">
                            {JSON.stringify(optResult, null, 2)}
                        </pre>
                    </div>
                )}
            </section>
        </div>
    );
}

// Deprecated local KPI, replaced by components/ui

function severityToClass(sev: number) {
    if (sev >= 5) return "bg-red-500/20 text-red-300 border border-red-500/30";
    if (sev >= 3) return "bg-amber-500/20 text-amber-300 border border-amber-500/30";
    return "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";
}


function AutoRecommendation({ competing, trains }: { competing: string[]; trains: LiveTrain[] }) {
    const candidates = trains.filter((t) => competing.includes(t.train_id));
    if (candidates.length === 0) return null;
    const best = [...candidates].sort((a, b) => {
        // Prefer lower delay, then higher speed
        if (a.delay_minutes !== b.delay_minutes) return a.delay_minutes - b.delay_minutes;
        return b.speed_kmph - a.speed_kmph;
    })[0];
    return (
        <div className="mt-2 text-xs text-neutral-300">
            Recommended to prioritize: <span className="text-emerald-400 font-medium">{best.train_id}</span> (delay {best.delay_minutes}m, {Math.round(best.speed_kmph)} km/h)
        </div>
    );
}



function AlertActions({ alert, trains }: { alert: ConflictAlert; trains: LiveTrain[] }) {
    const [submitting, setSubmitting] = useState<string | null>(null);

    const candidates = trains.filter((t) => alert.conflicting_trains.includes(t.train_id));
    const defaultChoice = candidates.length ? candidates.reduce((best, t) => {
        if (!best) return t;
        if (t.delay_minutes !== best.delay_minutes) return t.delay_minutes < best.delay_minutes ? t : best;
        return t.speed_kmph > best.speed_kmph ? t : best;
    }, candidates[0] as LiveTrain) : null;

    const submit = async (choice: string) => {
        try {
            setSubmitting(choice);
            const body = {
                alert_id: alert.alert_id,
                section_id: alert.section_id,
                competing_trains: alert.conflicting_trains,
                chosen_train_id: choice,
                reason: "controller-action",
                created_at: new Date().toISOString(),
            };
            await fetch(`${API_BASE}/api/audit/decision`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
        } finally {
            setSubmitting(null);
        }
    };

    if (!candidates.length) return null;
    return (
        <div className="mt-2 flex items-center gap-2">
            <button
                className="rounded-md bg-emerald-600 hover:bg-emerald-500 px-2 py-1 text-xs"
                onClick={() => defaultChoice && submit(defaultChoice.train_id)}
                disabled={!defaultChoice || !!submitting}
            >
                {submitting === (defaultChoice?.train_id || "") ? "Saving…" : `Accept ${defaultChoice?.train_id || ""}`}
            </button>
            <div className="text-xs text-neutral-500">or</div>
            {candidates.map((c) => (
                <button
                    key={c.train_id}
                    className="rounded-md bg-neutral-800 hover:bg-neutral-700 px-2 py-1 text-xs"
                    onClick={() => submit(c.train_id)}
                    disabled={!!submitting}
                >
                    {submitting === c.train_id ? "Saving…" : `Override ${c.train_id}`}
                </button>
            ))}
        </div>
    );
}

