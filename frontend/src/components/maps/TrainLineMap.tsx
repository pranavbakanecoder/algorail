"use client";

type Section = {
    section_id: string;
    from_station?: string;
    to_station?: string;
    length_km?: number;
};

type LiveTrain = {
    train_id: string;
    current_section: string;
    position_km: number;
    speed_kmph: number;
    delay_minutes: number;
};

export default function TrainLineMap({ sections, trains }: { sections: Section[]; trains: LiveTrain[] }) {
    const totalLength = sections.reduce((acc, s) => acc + (Number((s as any).length_km) || 10), 0) || 1;
    let offset = 0;

    const sectionOffsets: Record<string, { start: number; length: number }> = {};
    for (const s of sections) {
        const len = Number((s as any).length_km) || 10;
        sectionOffsets[s.section_id] = { start: offset, length: len };
        offset += len;
    }

    return (
        <div className="w-full">
            <div className="relative h-24">
                <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-2 rounded-full bg-neutral-800" />
                {sections.map((s) => {
                    const info = sectionOffsets[s.section_id];
                    const leftPct = (info.start / totalLength) * 100;
                    const widthPct = (info.length / totalLength) * 100;
                    return (
                        <div
                            key={s.section_id}
                            className="absolute top-1/2 -translate-y-1/2 h-2 bg-neutral-700"
                            style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                            title={`${s.section_id} (${(s as any).length_km ?? "?"} km)`}
                        />
                    );
                })}

                {trains.map((t) => {
                    const info = sectionOffsets[t.current_section];
                    if (!info) return null;
                    const absoluteKm = info.start + Math.max(0, Math.min(info.length, t.position_km));
                    const leftPct = (absoluteKm / totalLength) * 100;
                    const color = t.delay_minutes > 10 ? "#ef4444" : t.delay_minutes > 0 ? "#f59e0b" : "#10b981";
                    return (
                        <div key={t.train_id} className="absolute -translate-x-1/2" style={{ left: `${leftPct}%`, top: "18px" }}>
                            <div className="h-4 w-4 rounded-full border border-neutral-900 shadow" style={{ background: color }} title={`${t.train_id} • ${t.current_section} • ${t.delay_minutes}m`} />
                            <div className="mt-1 text-[10px] text-neutral-400 text-center whitespace-nowrap">{t.train_id}</div>
                        </div>
                    );
                })}
            </div>
            <div className="mt-2 flex justify-between text-[10px] text-neutral-500">
                <span>{sections[0]?.from_station || sections[0]?.section_id || "Start"}</span>
                <span>{sections[sections.length - 1]?.to_station || sections[sections.length - 1]?.section_id || "End"}</span>
            </div>
        </div>
    );
}


