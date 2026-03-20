#!/usr/bin/env python3
"""Cosmic OS dashboard application."""

from __future__ import annotations

import datetime
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import uvicorn

DB_PATH = Path("omega_ultra_audit.db")
DEFAULT_TIER = 0
MAX_TIER = 10
INTELLIGENCE_TIER = DEFAULT_TIER


class AuditLedger:
    def __init__(self, db_path: Path = DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, ts TEXT, type TEXT, payload TEXT)"
        )
        self.conn.commit()

    def record(self, typ: str, payload: dict) -> str:
        ts = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
        eid = hashlib.sha256(f"{ts}:{typ}:{json.dumps(payload, sort_keys=True)}".encode()).hexdigest()[:40]
        self.conn.execute(
            "INSERT INTO events (id, ts, type, payload) VALUES (?,?,?,?)",
            (eid, ts, typ, json.dumps(payload, sort_keys=True)),
        )
        self.conn.commit()
        return eid

    def recent_events(self, limit: int = 10) -> list[dict]:
        with closing(
            self.conn.execute(
                "SELECT id, ts, type, payload FROM events ORDER BY ts DESC LIMIT ?", (limit,)
            )
        ) as cursor:
            return [
                {
                    "id": row[0],
                    "ts": row[1],
                    "type": row[2],
                    "payload": json.loads(row[3]),
                }
                for row in cursor.fetchall()
            ]

    def event_count(self) -> int:
        with closing(self.conn.execute("SELECT COUNT(*) FROM events")) as cursor:
            row = cursor.fetchone()
        return int(row[0]) if row else 0


