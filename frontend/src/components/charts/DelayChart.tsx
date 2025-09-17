"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type DelayDatum = { bucket: string; count: number };

export default function DelayChart({ delays }: { delays: number[] }) {
    const buckets = [0, 1, 5, 10, 15, 30, 60];
    const data: DelayDatum[] = buckets.map((b, i) => {
        const next = buckets[i + 1] ?? Infinity;
        const count = delays.filter((d) => d >= b && d < next).length;
        const label = next === Infinity ? `${b}+` : `${b}-${next - 1}`;
        return { bucket: label, count };
    });

    return (
        <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <defs>
                        <linearGradient id="delayGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#10b981" stopOpacity={0.7} />
                            <stop offset="100%" stopColor="#10b981" stopOpacity={0.1} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                    <XAxis dataKey="bucket" stroke="#9ca3af" tickLine={false} axisLine={false} />
                    <YAxis stroke="#9ca3af" tickLine={false} axisLine={false} allowDecimals={false} />
                    <Tooltip contentStyle={{ background: "#0a0a0a", border: "1px solid #262626" }} />
                    <Area type="monotone" dataKey="count" stroke="#10b981" fill="url(#delayGradient)" />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}


