"use client";

import Script from "next/script";
import { useEffect, useRef, useState } from "react";

type Station = { station_id: string; display_name: string; lat?: number; lon?: number };
type LiveTrain = { train_id: string; current_section: string; position_km: number; speed_kmph: number; delay_minutes: number };

export default function LiveMap({ stations, trains }: { stations: Station[]; trains: LiveTrain[] }) {
    const mapRef = useRef<HTMLDivElement | null>(null);
    const mapInstance = useRef<any | null>(null);
    const markersRef = useRef<Record<string, any>>({});
    const [libReady, setLibReady] = useState(false);
    const [mapReady, setMapReady] = useState(false);

    useEffect(() => {
        // ensure CSS loaded for maplibre when using CDN
        const id = "maplibre-style-css";
        if (!document.getElementById(id)) {
            const link = document.createElement("link");
            link.id = id;
            link.rel = "stylesheet";
            link.href = "https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css";
            document.head.appendChild(link);
        }
    }, []);

    useEffect(() => {
        const g: any = (globalThis as any);
        if (!mapRef.current || mapInstance.current) return;
        if (!g.maplibregl) return; // wait for script
        const m = new g.maplibregl.Map({
            container: mapRef.current,
            style: "https://demotiles.maplibre.org/style.json",
            center: [77.5946, 12.9716],
            zoom: 5,
            attributionControl: false,
        });
        mapInstance.current = m;
        m.addControl(new g.maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
        const onLoad = () => setMapReady(true);
        m.on("load", onLoad);
        return () => { m.remove(); };
    }, [libReady]);

    useEffect(() => {
        const m = mapInstance.current;
        if (!m || !mapReady) return;

        // Station dots (only once; naive: clear and add)
        // Remove previous station layer if exists
        const layerId = "stations-layer";
        if (m.getLayer(layerId)) {
            m.removeLayer(layerId);
            if (m.getSource(layerId)) m.removeSource(layerId);
        }
        const features = stations
            .filter((s) => typeof s.lon === "number" && typeof s.lat === "number")
            .map((s) => ({ type: "Feature", geometry: { type: "Point", coordinates: [s.lon!, s.lat!] }, properties: { name: s.display_name } }));
        m.addSource(layerId, { type: "geojson", data: { type: "FeatureCollection", features } });
        m.addLayer({ id: layerId, type: "circle", source: layerId, paint: { "circle-radius": 3, "circle-color": "#60a5fa" } });
    }, [stations, mapReady]);

    useEffect(() => {
        const m = mapInstance.current;
        if (!m || !mapReady) return;

        // Update or create train markers
        trains.forEach((t) => {
            // For demo: randomly place near center if no station coords; otherwise, interpolate between two stations if available
            const color = t.delay_minutes > 10 ? "#ef4444" : t.delay_minutes > 0 ? "#f59e0b" : "#10b981";
            let lng = 77.5946;
            let lat = 12.9716;
            const from = stations.find((s) => s.station_id === "from:" + t.current_section);
            const to = stations.find((s) => s.station_id === "to:" + t.current_section);
            if (from && to && typeof from.lon === "number" && typeof to.lon === "number") {
                const frac = Math.max(0, Math.min(1, t.position_km / 50));
                lng = from.lon + (to.lon - from.lon) * frac;
                lat = from.lat! + (to.lat! - from.lat!) * frac;
            }
            let marker = markersRef.current[t.train_id];
            if (!marker) {
                const el = document.createElement("div");
                el.style.width = "10px";
                el.style.height = "10px";
                el.style.borderRadius = "9999px";
                el.style.border = "2px solid #111827";
                el.style.boxShadow = "0 0 0 2px rgba(0,0,0,0.2)";
                el.style.background = color;
                marker = new (globalThis as any).maplibregl.Marker({ element: el }).setLngLat([lng, lat]).addTo(m);
                markersRef.current[t.train_id] = marker;
            } else {
                (marker.getElement().style.background as any) = color;
                marker.setLngLat([lng, lat]);
            }
        });
    }, [trains, stations, mapReady]);

    return (
        <>
            <Script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js" strategy="afterInteractive" onLoad={() => setLibReady(true)} />
            <div ref={mapRef} className="h-72 w-full rounded-lg overflow-hidden border border-neutral-800" />
        </>
    );
}


