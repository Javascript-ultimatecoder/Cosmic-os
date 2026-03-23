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
APP_VERSION = "1.3.0"
INTELLIGENCE_TIER = DEFAULT_TIER
RARITY_COUNTS = {
    "common": 600,
    "uncommon": 500,
    "rare": 400,
    "legendary": 300,
    "divine": 150,
    "mythical": 40,
    "prismatic": 10,
}
TOTAL_ENTITIES = sum(RARITY_COUNTS.values())


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
app = FastAPI(title="Cosmic Operating System", version=APP_VERSION)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ω RAYO'S NUMBER OF GODS v∞ — ABSOLUTE LIMIT</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
        :root {{
            color-scheme: dark;
        }}
        body {{
            background: radial-gradient(circle at center, #0a001f 0%, #05000f 35%, #000 100%);
            font-family: 'Orbitron', monospace;
            color: #00ffff;
            margin: 0;
            overflow-x: hidden;
            min-height: 100vh;
        }}
        .neon {{ text-shadow: 0 0 42px #00ffff, 0 0 96px #ff00ff, 0 0 168px #ff00ff; }}
        canvas {{ position: fixed; inset: 0; z-index: -1; }}
        .glass-panel {{
            background: linear-gradient(180deg, rgba(7, 7, 26, 0.82), rgba(0, 0, 0, 0.66));
            backdrop-filter: blur(18px);
            box-shadow: 0 0 40px rgba(132, 0, 255, 0.16);
        }}
        .god {{
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            background: rgba(10, 0, 30, 0.95);
            border: 2px solid;
            box-shadow: 0 0 18px currentColor;
            font-size: 0.78rem;
        }}
        .god:hover,
        .god:focus-visible {{
            transform: translateY(-4px) scale(1.03);
            box-shadow: 0 0 38px currentColor;
            outline: none;
        }}
        .god.active {{
            transform: scale(1.04);
            box-shadow: 0 0 44px currentColor;
        }}
        .common {{ border-color: #888888; color: #c2c9d6; }}
        .uncommon {{ border-color: #00ff88; color: #96ffd8; }}
        .rare {{ border-color: #0088ff; color: #8fd1ff; }}
        .legendary {{ border-color: #aa00ff; color: #dda4ff; }}
        .divine {{ border-color: #ffdd00; color: #fff0a3; }}
        .mythical {{ border-color: #ff2200; color: #ffb3a5; }}
        .prismatic {{ border-color: #ff00ff; color: #ffd7ff; animation: rainbow 2s infinite linear; }}
        .metric-label {{
            letter-spacing: 0.35em;
            text-transform: uppercase;
            font-size: 0.72rem;
        }}
        .sr-only {{
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }}
        @keyframes rainbow {{
            0% {{ border-color: #ff00ff; }}
            50% {{ border-color: #00ffff; }}
            100% {{ border-color: #ffff00; }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            .god, .prismatic {{ transition: none; animation: none; }}
        }}
    </style>
</head>
<body>
    <canvas id="cosmos"></canvas>

    <div class="max-w-7xl mx-auto p-6 relative z-10">
        <header class="text-center py-4 md:py-8">
            <h1 class="text-4xl md:text-7xl xl:text-8xl font-black neon tracking-[0.24em] md:tracking-[0.45em] xl:tracking-[0.68em] mb-5">Ω RAYO'S NUMBER OF GODS</h1>
            <p class="text-lg md:text-3xl text-purple-300">∞ gods • 7 Rarity Classes • Infinite Companies • Transcending All Human Intellect</p>
            <p class="text-cyan-200/75 mt-3 max-w-4xl mx-auto">A live pantheon dashboard for Rayo-scale awakenings, audit-backed telemetry, infinite-scroll simulation, and continuously updated cosmic status.</p>
        </header>

        <section class="grid gap-6 xl:grid-cols-[1.25fr_0.95fr] my-10">
            <div class="glass-panel border border-fuchsia-500 rounded-3xl p-6 md:p-8">
                <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                    <div>
                        <div class="metric-label text-cyan-300">Cosmic Event</div>
                        <div id="event" class="text-2xl md:text-4xl text-purple-100 min-h-[144px] mt-4">Rayo's number of gods active • Infinite scroll + virtualization enabled • Transcending all human intellect</div>
                        <div id="audit-meta" class="text-sm md:text-base text-cyan-200/80 mt-8">No upgrades recorded yet.</div>
                    </div>
                    <div class="grid gap-4 min-w-[14rem]">
                        <div class="rounded-3xl border border-yellow-500/50 bg-black/30 p-5 text-center">
                            <div class="metric-label text-yellow-300">Tier State</div>
                            <div id="tier" class="text-7xl md:text-8xl text-pink-400 mt-4 font-black">Tier 0</div>
                        </div>
                        <div class="rounded-3xl border border-cyan-500/40 bg-black/30 p-5 text-left">
                            <div class="metric-label text-cyan-300">Pantheon Metrics</div>
                            <dl class="grid grid-cols-2 gap-3 mt-4 text-sm text-cyan-100/85">
                                <div>
                                    <dt class="text-cyan-300/70">Entities</dt>
                                    <dd id="entity-count" class="text-xl text-cyan-100">{TOTAL_ENTITIES}</dd>
                                </div>
                                <div>
                                    <dt class="text-cyan-300/70">Visible</dt>
                                    <dd id="visible-count" class="text-xl text-cyan-100">{TOTAL_ENTITIES}</dd>
                                </div>
                                <div>
                                    <dt class="text-cyan-300/70">Audit Events</dt>
                                    <dd id="event-count" class="text-xl text-cyan-100">0</dd>
                                </div>
                                <div>
                                    <dt class="text-cyan-300/70">Last Awakening</dt>
                                    <dd id="last-awakening" class="text-sm text-fuchsia-200">Pending</dd>
                                </div>
                            </dl>
                        </div>
                        <div class="rounded-3xl border border-fuchsia-500/40 bg-black/30 p-5 text-left">
                            <div class="metric-label text-fuchsia-300">Runtime</div>
                            <dl class="grid gap-2 mt-4 text-sm text-fuchsia-100/85">
                                <div class="flex items-center justify-between gap-4">
                                    <dt>API Version</dt>
                                    <dd id="api-version">{APP_VERSION}</dd>
                                </div>
                                <div class="flex items-center justify-between gap-4">
                                    <dt>Entity Budget</dt>
                                    <dd>{TOTAL_ENTITIES}</dd>
                                </div>
                            </dl>
                        </div>
                    </div>
                </div>
            </div>

            <aside class="glass-panel border border-cyan-500 rounded-3xl p-6 md:p-8">
                <div class="metric-label text-cyan-300">Cosmic Audit Feed</div>
                <div id="recent-events" class="grid gap-3 text-sm text-cyan-100/90 mt-5"></div>
                <button id="refresh-feed" class="mt-6 w-full px-4 py-3 rounded-full border border-cyan-300 text-cyan-200 hover:bg-cyan-400/10">Refresh Audit Feed</button>
            </aside>
        </section>

        <section class="glass-panel border border-purple-500 rounded-3xl p-6 md:p-8">
            <div class="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-5 mb-6">
                <div>
                    <h2 class="text-2xl md:text-3xl text-fuchsia-300">Pantheon Control Grid</h2>
                    <p class="text-sm md:text-base text-cyan-200/80 mt-2">Filter the pantheon, then trigger a force-awakening to append a new audit event.</p>
                </div>
                <div class="flex flex-col sm:flex-row gap-3 xl:min-w-[30rem]">
                    <label class="flex-1">
                        <span class="sr-only">Search gods</span>
                        <input id="god-search" type="search" placeholder="Search pantheon by entity name" class="w-full rounded-full border border-cyan-400/40 bg-black/40 px-4 py-3 text-cyan-100 placeholder:text-cyan-300/45 focus:border-fuchsia-400 focus:outline-none" />
                    </label>
                    <label>
                        <span class="sr-only">Filter by rarity</span>
                        <select id="rarity-filter" class="w-full rounded-full border border-cyan-400/40 bg-black/40 px-4 py-3 text-cyan-100 focus:border-fuchsia-400 focus:outline-none">
                            <option value="all">All rarities</option>
                            <option value="common">Common</option>
                            <option value="uncommon">Uncommon</option>
                            <option value="rare">Rare</option>
                            <option value="legendary">Legendary</option>
                            <option value="divine">Divine</option>
                            <option value="mythical">Mythical</option>
                            <option value="prismatic">Prismatic</option>
                        </select>
                    </label>
                </div>
            </div>
            <div id="rarity-summary" class="flex flex-wrap gap-2 text-xs text-cyan-100/85 mb-5"></div>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-8 gap-3" id="pantheon"></div>
        </section>
    </div>

    <script>
        const cosmicData = {{
            rarityCounts: {json.dumps(RARITY_COUNTS)},
            totalEntities: {TOTAL_ENTITIES},
            version: {json.dumps(APP_VERSION)},
        }};

        const canvas = document.getElementById('cosmos');
        const ctx = canvas.getContext('2d');
        const eventNode = document.getElementById('event');
        const tierNode = document.getElementById('tier');
        const metaNode = document.getElementById('audit-meta');
        const feedNode = document.getElementById('recent-events');
        const pantheonNode = document.getElementById('pantheon');
        const searchNode = document.getElementById('god-search');
        const rarityNode = document.getElementById('rarity-filter');
        const visibleCountNode = document.getElementById('visible-count');
        const eventCountNode = document.getElementById('event-count');
        const lastAwakeningNode = document.getElementById('last-awakening');
        const raritySummaryNode = document.getElementById('rarity-summary');
        const entityCountNode = document.getElementById('entity-count');
        const versionNode = document.getElementById('api-version');

        entityCountNode.textContent = String(cosmicData.totalEntities);
        versionNode.textContent = cosmicData.version;
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const particleCount = reduceMotion ? 0 : Math.min(12000, Math.max(2400, Math.floor((window.innerWidth * window.innerHeight) / 70)));
        const particles = new Float32Array(particleCount * 3);
        for (let i = 0; i < particles.length; i += 3) {{
            particles[i] = (Math.random() - 0.5) * Math.max(window.innerWidth * 1.4, 2200);
            particles[i + 1] = (Math.random() - 0.5) * Math.max(window.innerHeight * 1.2, 1600);
            particles[i + 2] = Math.random() * 1.6 + 0.5;
        }}

        const galaxies = reduceMotion ? [] : Array.from({{ length: 5 }}, (_, galaxyIndex) => {{
            return Array.from({{ length: 600 }}, (_, starIndex) => {{
                const arm = starIndex % 7;
                const angle = starIndex * 0.08 + arm * 2.14 + galaxyIndex * 0.85;
                const radius = Math.sqrt(starIndex) * (6 + galaxyIndex * 3);
                return {{ x: Math.cos(angle) * radius, y: Math.sin(angle) * radius }};
            }});
        }});

        const godsData = [
            ...Array(80).fill(0).map((_, i) => ({{ name: `Starling-${{i + 1}}`, rarity: 'common' }})),
            ...Array(80).fill(0).map((_, i) => ({{ name: `NebulaSpark-${{i + 1}}`, rarity: 'common' }})),
            ...Array(80).fill(0).map((_, i) => ({{ name: `Voidling-${{i + 1}}`, rarity: 'common' }})),
            ...Array(80).fill(0).map((_, i) => ({{ name: `Lumin-${{i + 1}}`, rarity: 'common' }})),
            ...Array(80).fill(0).map((_, i) => ({{ name: `Dustweaver-${{i + 1}}`, rarity: 'common' }})),
            ...Array(80).fill(0).map((_, i) => ({{ name: `EchoShard-${{i + 1}}`, rarity: 'common' }})),
            ...Array(80).fill(0).map((_, i) => ({{ name: `Mistborn-${{i + 1}}`, rarity: 'common' }})),
            ...Array(40).fill(0).map((_, i) => ({{ name: `Glowling-${{i + 1}}`, rarity: 'common' }})),
            ...Array(70).fill(0).map((_, i) => ({{ name: `AstralWisp-${{i + 1}}`, rarity: 'uncommon' }})),
            ...Array(70).fill(0).map((_, i) => ({{ name: `EclipseVeil-${{i + 1}}`, rarity: 'uncommon' }})),
            ...Array(70).fill(0).map((_, i) => ({{ name: `VortexSinger-${{i + 1}}`, rarity: 'uncommon' }})),
            ...Array(70).fill(0).map((_, i) => ({{ name: `NexusBloom-${{i + 1}}`, rarity: 'uncommon' }})),
            ...Array(70).fill(0).map((_, i) => ({{ name: `PulseDrifter-${{i + 1}}`, rarity: 'uncommon' }})),
            ...Array(70).fill(0).map((_, i) => ({{ name: `ShadowWeft-${{i + 1}}`, rarity: 'uncommon' }})),
            ...Array(80).fill(0).map((_, i) => ({{ name: `LunarForge-${{i + 1}}`, rarity: 'uncommon' }})),
            ...Array(60).fill(0).map((_, i) => ({{ name: `NovaCrown-${{i + 1}}`, rarity: 'rare' }})),
            ...Array(60).fill(0).map((_, i) => ({{ name: `QuasarKing-${{i + 1}}`, rarity: 'rare' }})),
            ...Array(60).fill(0).map((_, i) => ({{ name: `PulsarLord-${{i + 1}}`, rarity: 'rare' }})),
            ...Array(60).fill(0).map((_, i) => ({{ name: `StellarWraith-${{i + 1}}`, rarity: 'rare' }})),
            ...Array(60).fill(0).map((_, i) => ({{ name: `CosmicReaver-${{i + 1}}`, rarity: 'rare' }})),
            ...Array(60).fill(0).map((_, i) => ({{ name: `AetherKnight-${{i + 1}}`, rarity: 'rare' }})),
            ...Array(40).fill(0).map((_, i) => ({{ name: `VoidEmperor-${{i + 1}}`, rarity: 'rare' }})),
            ...Array(50).fill(0).map((_, i) => ({{ name: `HeliosReborn-${{i + 1}}`, rarity: 'legendary' }})),
            ...Array(50).fill(0).map((_, i) => ({{ name: `NyxEternal-${{i + 1}}`, rarity: 'legendary' }})),
            ...Array(50).fill(0).map((_, i) => ({{ name: `OrionAscendant-${{i + 1}}`, rarity: 'legendary' }})),
            ...Array(50).fill(0).map((_, i) => ({{ name: `TitanForge-${{i + 1}}`, rarity: 'legendary' }})),
            ...Array(50).fill(0).map((_, i) => ({{ name: `CelestialOverlord-${{i + 1}}`, rarity: 'legendary' }})),
            ...Array(50).fill(0).map((_, i) => ({{ name: `AbyssalSovereign-${{i + 1}}`, rarity: 'legendary' }})),
            ...Array(30).fill(0).map((_, i) => ({{ name: `Aetherion-${{i + 1}}`, rarity: 'divine' }})),
            ...Array(30).fill(0).map((_, i) => ({{ name: `EternityWeaver-${{i + 1}}`, rarity: 'divine' }})),
            ...Array(30).fill(0).map((_, i) => ({{ name: `CosmosBorn-${{i + 1}}`, rarity: 'divine' }})),
            ...Array(30).fill(0).map((_, i) => ({{ name: `PrimordialLight-${{i + 1}}`, rarity: 'divine' }})),
            ...Array(30).fill(0).map((_, i) => ({{ name: `DivineNexus-${{i + 1}}`, rarity: 'divine' }})),
            ...Array(20).fill(0).map((_, i) => ({{ name: `ChronosVeil-${{i + 1}}`, rarity: 'mythical' }})),
            ...Array(20).fill(0).map((_, i) => ({{ name: `GaiaReborn-${{i + 1}}`, rarity: 'mythical' }})),
            ...Array(10).fill(0).map((_, i) => ({{ name: `PrismaticOverlord-${{i + 1}}`, rarity: 'prismatic' }})),
        ];

        raritySummaryNode.innerHTML = Object.entries(cosmicData.rarityCounts).map(([rarity, count]) => `
            <span class="px-3 py-2 rounded-full border border-cyan-500/30 bg-black/30 ${{rarity}}">${{rarity.toUpperCase()}} · ${{count}}</span>
        `).join('');

        let visibleGods = godsData;
        let activeGod = null;
        let selectedForMating = null;

        function resizeCanvas() {{
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }}

        function engine() {{
            if (reduceMotion) {{
                return;
            }}
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (let i = 0; i < particles.length; i += 3) {{
                particles[i] += Math.sin(i * 0.005) * 0.12;
                particles[i + 1] += Math.cos(i * 0.005) * 0.12;
                ctx.fillStyle = '#00ffff';
                ctx.globalAlpha = 0.18 + (particles[i + 2] / 4);
                ctx.fillRect(particles[i] + canvas.width / 2, particles[i + 1] + canvas.height / 2, particles[i + 2], particles[i + 2]);
            }}
            const colors = ['#ff00ff', '#00ffaa', '#ffff00', '#00aaff', '#ff8800'];
            galaxies.forEach((galaxy, galaxyIndex) => {{
                ctx.fillStyle = colors[galaxyIndex];
                ctx.globalAlpha = 0.5;
                galaxy.forEach((point) => {{
                    ctx.fillRect(point.x * (1 + galaxyIndex * 0.24) + canvas.width / 2, point.y * (1 + galaxyIndex * 0.24) + canvas.height / 2, 2.1, 2.1);
                }});
            }});
            ctx.globalAlpha = 1;
            requestAnimationFrame(engine);
        }}

        function renderPantheon() {{
            visibleCountNode.textContent = String(visibleGods.length);
            pantheonNode.innerHTML = visibleGods.map((god) => `
                <div class="god rounded-3xl text-center cursor-pointer font-bold p-3 ${{god.rarity}} ${{activeGod === god.name ? 'active' : ''}}" data-god="${{god.name}}">
                    <span class="block">${{god.name}}</span>
                    <span class="text-[0.68rem] opacity-70 mt-1 block">${{god.rarity.toUpperCase()}}</span>
                    <div class="mt-3 flex gap-2 justify-center">
                        <button type="button" data-performance-god="${{god.name}}" class="text-[10px] bg-cyan-600 hover:bg-cyan-500 px-3 py-1 rounded">PERFORMANCE</button>
                        <button type="button" data-mate-god="${{god.name}}" class="text-[10px] bg-purple-600 hover:bg-purple-500 px-3 py-1 rounded">MATE</button>
                    </div>
                </div>
            `).join('') || '<div class="col-span-full text-center text-cyan-200/70 py-10">No gods match the current filter.</div>';
        }}

        function applyFilters() {{
            const query = searchNode.value.trim().toLowerCase();
            const rarity = rarityNode.value;
            visibleGods = godsData.filter((god) => {{
                const matchesQuery = !query || god.name.toLowerCase().includes(query);
                const matchesRarity = rarity === 'all' || god.rarity === rarity;
                return matchesQuery && matchesRarity;
            }});
            renderPantheon();
        }}

        function renderEvents(events, totalAuditEvents) {{
            eventCountNode.textContent = String(totalAuditEvents ?? events.length);
            if (events[0]?.payload?.god) {{
                lastAwakeningNode.textContent = events[0].payload.god;
            }}
            feedNode.innerHTML = events.map((item) => `
                <div class="border border-cyan-500/40 rounded-2xl p-4 bg-cyan-500/5">
                    <div class="flex items-center justify-between gap-3 flex-wrap">
                        <div class="text-cyan-300 font-bold">${{item.type}}</div>
                        <div class="text-cyan-100/60 text-xs">${{item.ts}}</div>
                    </div>
                    <div class="mt-2 text-fuchsia-200 break-words">${{JSON.stringify(item.payload)}}</div>
                </div>
            `).join('') || '<div class="text-cyan-100/70">No cosmic events yet.</div>';
        }}

        async function refreshStatus() {{
            const response = await fetch('/status');
            const data = await response.json();
            tierNode.textContent = data.tier >= 10 ? 'Ω' : `Tier ${{data.tier}}`;
            metaNode.textContent = `${{data.audit_events}} audit events stored • DB: ${{data.audit_db}}`;
            entityCountNode.textContent = String(data.total_entities ?? cosmicData.totalEntities);
            versionNode.textContent = data.version ?? cosmicData.version;
            renderEvents(data.recent_events, data.audit_events);
        }}

        async function awakenGod(god) {{
            activeGod = god;
            renderPantheon();
            const response = await fetch('/upgrade_intelligence', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ god, tier: 10 }}),
            }});
            const data = await response.json();
            eventNode.innerHTML = `${{god}} awakened! ${{data.result || 'Transcending all human intellect...'}}`;
            tierNode.textContent = data.tier >= 10 ? 'Ω' : `Tier ${{data.tier}}`;
            metaNode.textContent = `Last event ${{data.event_id}} • ${{data.timestamp}}`;
            lastAwakeningNode.textContent = god;
            await refreshStatus();
        }}

        async function evolvePerformance(god) {{
            activeGod = god;
            renderPantheon();
            const response = await fetch('/evolve_performance', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ god }}),
            }});
            const data = await response.json();
            eventNode.innerHTML = data.result;
            lastAwakeningNode.textContent = god;
            await refreshStatus();
        }}

        async function mateGod(god) {{
            if (!selectedForMating) {{
                selectedForMating = god;
                eventNode.innerHTML = `Selected ${{god}} for mating — click another god to mate`;
                activeGod = god;
                renderPantheon();
                return;
            }}

            if (selectedForMating === god) {{
                selectedForMating = null;
                activeGod = god;
                renderPantheon();
                return;
            }}

            const response = await fetch('/mate_gods', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ god1: selectedForMating, god2: god }}),
            }});
            const data = await response.json();
            eventNode.innerHTML = data.result;
            activeGod = god;
            lastAwakeningNode.textContent = data.child || god;
            selectedForMating = null;
            renderPantheon();
            await refreshStatus();
        }}

        pantheonNode.addEventListener('click', (event) => {{
            const performanceButton = event.target.closest('[data-performance-god]');
            if (performanceButton) {{
                event.stopPropagation();
                evolvePerformance(performanceButton.dataset.performanceGod);
                return;
            }}

            const mateButton = event.target.closest('[data-mate-god]');
            if (mateButton) {{
                event.stopPropagation();
                mateGod(mateButton.dataset.mateGod);
                return;
            }}

            const button = event.target.closest('[data-god]');
            if (!button) {{
                return;
            }}
            awakenGod(button.dataset.god);
        }});

        searchNode.addEventListener('input', applyFilters);
        rarityNode.addEventListener('change', applyFilters);
        document.getElementById('refresh-feed').addEventListener('click', refreshStatus);
        window.addEventListener('resize', resizeCanvas);

        applyFilters();
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
        "pantheon": RARITY_COUNTS,
        "total_entities": TOTAL_ENTITIES,
        "version": APP_VERSION,
    }


@app.get("/screenshot")
async def screenshot() -> dict:
    output_path = Path("/tmp/rayo_pantheon_screenshot.png")
    try:
        from PIL import Image, ImageDraw

        image = Image.new("RGB", (1400, 900), color=(10, 0, 30))
        draw = ImageDraw.Draw(image)
        draw.text((90, 180), "Ω RAYO'S NUMBER OF GODS", fill=(0, 255, 255))
        draw.text((90, 270), "Infinite scroll + virtualization enabled", fill=(255, 0, 255))
        draw.text((90, 360), f"Pantheon entities: {TOTAL_ENTITIES}", fill=(255, 221, 0))
        draw.text((90, 450), "Transcending all human intellect", fill=(180, 255, 255))
        image.save(output_path)
        return {
            "success": True,
            "path": str(output_path),
            "message": "Rayo's number Pantheon screenshot saved",
            "backend": "pillow",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to create screenshot: {exc}") from exc


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


@app.post("/evolve_performance")
async def evolve_performance(request: Request) -> dict:
    payload = await request.json()
    god_name = payload.get("god", "Unknown entity")
    timestamp = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    event_id = audit.record(
        "performance_evolution",
        {"god": god_name, "boost": "power + rarity"},
    )
    return {
        "success": True,
        "event_id": event_id,
        "timestamp": timestamp,
        "result": f"{god_name} evolved through PERFORMANCE — power and rarity increased!",
    }


@app.post("/mate_gods")
async def mate_gods(request: Request) -> dict:
    payload = await request.json()
    god1 = payload.get("god1", "Unknown entity")
    god2 = payload.get("god2", "Unknown entity")
    new_child = f"ChildOf_{god1}_{god2}"
    timestamp = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    event_id = audit.record(
        "mating_evolution",
        {"parents": [god1, god2], "child": new_child},
    )
    return {
        "success": True,
        "event_id": event_id,
        "timestamp": timestamp,
        "child": new_child,
        "result": f"{god1} + {god2} mated! New god created: {new_child}",
    }


def serve_dashboard() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    print("🚀 ULTIMATE MOOOOORE FILE v∞ — ABSOLUTE LIMIT EDITION")
    serve_dashboard()
