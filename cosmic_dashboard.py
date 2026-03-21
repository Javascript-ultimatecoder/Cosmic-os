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


audit = AuditLedger()
app = FastAPI(title="Cosmic Operating System", version="1.1.0")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ω COSMIC OPERATING SYSTEM v∞ — ABSOLUTE LIMIT</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
        body {
            background: radial-gradient(circle at center, #0a001f, #000);
            font-family: 'Orbitron', monospace;
            color: #00ffff;
            margin: 0;
            overflow-x: hidden;
            min-height: 100vh;
        }
        .neon { text-shadow: 0 0 60px #00ffff, 0 0 120px #ff00ff, 0 0 180px #ff00ff; }
        canvas { position: fixed; top: 0; left: 0; z-index: -1; }
        .god {
            transition: all 0.6s cubic-bezier(0.23,1,0.32,1);
            background: rgba(10,0,30,0.95);
            border: 3px solid;
            box-shadow: 0 0 25px currentColor;
            font-size: 0.75rem;
            padding: 10px 8px;
            margin: 3px;
        }
        .god:hover {
            transform: scale(1.18) rotate(4deg);
            box-shadow: 0 0 120px currentColor;
        }
        .common { border-color: #888888; color: #b9c2cf; }
        .uncommon { border-color: #00ff88; color: #8dffd0; }
        .rare { border-color: #0088ff; color: #88d0ff; }
        .legendary { border-color: #aa00ff; color: #e1a6ff; }
        .divine { border-color: #ffdd00; color: #fff2a6; }
        .mythical { border-color: #ff2200; color: #ffb2a6; }
        .prismatic { border-color: #ff00ff; color: #ffd8ff; animation: rainbow 2s infinite; }
        .glass-panel {
            background: rgba(0, 0, 0, 0.65);
            backdrop-filter: blur(12px);
            box-shadow: 0 0 40px rgba(132, 0, 255, 0.18);
        }
        @keyframes rainbow {
            0% { border-color: #ff00ff; }
            50% { border-color: #00ffff; }
            100% { border-color: #ffff00; }
        }
    </style>
</head>
<body>
    <canvas id="cosmos"></canvas>

    <div class="max-w-7xl mx-auto p-6 relative z-10">
        <h1 class="text-4xl md:text-7xl xl:text-8xl font-black text-center neon tracking-[0.3em] md:tracking-[0.55em] xl:tracking-[0.8em] mb-6">Ω COSMIC OPERATING SYSTEM</h1>
        <p class="text-center text-lg md:text-3xl text-purple-400">320 Gods • 7 Rarity Classes • Infinite Companies</p>

        <div class="grid gap-6 lg:grid-cols-[1.4fr_0.9fr] my-10">
            <section class="glass-panel border border-fuchsia-500 rounded-3xl p-6 md:p-8">
                <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                    <div>
                        <div class="text-sm uppercase tracking-[0.45em] text-cyan-300">Cosmic Event</div>
                        <div id="event" class="text-2xl md:text-4xl text-purple-200 min-h-[160px] mt-4">The Cosmos is awakening...</div>
                    </div>
                    <div class="text-center md:text-right min-w-[10rem]">
                        <div class="text-sm uppercase tracking-[0.45em] text-yellow-300">Tier State</div>
                        <div id="tier" class="text-7xl md:text-8xl text-pink-400 mt-4 font-black">Tier 0</div>
                    </div>
                </div>
                <div id="audit-meta" class="text-sm md:text-base text-cyan-200/80 mt-8">No upgrades recorded yet.</div>
            </section>

            <section class="glass-panel border border-cyan-500 rounded-3xl p-6 md:p-8">
                <div class="text-sm uppercase tracking-[0.45em] text-cyan-300">Cosmic Audit Feed</div>
                <div id="recent-events" class="grid gap-3 text-sm text-cyan-100/90 mt-5"></div>
                <button id="refresh-feed" class="mt-6 w-full px-4 py-3 rounded-full border border-cyan-300 text-cyan-200 hover:bg-cyan-400/10">Refresh Audit Feed</button>
            </section>
        </div>

        <section class="glass-panel border border-purple-500 rounded-3xl p-6 md:p-8">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
                <h2 class="text-2xl md:text-3xl text-fuchsia-300">Pantheon Control Grid</h2>
                <div class="text-sm md:text-base text-cyan-200/80">Select an entity to force an Ω-tier awakening and append it to the audit ledger.</div>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 xl:grid-cols-8 gap-3 my-4" id="pantheon"></div>
        </section>
    </div>

    <script>
        const canvas = document.getElementById('cosmos');
        const ctx = canvas.getContext('2d');
        const eventNode = document.getElementById('event');
        const tierNode = document.getElementById('tier');
        const metaNode = document.getElementById('audit-meta');
        const feedNode = document.getElementById('recent-events');
        const pantheonNode = document.getElementById('pantheon');

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const particleCount = 24000;
        const particles = new Float32Array(particleCount * 3);
        for (let i = 0; i < particles.length; i += 3) {
            particles[i] = (Math.random() - 0.5) * Math.max(window.innerWidth * 1.4, 2200);
            particles[i + 1] = (Math.random() - 0.5) * Math.max(window.innerHeight * 1.4, 1800);
            particles[i + 2] = Math.random() * 1.8 + 0.6;
        }

        const galaxies = [];
        for (let g = 0; g < 5; g++) {
            const stars = [];
            for (let i = 0; i < 1200; i++) {
                const arm = i % 8;
                const angle = i * 0.07 + arm * 2.2 + g * 1.1;
                const radius = Math.sqrt(i) * (7 + g * 3);
                stars.push({ x: Math.cos(angle) * radius, y: Math.sin(angle) * radius });
            }
            galaxies.push(stars);
        }

        function engine() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (let i = 0; i < particles.length; i += 3) {
                particles[i] += Math.sin(i * 0.005) * 0.18;
                particles[i + 1] += Math.cos(i * 0.005) * 0.15;
                ctx.fillStyle = '#00ffff';
                ctx.globalAlpha = 0.2 + (particles[i + 2] / 4);
                ctx.fillRect(particles[i] + canvas.width / 2, particles[i + 1] + canvas.height / 2, particles[i + 2], particles[i + 2]);
            }
            const colors = ['#ff00ff', '#00ffaa', '#ffff00', '#00aaff', '#ff8800'];
            for (let g = 0; g < galaxies.length; g++) {
                ctx.fillStyle = colors[g];
                ctx.globalAlpha = 0.55;
                galaxies[g].forEach((p) => {
                    ctx.fillRect(p.x * (1 + g * 0.25) + canvas.width / 2, p.y * (1 + g * 0.25) + canvas.height / 2, 2.5, 2.5);
                });
            }
            ctx.globalAlpha = 1;
            requestAnimationFrame(engine);
        }

        const godsData = [
            ...Array(80).fill(0).map((_, i) => ({ name: `CommonGod-${i + 1}`, rarity: 'common' })),
            ...Array(70).fill(0).map((_, i) => ({ name: `UncommonGod-${i + 1}`, rarity: 'uncommon' })),
            ...Array(60).fill(0).map((_, i) => ({ name: `RareGod-${i + 1}`, rarity: 'rare' })),
            ...Array(50).fill(0).map((_, i) => ({ name: `LegendaryGod-${i + 1}`, rarity: 'legendary' })),
            ...Array(30).fill(0).map((_, i) => ({ name: `DivineGod-${i + 1}`, rarity: 'divine' })),
            ...Array(20).fill(0).map((_, i) => ({ name: `MythicalGod-${i + 1}`, rarity: 'mythical' })),
            ...Array(10).fill(0).map((_, i) => ({ name: `PrismaticGod-${i + 1}`, rarity: 'prismatic' }))
        ];

        pantheonNode.innerHTML = godsData.map((god) => `
            <button onclick="awakenGod('${god.name}')" class="god rounded-3xl text-center cursor-pointer text-sm font-bold ${god.rarity}">
                ${god.name}<br><span class="text-xs opacity-70">${god.rarity.toUpperCase()}</span>
            </button>
        `).join('');

        function renderEvents(events) {
            feedNode.innerHTML = events.map((item) => `
                <div class="border border-cyan-500/40 rounded-2xl p-4 bg-cyan-500/5">
                    <div class="flex items-center justify-between gap-3 flex-wrap">
                        <div class="text-cyan-300 font-bold">${item.type}</div>
                        <div class="text-cyan-100/60 text-xs">${item.ts}</div>
                    </div>
                    <div class="mt-2 text-fuchsia-200 break-words">${JSON.stringify(item.payload)}</div>
                </div>
            `).join('') || '<div class="text-cyan-100/70">No cosmic events yet.</div>';
        }

        async function refreshStatus() {
            const res = await fetch('/status');
            const data = await res.json();
            tierNode.textContent = data.tier >= 10 ? 'Ω' : `Tier ${data.tier}`;
            metaNode.textContent = `${data.audit_events} audit events stored • DB: ${data.audit_db}`;
            renderEvents(data.recent_events);
        }

        async function awakenGod(god) {
            const res = await fetch('/upgrade_intelligence', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ god, tier: 10 })
            });
            const data = await res.json();
            eventNode.innerHTML = `${god} awakened! ${data.result || 'Transcending all human intellect...'}`;
            tierNode.textContent = data.tier >= 10 ? 'Ω' : `Tier ${data.tier}`;
            metaNode.textContent = `Last event ${data.event_id} • ${data.timestamp}`;
            await refreshStatus();
        }

        document.getElementById('refresh-feed').addEventListener('click', refreshStatus);
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });

        refreshStatus();
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
        "audit_events": len(audit.recent_events(limit=1000)),
        "recent_events": events,
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
        "result": "Infinite companies spawning • Transcending all human intellect",
    }


def serve_dashboard() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    print("🚀 ULTIMATE MOOOOORE FILE v∞ — ABSOLUTE LIMIT EDITION")
    serve_dashboard()