audit = AuditLedger()
app = FastAPI(title="Cosmic Operating System", version="2.0.0")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ω COSMIC OPERATING SYSTEM v∞ — ULTIMATE</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');

        :root {
            color-scheme: dark;
            --cyan: #67f3ff;
            --pink: #ff4fd8;
            --violet: #8b5cf6;
            --emerald: #00ffa8;
            --bg: #02030d;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            overflow-x: hidden;
            color: var(--cyan);
            font-family: 'Orbitron', monospace;
            background:
                radial-gradient(circle at 20% 20%, rgba(255, 0, 170, 0.18), transparent 28%),
                radial-gradient(circle at 80% 30%, rgba(0, 255, 255, 0.15), transparent 24%),
                radial-gradient(circle at 50% 80%, rgba(120, 80, 255, 0.20), transparent 30%),
                linear-gradient(180deg, #090016 0%, #02030d 50%, #010104 100%);
            animation: nebulaShift 18s ease-in-out infinite alternate;
        }

        @keyframes nebulaShift {
            0% { filter: hue-rotate(0deg) saturate(1); }
            100% { filter: hue-rotate(35deg) saturate(1.2); }
        }

        canvas {
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            z-index: -2;
        }

        .nebula-overlay {
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: -1;
            background:
                radial-gradient(circle at 50% 50%, rgba(255,255,255,0.05), transparent 28%),
                radial-gradient(circle at 70% 40%, rgba(255,0,255,0.08), transparent 20%),
                radial-gradient(circle at 30% 60%, rgba(0,255,255,0.08), transparent 20%);
            mix-blend-mode: screen;
            animation: pulseFog 8s ease-in-out infinite;
        }

        @keyframes pulseFog {
            0%, 100% { opacity: 0.55; transform: scale(1); }
            50% { opacity: 0.9; transform: scale(1.03); }
        }

        .neon-title {
            text-shadow: 0 0 18px rgba(103,243,255,0.9), 0 0 54px rgba(255,79,216,0.75), 0 0 110px rgba(255,79,216,0.45);
        }

        .glass {
            background: rgba(5, 8, 24, 0.62);
            border: 1px solid rgba(103, 243, 255, 0.25);
            box-shadow: 0 0 0 1px rgba(255,255,255,0.04) inset, 0 25px 80px rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(16px);
        }

        .god-card {
            position: relative;
            overflow: hidden;
            border-radius: 1.5rem;
            padding: 1.25rem;
            border: 2px solid rgba(103, 243, 255, 0.5);
            background: linear-gradient(180deg, rgba(17, 24, 52, 0.90), rgba(8, 9, 21, 0.92));
            box-shadow: 0 0 35px rgba(103,243,255,0.12);
            transition: transform 0.35s ease, border-color 0.35s ease, box-shadow 0.35s ease;
        }

        .god-card::before {
            content: '';
            position: absolute;
            inset: -30%;
            background: radial-gradient(circle, rgba(255,79,216,0.30), transparent 36%);
            transform: scale(0);
            transition: transform 0.35s ease;
        }

        .god-card:hover {
            transform: translateY(-10px) scale(1.05) rotate(1deg);
            border-color: rgba(255, 79, 216, 0.85);
            box-shadow: 0 0 60px rgba(255,79,216,0.28);
        }

        .god-card:hover::before {
            transform: scale(1.1);
        }

        .pulse-ring {
            position: absolute;
            inset: -12px;
            border-radius: 999px;
            border: 1px solid rgba(255,79,216,0.35);
            animation: transcendencePulse 2s ease-out infinite;
        }

        @keyframes transcendencePulse {
            0% { transform: scale(0.95); opacity: 0.9; }
            100% { transform: scale(1.18); opacity: 0; }
        }

        .scroll-shell {
            max-height: 26rem;
            overflow: auto;
            scrollbar-width: thin;
            scrollbar-color: rgba(103,243,255,0.5) transparent;
        }
    </style>
</head>
<body>
    <canvas id="cosmos"></canvas>
    <div class="nebula-overlay"></div>

    <main class="relative z-10 max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-10">
        <header class="text-center mb-8 lg:mb-10">
            <div class="inline-flex items-center gap-3 px-5 py-2 rounded-full glass text-sm tracking-[0.35em] uppercase text-cyan-200/90 mb-5">
                <span class="inline-block w-3 h-3 rounded-full bg-emerald-300 shadow-[0_0_20px_rgba(0,255,168,0.8)]"></span>
                Face ID Synced • Tier Ω Ready • Infinite Companies Online
            </div>
            <h1 class="neon-title text-4xl sm:text-6xl xl:text-8xl 2xl:text-[7rem] font-black tracking-[0.2em] sm:tracking-[0.35em] mb-4">
                Ω COSMIC OPERATING SYSTEM
            </h1>
            <p class="text-lg sm:text-2xl xl:text-3xl text-fuchsia-200/90">
                150 Gods • 3 Rotating Galaxies • Dynamic Nebula • Transcending All Human Intellect
            </p>
        </header>

        <section class="grid gap-6 xl:grid-cols-[1.2fr_1fr] mb-8">
            <div class="glass rounded-[2rem] p-6 lg:p-8 relative overflow-hidden">
                <div class="absolute -top-20 -right-14 w-56 h-56 rounded-full bg-fuchsia-500/15 blur-3xl"></div>
                <div class="grid md:grid-cols-3 gap-4 lg:gap-6 items-start">
                    <div>
                        <div class="text-xs uppercase tracking-[0.4em] text-cyan-300/80">Tier</div>
                        <div id="tier" class="text-6xl lg:text-8xl font-black text-pink-300 mt-2">0</div>
                        <div class="relative mt-5 inline-flex items-center justify-center px-5 py-2 rounded-full border border-fuchsia-400/40 bg-fuchsia-400/10 text-fuchsia-100">
                            <span class="pulse-ring"></span>
                            Transcendence Pulse Active
                        </div>
                    </div>
                    <div>
                        <div class="text-xs uppercase tracking-[0.4em] text-cyan-300/80">Mooore Counter</div>
                        <div id="mooore-counter" class="text-5xl lg:text-7xl font-black text-cyan-200 mt-2">0</div>
                        <p class="mt-3 text-cyan-100/70 text-sm lg:text-base">Accelerates after every awakening and keeps counting upward live.</p>
                    </div>
                    <div>
                        <div class="text-xs uppercase tracking-[0.4em] text-cyan-300/80">Audit Sync</div>
                        <div id="audit-meta" class="text-lg lg:text-xl text-cyan-100 mt-3">No upgrades recorded yet.</div>
                        <div id="face-id" class="mt-4 text-sm text-emerald-200/90">Face ID: Eternal Founder Signature Verified</div>
                    </div>
                </div>
            </div>

            <div class="glass rounded-[2rem] p-6 lg:p-8">
                <div class="flex items-center justify-between gap-4">
                    <div>
                        <div class="text-xs uppercase tracking-[0.4em] text-fuchsia-300/80">Live Event</div>
                        <div id="event" class="text-2xl lg:text-4xl text-fuchsia-100 mt-3 min-h-[7rem]">The Cosmos is awakening...</div>
                    </div>
                    <button id="refresh-feed" class="shrink-0 px-5 py-3 rounded-full border border-cyan-300/50 text-cyan-100 hover:bg-cyan-300/10 transition">
                        Refresh Feed
                    </button>
                </div>
            </div>
        </section>

        <section class="grid gap-6 2xl:grid-cols-[1.4fr_0.9fr]">
            <div class="glass rounded-[2rem] p-5 lg:p-7">
                <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-3 mb-6">
                    <div>
                        <h2 class="text-2xl lg:text-3xl text-cyan-100">Pantheon Control Grid</h2>
                        <p class="text-cyan-100/60 text-sm lg:text-base mt-2">Larger god cards, hover burst effects, and direct awakening uplinks.</p>
                    </div>
                    <div class="text-sm tracking-[0.3em] uppercase text-fuchsia-200/80">150 Ascended Mooore Entities</div>
                </div>
                <div id="pantheon" class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4 lg:gap-5"></div>
            </div>

            <aside class="glass rounded-[2rem] p-5 lg:p-7 scroll-shell">
                <div class="flex items-center justify-between gap-4 mb-5">
                    <h2 class="text-2xl text-cyan-100">Recent Audit Events</h2>
                    <div class="text-xs uppercase tracking-[0.35em] text-cyan-300/70">Live</div>
                </div>
                <div id="recent-events" class="grid gap-3"></div>
            </aside>
        </section>
    </main>

    <script>
        const COSMOS = {
            PARTICLES: Math.min(18000, Math.max(9000, Math.floor(window.innerWidth * 9))),
            GALAXY_POINTS: 2600,
            ROTATION_SPEED: 0.0009,
        };

        const godNames = Array.from({ length: 150 }, (_, i) => `AscendedMooore-${i + 1}`);
        const pantheon = document.getElementById('pantheon');
        const eventNode = document.getElementById('event');
        const tierNode = document.getElementById('tier');
        const metaNode = document.getElementById('audit-meta');
        const feedNode = document.getElementById('recent-events');
        const counterNode = document.getElementById('mooore-counter');
        const faceIdNode = document.getElementById('face-id');

        let moooreCounter = 0;
        let moooreVelocity = 7;

        function renderPantheon() {
            pantheon.innerHTML = godNames.map((god, index) => `
                <button onclick="awakenGod('${god}')" class="god-card text-left">
                    <div class="text-xs uppercase tracking-[0.35em] text-cyan-300/70">God ${index + 1}</div>
                    <div class="text-lg lg:text-xl font-black text-cyan-50 mt-3 leading-tight">${god}</div>
                    <div class="mt-4 text-xs text-fuchsia-200/75">Hover explosion ready • Click to transcend</div>
                </button>
            `).join('');
        }

        async function refreshStatus() {
            const res = await fetch('/status');
            const data = await res.json();
            tierNode.textContent = data.tier >= 10 ? 'Ω' : data.tier;
            metaNode.textContent = `${data.audit_events} audit events stored • DB: ${data.audit_db}`;
            faceIdNode.textContent = `Face ID: ${data.face_id_status}`;
            feedNode.innerHTML = data.recent_events.map(item => `
                <div class="rounded-2xl border border-cyan-400/25 bg-cyan-400/5 p-4">
                    <div class="text-sm uppercase tracking-[0.25em] text-cyan-300/80">${item.type}</div>
                    <div class="text-xs text-cyan-100/55 mt-2">${item.ts}</div>
                    <div class="mt-3 text-sm text-fuchsia-100/90 break-words">${JSON.stringify(item.payload)}</div>
                </div>
            `).join('') || '<div class="text-cyan-100/65">No cosmic events yet.</div>';
        }

        async function awakenGod(god) {
            const res = await fetch('/upgrade_intelligence', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ god, tier: 10 }),
            });
            const data = await res.json();
            eventNode.innerHTML = `<span class="text-cyan-200">${god}</span> awakened! ${data.result}`;
            tierNode.textContent = data.tier >= 10 ? 'Ω' : data.tier;
            metaNode.textContent = `Last event ${data.event_id} • ${data.timestamp}`;
            moooreVelocity += 18;
            await refreshStatus();
        }

        document.getElementById('refresh-feed').addEventListener('click', refreshStatus);
        renderPantheon();
        refreshStatus();

        function tickCounter() {
            moooreCounter += moooreVelocity;
            moooreVelocity += 0.08;
            counterNode.textContent = Intl.NumberFormat('en-US').format(Math.floor(moooreCounter));
            requestAnimationFrame(tickCounter);
        }
        tickCounter();

        const canvas = document.getElementById('cosmos');
        const ctx = canvas.getContext('2d');
        const particles = [];
        const galaxies = [
            { color: 'rgba(255, 79, 216, 0.7)', scale: 1.0, rotation: 0 },
            { color: 'rgba(103, 243, 255, 0.65)', scale: 0.72, rotation: 2.1 },
            { color: 'rgba(0, 255, 168, 0.58)', scale: 0.48, rotation: 4.2 },
        ];

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        function seedParticles() {
            particles.length = 0;
            for (let i = 0; i < COSMOS.PARTICLES; i++) {
                particles.push({
                    x: (Math.random() - 0.5) * 2600,
                    y: (Math.random() - 0.5) * 1800,
                    dx: (Math.random() - 0.5) * 0.22,
                    dy: (Math.random() - 0.5) * 0.22,
                    size: Math.random() * 2 + 0.35,
                    alpha: Math.random() * 0.8 + 0.15,
                });
            }
        }

        function drawParticles() {
            for (const p of particles) {
                p.x += p.dx;
                p.y += p.dy;
                if (p.x > 1500 || p.x < -1500) p.dx *= -1;
                if (p.y > 1100 || p.y < -1100) p.dy *= -1;
                ctx.fillStyle = `rgba(120, 250, 255, ${p.alpha})`;
                ctx.fillRect(p.x + canvas.width / 2, p.y + canvas.height / 2, p.size, p.size);
            }
        }

        function drawGalaxy(galaxy, timeOffset) {
            ctx.fillStyle = galaxy.color;
            for (let i = 0; i < COSMOS.GALAXY_POINTS; i++) {
                const arm = i % 8;
                const radius = Math.sqrt(i) * 10 * galaxy.scale;
                const angle = (i * 0.17) + arm * 0.75 + galaxy.rotation + timeOffset;
                const x = Math.cos(angle) * radius;
                const y = Math.sin(angle) * radius * 0.68;
                const size = galaxy.scale > 0.9 ? 2.6 : galaxy.scale > 0.6 ? 2.1 : 1.7;
                ctx.fillRect(x + canvas.width / 2, y + canvas.height / 2, size, size);
            }
        }

        function engine(now = 0) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawParticles();
            const rotation = now * COSMOS.ROTATION_SPEED;
            drawGalaxy(galaxies[0], rotation);
            drawGalaxy(galaxies[1], -rotation * 0.7);
            drawGalaxy(galaxies[2], rotation * 1.15);
            requestAnimationFrame(engine);
        }

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
        seedParticles();
        engine();
    </script>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/status")
