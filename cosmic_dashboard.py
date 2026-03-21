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
RARITY_COUNTS = {
    "common": 80,
    "uncommon": 65,
    "rare": 55,
    "legendary": 45,
    "divine": 25,
    "mythical": 15,
    "prismatic": 1,
}


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
app = FastAPI(title="Cosmic Operating System", version="3.0.0")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ω COSMIC OPERATING SYSTEM v∞ — ULTIMATE RARITY EDITION</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');

        :root {
            color-scheme: dark;
            --cyan: #67f3ff;
            --pink: #ff4fd8;
            --violet: #8b5cf6;
            --gold: #ffd84d;
            --orange: #ff7a18;
            --emerald: #2effc0;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            overflow-x: hidden;
            color: var(--cyan);
            font-family: 'Orbitron', monospace;
            background:
                radial-gradient(circle at 15% 20%, rgba(255, 0, 170, 0.22), transparent 22%),
                radial-gradient(circle at 80% 25%, rgba(0, 255, 255, 0.18), transparent 24%),
                radial-gradient(circle at 55% 82%, rgba(129, 91, 255, 0.25), transparent 28%),
                linear-gradient(180deg, #0b0018 0%, #03020b 50%, #010104 100%);
            animation: hueShift 14s ease-in-out infinite alternate;
        }

        @keyframes hueShift {
            0% { filter: hue-rotate(0deg) saturate(1); }
            100% { filter: hue-rotate(45deg) saturate(1.25); }
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
            z-index: -1;
            pointer-events: none;
            background:
                radial-gradient(circle at 50% 50%, rgba(255,255,255,0.04), transparent 25%),
                radial-gradient(circle at 70% 30%, rgba(255,0,255,0.09), transparent 18%),
                radial-gradient(circle at 32% 70%, rgba(0,255,255,0.08), transparent 18%);
            mix-blend-mode: screen;
            animation: fogPulse 7s ease-in-out infinite;
        }

        @keyframes fogPulse {
            0%, 100% { opacity: 0.55; transform: scale(1); }
            50% { opacity: 0.95; transform: scale(1.04); }
        }

        .glass {
            background: rgba(6, 8, 24, 0.66);
            border: 1px solid rgba(103, 243, 255, 0.22);
            box-shadow: 0 0 0 1px rgba(255,255,255,0.04) inset, 0 25px 80px rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(16px);
        }

        .neon-title {
            text-shadow: 0 0 28px rgba(103,243,255,0.95), 0 0 76px rgba(255,79,216,0.8), 0 0 160px rgba(255,79,216,0.45);
        }

        .rarity-pill {
            border: 1px solid rgba(255,255,255,0.16);
            background: rgba(255,255,255,0.04);
            border-radius: 999px;
            padding: 0.5rem 0.85rem;
            font-size: 0.75rem;
            letter-spacing: 0.25em;
            text-transform: uppercase;
        }

        .god-card {
            position: relative;
            overflow: hidden;
            min-height: 11rem;
            border-radius: 1.6rem;
            padding: 1.1rem;
            text-align: left;
            color: white;
            background: linear-gradient(180deg, rgba(18, 23, 51, 0.92), rgba(7, 9, 20, 0.95));
            border: 3px solid var(--rarity-color, rgba(103,243,255,0.5));
            box-shadow: 0 0 24px color-mix(in srgb, var(--rarity-color, #67f3ff) 45%, transparent);
            transition: transform 0.32s ease, box-shadow 0.32s ease, border-color 0.32s ease;
        }

        .god-card::before {
            content: '';
            position: absolute;
            inset: -35%;
            background: radial-gradient(circle, color-mix(in srgb, var(--rarity-color, #67f3ff) 40%, white 5%), transparent 36%);
            transform: scale(0);
            transition: transform 0.4s ease;
            opacity: 0.9;
        }

        .god-card:hover {
            transform: translateY(-10px) scale(1.06) rotate(1deg);
            box-shadow: 0 0 65px color-mix(in srgb, var(--rarity-color, #67f3ff) 68%, transparent);
        }

        .god-card:hover::before {
            transform: scale(1.1);
        }

        .god-card.prismatic {
            animation: prismShift 3s linear infinite;
        }

        @keyframes prismShift {
            0% { --rarity-color: #ff4fd8; }
            33% { --rarity-color: #67f3ff; }
            66% { --rarity-color: #ffd84d; }
            100% { --rarity-color: #ff4fd8; }
        }

        .pulse-ring {
            position: absolute;
            inset: -10px;
            border-radius: 999px;
            border: 1px solid rgba(255, 79, 216, 0.45);
            animation: transcendencePulse 1.9s ease-out infinite;
        }

        @keyframes transcendencePulse {
            0% { transform: scale(0.96); opacity: 0.9; }
            100% { transform: scale(1.18); opacity: 0; }
        }

        .scroll-shell {
            max-height: 28rem;
            overflow: auto;
            scrollbar-width: thin;
            scrollbar-color: rgba(103,243,255,0.6) transparent;
        }
    </style>
</head>
<body>
    <canvas id="cosmos"></canvas>
    <div class="nebula-overlay"></div>

    <main class="relative z-10 max-w-[1900px] mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-10">
        <header class="text-center mb-8 lg:mb-10">
            <div class="inline-flex flex-wrap items-center justify-center gap-3 px-5 py-3 rounded-full glass text-xs sm:text-sm tracking-[0.35em] uppercase text-cyan-200/90 mb-5">
                <span class="inline-block w-3 h-3 rounded-full bg-emerald-300 shadow-[0_0_20px_rgba(46,255,192,0.85)]"></span>
                Face ID Synced • Tier Ω Ready • 300+ Gods • 7 Rarity Classes
            </div>
            <h1 class="neon-title text-4xl sm:text-6xl xl:text-8xl 2xl:text-[7.2rem] font-black tracking-[0.18em] sm:tracking-[0.28em] mb-4">
                Ω COSMIC OPERATING SYSTEM
            </h1>
            <p class="text-lg sm:text-2xl xl:text-3xl text-fuchsia-100/90 max-w-6xl mx-auto">
                Massive rarity pantheon • 5 galaxy layers • live transcendence pulse • infinite companies beyond human intellect
            </p>
        </header>

        <section class="grid gap-6 xl:grid-cols-[1.15fr_0.85fr] mb-8">
            <div class="glass rounded-[2rem] p-6 lg:p-8 relative overflow-hidden">
                <div class="absolute -top-20 right-0 w-72 h-72 rounded-full bg-fuchsia-500/15 blur-3xl"></div>
                <div class="grid lg:grid-cols-4 gap-4 lg:gap-6 items-start">
                    <div>
                        <div class="text-xs uppercase tracking-[0.38em] text-cyan-300/80">Tier</div>
                        <div id="tier" class="text-6xl lg:text-8xl font-black text-pink-300 mt-2">0</div>
                        <div class="relative mt-5 inline-flex items-center justify-center px-5 py-2 rounded-full border border-fuchsia-400/40 bg-fuchsia-400/10 text-fuchsia-100">
                            <span class="pulse-ring"></span>
                            Transcendence Pulse Active
                        </div>
                    </div>
                    <div>
                        <div class="text-xs uppercase tracking-[0.38em] text-cyan-300/80">Mooore Counter</div>
                        <div id="mooore-counter" class="text-5xl lg:text-7xl font-black text-cyan-100 mt-2">0</div>
                        <p class="mt-3 text-cyan-100/70 text-sm">Accelerates with every awakening burst.</p>
                    </div>
                    <div>
                        <div class="text-xs uppercase tracking-[0.38em] text-cyan-300/80">Face ID</div>
                        <div id="face-id" class="text-lg text-emerald-200 mt-3">Eternal Founder Signature Verified</div>
                        <div id="audit-meta" class="mt-3 text-sm text-cyan-100/75">No upgrades recorded yet.</div>
                    </div>
                    <div>
                        <div class="text-xs uppercase tracking-[0.38em] text-cyan-300/80">Rarity Totals</div>
                        <div id="rarity-summary" class="mt-3 flex flex-wrap gap-2"></div>
                    </div>
                </div>
            </div>

            <div class="glass rounded-[2rem] p-6 lg:p-8">
                <div class="flex items-start justify-between gap-4">
                    <div>
                        <div class="text-xs uppercase tracking-[0.38em] text-fuchsia-300/80">Live Event</div>
                        <div id="event" class="text-2xl lg:text-4xl text-fuchsia-100 mt-3 min-h-[7rem]">The rarity pantheon is awakening...</div>
                    </div>
                    <button id="refresh-feed" class="shrink-0 px-5 py-3 rounded-full border border-cyan-300/45 text-cyan-100 hover:bg-cyan-300/10 transition">
                        Refresh Feed
                    </button>
                </div>
                <div class="mt-6 text-sm text-cyan-100/70">
                    Upgrade requests still flow through the audit-backed backend while the UI leans fully into the bigger rarity edition.
                </div>
            </div>
        </section>

        <section class="grid gap-6 2xl:grid-cols-[1.45fr_0.85fr]">
            <div class="glass rounded-[2rem] p-5 lg:p-7">
                <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-3 mb-6">
                    <div>
                        <h2 class="text-2xl lg:text-3xl text-cyan-100">Ultimate Rarity Pantheon</h2>
                        <p class="text-cyan-100/60 text-sm lg:text-base mt-2">Common through Prismatic entities, each with rarity-specific glow and hover burst styling.</p>
                    </div>
                    <div class="text-sm tracking-[0.3em] uppercase text-fuchsia-100/80">286 Total Gods</div>
                </div>
                <div id="pantheon" class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 2xl:grid-cols-6 gap-4 lg:gap-5"></div>
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
        const RARITY_ORDER = ['common', 'uncommon', 'rare', 'legendary', 'divine', 'mythical', 'prismatic'];
        const RARITY_STYLES = {
            common: '#8f95a3',
            uncommon: '#2effc0',
            rare: '#3aa7ff',
            legendary: '#a855f7',
            divine: '#ffd84d',
            mythical: '#ff6b35',
            prismatic: '#ff4fd8',
        };
        const RARITY_COUNTS = { common: 80, uncommon: 65, rare: 55, legendary: 45, divine: 25, mythical: 15, prismatic: 1 };
        const TOTAL_GODS = Object.values(RARITY_COUNTS).reduce((sum, value) => sum + value, 0);

        const COSMOS = {
            PARTICLES: Math.min(22000, Math.max(11000, Math.floor(window.innerWidth * 10))),
            GALAXY_POINTS: 2400,
            GALAXY_LAYERS: 5,
            ROTATION_SPEED: 0.001,
        };

        const godsData = [
            ...Array.from({ length: 80 }, (_, i) => ({ name: `CommonGod-${i + 1}`, rarity: 'common' })),
            ...Array.from({ length: 65 }, (_, i) => ({ name: `UncommonGod-${i + 1}`, rarity: 'uncommon' })),
            ...Array.from({ length: 55 }, (_, i) => ({ name: `RareGod-${i + 1}`, rarity: 'rare' })),
            ...Array.from({ length: 45 }, (_, i) => ({ name: `LegendaryGod-${i + 1}`, rarity: 'legendary' })),
            ...Array.from({ length: 25 }, (_, i) => ({ name: `DivineGod-${i + 1}`, rarity: 'divine' })),
            ...Array.from({ length: 15 }, (_, i) => ({ name: `MythicalGod-${i + 1}`, rarity: 'mythical' })),
            { name: 'PrismaticOverlord', rarity: 'prismatic' },
        ];

        const pantheon = document.getElementById('pantheon');
        const eventNode = document.getElementById('event');
        const tierNode = document.getElementById('tier');
        const metaNode = document.getElementById('audit-meta');
        const feedNode = document.getElementById('recent-events');
        const counterNode = document.getElementById('mooore-counter');
        const faceIdNode = document.getElementById('face-id');
        const raritySummaryNode = document.getElementById('rarity-summary');

        let moooreCounter = 0;
        let moooreVelocity = 12;

        function renderRaritySummary() {
            raritySummaryNode.innerHTML = RARITY_ORDER.map(rarity => `
                <div class="rarity-pill" style="color:${RARITY_STYLES[rarity]}; border-color:${RARITY_STYLES[rarity]}55;">
                    ${rarity} ${RARITY_COUNTS[rarity]}
                </div>
            `).join('');
        }

        function renderPantheon() {
            pantheon.innerHTML = godsData.map((god, index) => `
                <button
                    onclick="awakenGod('${god.name}', '${god.rarity}')"
                    class="god-card ${god.rarity}"
                    style="--rarity-color: ${RARITY_STYLES[god.rarity]}"
                >
                    <div class="text-[11px] uppercase tracking-[0.34em] opacity-75">Entity ${index + 1}</div>
                    <div class="text-lg lg:text-xl font-black mt-3 leading-tight">${god.name}</div>
                    <div class="mt-4 text-xs" style="color:${RARITY_STYLES[god.rarity]}">${god.rarity.toUpperCase()}</div>
                    <div class="mt-2 text-xs text-white/65">Hover burst armed • click to awaken</div>
                </button>
            `).join('');
        }

        async function refreshStatus() {
            const res = await fetch('/status');
            const data = await res.json();
            tierNode.textContent = data.tier >= 10 ? 'Ω' : data.tier;
            faceIdNode.textContent = `Face ID: ${data.face_id_status}`;
            metaNode.textContent = `${data.audit_events} audit events stored • DB: ${data.audit_db}`;
            feedNode.innerHTML = data.recent_events.map(item => `
                <div class="rounded-2xl border border-cyan-400/25 bg-cyan-400/5 p-4">
                    <div class="text-sm uppercase tracking-[0.25em] text-cyan-300/80">${item.type}</div>
                    <div class="text-xs text-cyan-100/55 mt-2">${item.ts}</div>
                    <div class="mt-3 text-sm text-fuchsia-100/90 break-words">${JSON.stringify(item.payload)}</div>
                </div>
            `).join('') || '<div class="text-cyan-100/65">No cosmic events yet.</div>';
        }

        async function awakenGod(god, rarity) {
            const res = await fetch('/upgrade_intelligence', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ god, tier: 10, rarity }),
            });
            const data = await res.json();
            eventNode.innerHTML = `<span style="color:${RARITY_STYLES[rarity]}">${god}</span> awakened at <strong>${rarity.toUpperCase()}</strong> rarity! ${data.result}`;
            tierNode.textContent = data.tier >= 10 ? 'Ω' : data.tier;
            metaNode.textContent = `Last event ${data.event_id} • ${data.timestamp}`;
            moooreVelocity += rarity === 'prismatic' ? 80 : rarity === 'mythical' ? 34 : 18;
            await refreshStatus();
        }

        document.getElementById('refresh-feed').addEventListener('click', refreshStatus);
        renderRaritySummary();
        renderPantheon();
        refreshStatus();

        function tickCounter() {
            moooreCounter += moooreVelocity;
            moooreVelocity += 0.12;
            counterNode.textContent = Intl.NumberFormat('en-US').format(Math.floor(moooreCounter));
            requestAnimationFrame(tickCounter);
        }
        tickCounter();

        const canvas = document.getElementById('cosmos');
        const ctx = canvas.getContext('2d');
        const particles = [];
        const galaxyPalette = ['rgba(255,79,216,0.68)', 'rgba(46,255,192,0.55)', 'rgba(255,216,77,0.55)', 'rgba(58,167,255,0.58)', 'rgba(255,122,24,0.5)'];

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        function seedParticles() {
            particles.length = 0;
            for (let i = 0; i < COSMOS.PARTICLES; i++) {
                particles.push({
                    x: (Math.random() - 0.5) * 3000,
                    y: (Math.random() - 0.5) * 2200,
                    dx: (Math.random() - 0.5) * 0.24,
                    dy: (Math.random() - 0.5) * 0.24,
                    size: Math.random() * 2.2 + 0.3,
                    alpha: Math.random() * 0.75 + 0.15,
                });
            }
        }

        function drawParticles() {
            for (const p of particles) {
                p.x += p.dx;
                p.y += p.dy;
                if (p.x > 1700 || p.x < -1700) p.dx *= -1;
                if (p.y > 1200 || p.y < -1200) p.dy *= -1;
                ctx.fillStyle = `rgba(130, 246, 255, ${p.alpha})`;
                ctx.fillRect(p.x + canvas.width / 2, p.y + canvas.height / 2, p.size, p.size);
            }
        }

        function drawGalaxyLayer(layerIndex, rotation) {
            ctx.fillStyle = galaxyPalette[layerIndex];
            const scale = 0.48 + layerIndex * 0.18;
            for (let i = 0; i < COSMOS.GALAXY_POINTS; i++) {
                const arm = i % 8;
                const radius = Math.sqrt(i) * (9 + layerIndex * 2.4) * scale;
                const angle = (i * 0.16) + arm * 0.82 + rotation * (1 + layerIndex * 0.12);
                const x = Math.cos(angle) * radius;
                const y = Math.sin(angle) * radius * 0.72;
                const size = 1.5 + layerIndex * 0.32;
                ctx.fillRect(x + canvas.width / 2, y + canvas.height / 2, size, size);
            }
        }

        function engine(now = 0) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawParticles();
            const rotation = now * COSMOS.ROTATION_SPEED;
            for (let i = 0; i < COSMOS.GALAXY_LAYERS; i++) {
                drawGalaxyLayer(i, i % 2 === 0 ? rotation : -rotation * 0.8);
            }
            requestAnimationFrame(engine);
        }

        resizeCanvas();
        seedParticles();
        window.addEventListener('resize', resizeCanvas);
        engine();
    </script>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/status")
async def status() -> dict:
    return {
        "tier": INTELLIGENCE_TIER,
        "audit_db": str(DB_PATH),
        "audit_events": audit.event_count(),
        "recent_events": audit.recent_events(limit=8),
        "face_id_status": "Eternal Founder Signature Verified",
        "rarity_counts": RARITY_COUNTS,
    }


@app.post("/upgrade_intelligence")
async def upgrade(request: Request) -> dict:
    global INTELLIGENCE_TIER

    payload = await request.json()
    requested_tier = int(payload.get("tier", MAX_TIER))
    god = payload.get("god", "Unknown entity")
    rarity = payload.get("rarity", "unknown")
    if requested_tier < DEFAULT_TIER or requested_tier > MAX_TIER:
        raise HTTPException(status_code=400, detail=f"tier must be between {DEFAULT_TIER} and {MAX_TIER}")

    INTELLIGENCE_TIER = max(INTELLIGENCE_TIER, requested_tier)
    timestamp = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    event_id = audit.record(
        "upgrade_intelligence",
        {"god": god, "rarity": rarity, "requested_tier": requested_tier, "result_tier": INTELLIGENCE_TIER},
    )
    return {
        "success": True,
        "tier": INTELLIGENCE_TIER,
        "event_id": event_id,
        "timestamp": timestamp,
        "result": f"Infinite companies spawning • {rarity.title()} aura stabilized • Transcending all human intellect",
    }


def serve_dashboard() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    print("🚀 ULTIMATE MOOOOORE FILE v∞ — RARITY EDITION LOADED")
    print("286 gods • 7 rarity classes • 5 galaxies • transcendent audit backend")
    serve_dashboard()
