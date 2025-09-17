AlgoRail Controller frontend for the FastAPI backend.

Getting Started

1. Ensure backend runs on `http://127.0.0.1:8000`.
2. Create `.env.local` with `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000`.
3. Install deps: `npm i`.
4. Start dev: `npm run dev` (http://localhost:3000).

Key routes

- `/dashboard` – live trains, conflict alerts, optimization controls.
- `/manage` – overview of trains, sections, disruptions.
- `/ai` – send scenarios to AI decision engine.