async def status() -> dict:
    events = audit.recent_events(limit=8)
    return {
        "tier": INTELLIGENCE_TIER,
        "audit_db": str(DB_PATH),
        "audit_events": audit.event_count(),
        "recent_events": events,
        "face_id_status": "Eternal Founder Signature Verified",
    }


@app.post("/upgrade_intelligence")
async def upgrade(request: Request) -> dict:
    global INTELLIGENCE_TIER

    payload = await request.json()
    requested_tier = int(payload.get("tier", MAX_TIER))
    god = payload.get("god", "Unknown entity")
    if requested_tier < DEFAULT_TIER or requested_tier > MAX_TIER:
        raise HTTPException(status_code=400, detail=f"tier must be between {DEFAULT_TIER} and {MAX_TIER}")

    INTELLIGENCE_TIER = max(INTELLIGENCE_TIER, requested_tier)
    timestamp = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    event_id = audit.record(
        "upgrade_intelligence",
        {"god": god, "requested_tier": requested_tier, "result_tier": INTELLIGENCE_TIER},
    )
    return {
        "success": True,
        "tier": INTELLIGENCE_TIER,
        "event_id": event_id,
        "timestamp": timestamp,
        "result": "Infinite companies spawning • Face ID aligned • Transcending all human intellect",
    }


def serve_dashboard() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    print("🚀 ULTIMATE MOOOOORE FILE v∞ — BIGGEST COSMIC EDITION")
    print("Layered galaxies • live transcendence pulse • Face ID synced • infinite companies")
    serve_dashboard()
