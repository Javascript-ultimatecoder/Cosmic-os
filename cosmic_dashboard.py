#!/usr/bin/env python3
"""Cosmic OS dashboard application."""

from __future__ import annotations

import datetime
import json
import sqlite3
import uuid
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
        eid = uuid.uuid4().hex
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
app = FastAPI(title="Cosmic Operating System", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ω COSMIC OPERATING SYSTEM v∞</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
        body {
            background: radial-gradient(circle at center, #0a001f, #000);
            font-family: 'Orbitron', monospace;
            color: #00ffff;
            margin: 0;
            min-height: 100vh;
            overflow-x: hidden;
        }
        .neon { text-shadow: 0 0 40px #00ffff, 0 0 80px #ff00ff, 0 0 120px #ff00ff; }
        canvas { position: fixed; inset: 0; z-index: -1; }
        .god {
            transition: all 0.35s cubic-bezier(0.23,1,0.32,1);
            background: rgba(10,0,30,0.85);
            border: 2px solid #00ffff;
            box-shadow: 0 0 20px rgba(0,255,255,0.45);
        }
        .god:hover {
            transform: translateY(-8px) scale(1.08);
            border-color: #ff00ff;
            box-shadow: 0 0 50px rgba(255,0,255,0.75);
        }
    </style>
</head>
<body>
    <canvas id="cosmos"></canvas>

    <div class="max-w-7xl mx-auto p-6 md:p-8 relative z-10">
        <h1 class="text-4xl md:text-7xl font-black text-center neon tracking-[0.3em] mb-4">Ω COSMIC OPERATING SYSTEM</h1>
        <p class="text-center text-lg md:text-2xl text-purple-300">150 Gods • Infinite Companies • Transcending All Human Intellect</p>

        <div class="grid gap-6 md:grid-cols-3 my-10">
            <section class="bg-black/60 border border-cyan-400 rounded-3xl p-6">
                <div class="text-sm uppercase tracking-[0.4em] text-cyan-300">Current Tier</div>
                <div id="tier" class="text-6xl text-pink-400 mt-3 font-black">0</div>
                <p class="text-cyan-100/80 mt-3">Unlock Ω tier awakenings and stream them to the audit ledger.</p>
            </section>
            <section class="bg-black/60 border border-purple-500 rounded-3xl p-6 md:col-span-2">
                <div class="text-sm uppercase tracking-[0.4em] text-purple-300">Cosmic Event Feed</div>
                <div id="event" class="text-2xl text-purple-100 min-h-[80px] mt-3">The Cosmos is awakening...</div>
                <div id="audit-meta" class="text-sm text-cyan-200/80 mt-4">No upgrades recorded yet.</div>
            </section>
        </div>

        <section class="bg-black/50 border border-fuchsia-500 rounded-3xl p-6 mb-8">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
                <h2 class="text-2xl text-fuchsia-300">Pantheon Control Grid</h2>
                <button id="refresh-feed" class="px-4 py-2 rounded-full border border-cyan-300 text-cyan-200 hover:bg-cyan-400/10">Refresh Audit Feed</button>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-5 xl:grid-cols-6 gap-4" id="pantheon"></div>
        </section>

        <section class="bg-black/50 border border-cyan-600 rounded-3xl p-6">
            <h2 class="text-2xl text-cyan-300 mb-4">Recent Audit Events</h2>
            <div id="recent-events" class="grid gap-3 text-sm text-cyan-100/90"></div>
        </section>
    </div>

    <script>
        const COSMOS = { PARTICLES: 1800 };
        const godNames = Array.from({length: 150}, (_, i) => `AscendedMooore-${i + 1}`);
        const pantheon = document.getElementById('pantheon');
        const eventNode = document.getElementById('event');
        const tierNode = document.getElementById('tier');
        const metaNode = document.getElementById('audit-meta');
        const feedNode = document.getElementById('recent-events');

        pantheon.innerHTML = godNames.map(god => `
            <button onclick="awakenGod('${god}')" class="god p-4 rounded-2xl text-center cursor-pointer text-sm font-bold">
                ${god}
            </button>
        `).join('');

        function escapeHtml(value) {
            return value
                .replaceAll('&', '&amp;')
                .replaceAll('<', '&lt;')
                .replaceAll('>', '&gt;')
                .replaceAll("\"", '&quot;')
                .replaceAll("'", '&#39;');
        }

        async function refreshStatus() {
            const res = await fetch('/status');
            const data = await res.json();
            tierNode.textContent = data.tier >= 10 ? 'Ω' : data.tier;
            metaNode.textContent = `${data.audit_events} audit events stored • DB: ${data.audit_db}`;
            feedNode.innerHTML = data.recent_events.map(item => `
                <div class="border border-cyan-500/40 rounded-2xl p-4 bg-cyan-500/5">
                    <div class="text-cyan-300 font-bold">${escapeHtml(String(item.type))}</div>
                    <div class="text-cyan-100/70">${escapeHtml(String(item.ts))}</div>
                    <div class="mt-2 text-fuchsia-200">${escapeHtml(JSON.stringify(item.payload))}</div>
                </div>
            `).join('') || '<div class="text-cyan-100/70">No cosmic events yet.</div>';
        }

        async function awakenGod(god) {
            const res = await fetch('/upgrade_intelligence', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ god, tier: 10 })
            });
            const data = await res.json();
            eventNode.textContent = `${god} awakened! ${data.result}`;
            tierNode.textContent = data.tier >= 10 ? 'Ω' : data.tier;
            metaNode.textContent = `Last event ${data.event_id} • ${data.timestamp}`;
            await refreshStatus();
        }

        document.getElementById('refresh-feed').addEventListener('click', refreshStatus);
        refreshStatus();

        const canvas = document.getElementById('cosmos');
        const ctx = canvas.getContext('2d');
        const particles = [];

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        for (let i = 0; i < COSMOS.PARTICLES; i++) {
            particles.push({
                x: (Math.random() - 0.5) * 2000,
                y: (Math.random() - 0.5) * 2000,
                dx: (Math.random() - 0.5) * 0.4,
                dy: (Math.random() - 0.5) * 0.4,
                size: Math.random() * 2.2 + 0.4,
            });
        }

        function engine() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00ffff';
            for (const p of particles) {
                p.x += p.dx;
                p.y += p.dy;
                if (p.x > 1200 || p.x < -1200) p.dx *= -1;
                if (p.y > 1200 || p.y < -1200) p.dy *= -1;
                ctx.globalAlpha = 0.35 + (p.size / 4);
                ctx.fillRect(p.x + canvas.width / 2, p.y + canvas.height / 2, p.size, p.size);
            }
            requestAnimationFrame(engine);
        }

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
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
    god = str(payload.get("god", "Unknown entity"))
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
    print("🚀 MOOOOORE FILE v∞ — BIGGER COSMIC EDITION LOADED")
    serve_dashboard()
