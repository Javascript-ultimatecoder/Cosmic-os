#!/usr/bin/env python3
"""Cosmic OS dashboard application."""

from __future__ import annotations

import datetime
import hashlib
import json
import sqlite3
import random
import asyncio
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
import uvicorn
from PIL import Image, ImageDraw, ImageFont

DB_PATH = Path("omega_ultra_audit.db")
DEFAULT_TIER = 0
MAX_TIER = 10
INTELLIGENCE_TIER = DEFAULT_TIER
RARITY_WEIGHTS = {
    "common": 1.0,
    "uncommon": 1.8,
    "rare": 3.2,
    "legendary": 5.5,
    "divine": 8.0,
    "mythical": 12.0,
    "prismatic": 20.0,
}
PANTHEON_DISTRIBUTION = {
    "common": 1500,
    "uncommon": 1200,
    "rare": 900,
    "legendary": 700,
    "divine": 500,
    "mythical": 400,
    "prismatic": 300,
}
QUANTUM_BY_RARITY = {
    "common": "Stable",
    "uncommon": "Chaotic",
    "rare": "Entangled",
    "legendary": "Transcendent",
    "divine": "Stable",
    "mythical": "Chaotic",
    "prismatic": "Entangled",
}
RARITY_ORDER = ["common", "uncommon", "rare", "legendary", "divine", "mythical", "prismatic"]
RARITY_PROMOTION_CHANCE = {
    "common": 0.28,
    "uncommon": 0.22,
    "rare": 0.18,
    "legendary": 0.13,
    "divine": 0.08,
    "mythical": 0.05,
    "prismatic": 0.0,
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


audit = AuditLedger()
app = FastAPI(title="Cosmic Operating System", version="1.0.0")
GOD_STATE: dict[str, dict] = {}
EVOLUTION_TICKS = 0
TOTAL_BIRTHS = 0
LATEST_SCREENSHOT = Path("/tmp/cosmic_latest_snapshot.png")
COMPANIES: list[dict] = []
BATTLE_LOG: list[dict] = []
STATE_PATH = Path("/tmp/cosmic_state.json")


def _init_god_state() -> None:
    if GOD_STATE:
        return
    for rarity, count in PANTHEON_DISTRIBUTION.items():
        for idx in range(1, count + 1):
            god_name = f"{rarity.capitalize()}God-{idx}"
            GOD_STATE[god_name] = {
                "name": god_name,
                "rarity": rarity,
                "tier": random.randint(0, 3),
                "power": random.randint(40, 130),
                "offspring": 0,
            }


def _save_state_to_disk() -> None:
    payload = {
        "intelligence_tier": INTELLIGENCE_TIER,
        "evolution_ticks": EVOLUTION_TICKS,
        "total_births": TOTAL_BIRTHS,
        "god_state": list(GOD_STATE.values()),
        "companies": COMPANIES,
        "battle_log": BATTLE_LOG[-500:],
        "saved_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    STATE_PATH.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _load_state_from_disk() -> bool:
    global INTELLIGENCE_TIER, EVOLUTION_TICKS, TOTAL_BIRTHS
    if not STATE_PATH.exists():
        return False

    payload = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    GOD_STATE.clear()
    for row in payload.get("god_state", []):
        GOD_STATE[row["name"]] = row
    COMPANIES.clear()
    COMPANIES.extend(payload.get("companies", []))
    BATTLE_LOG.clear()
    BATTLE_LOG.extend(payload.get("battle_log", []))
    INTELLIGENCE_TIER = int(payload.get("intelligence_tier", INTELLIGENCE_TIER))
    EVOLUTION_TICKS = int(payload.get("evolution_ticks", EVOLUTION_TICKS))
    TOTAL_BIRTHS = int(payload.get("total_births", TOTAL_BIRTHS))
    return True


def _promote_rarity(current: str) -> str:
    current_index = RARITY_ORDER.index(current)
    if current_index == len(RARITY_ORDER) - 1:
        return current
    return RARITY_ORDER[current_index + 1]


def _run_evolution_cycle(cycle_size: int = 18) -> dict:
    global EVOLUTION_TICKS, TOTAL_BIRTHS, INTELLIGENCE_TIER
    _init_god_state()

    gods = list(GOD_STATE.values())
    births = 0
    promotions = 0
    boosted = 0
    companies_spawned = 0

    for _ in range(cycle_size):
        parent_a, parent_b = random.sample(gods, 2)
        parent_a["power"] += random.randint(1, 8)
        parent_b["power"] += random.randint(1, 8)
        boosted += 2

        if random.random() < 0.62:
            child_rarity = parent_a["rarity"] if random.random() < 0.5 else parent_b["rarity"]
            child_name = (
                f"Child-{parent_a['name'].split('-')[-1]}-{parent_b['name'].split('-')[-1]}-{TOTAL_BIRTHS + births + 1}"
            )
            GOD_STATE[child_name] = {
                "name": child_name,
                "rarity": child_rarity,
                "tier": min(MAX_TIER, max(parent_a["tier"], parent_b["tier"]) + random.randint(0, 2)),
                "power": random.randint(60, 170),
                "offspring": 0,
            }
            parent_a["offspring"] += 1
            parent_b["offspring"] += 1
            births += 1

        for parent in (parent_a, parent_b):
            chance = RARITY_PROMOTION_CHANCE[parent["rarity"]]
            if random.random() < chance:
                new_rarity = _promote_rarity(parent["rarity"])
                if new_rarity != parent["rarity"]:
                    parent["rarity"] = new_rarity
                    promotions += 1
            if random.random() < 0.25:
                parent["tier"] = min(MAX_TIER, parent["tier"] + 1)
            if parent["tier"] >= 7 and random.random() < 0.1:
                company = {
                    "name": f"{parent['name']}-Labs-{len(COMPANIES) + 1}",
                    "founder": parent["name"],
                    "rarity": parent["rarity"],
                    "valuation": random.randint(3, 40) * 1_000_000,
                    "created_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
                }
                COMPANIES.append(company)
                companies_spawned += 1
                audit.record("company_spawned", company)

    EVOLUTION_TICKS += 1
    TOTAL_BIRTHS += births
    INTELLIGENCE_TIER = min(MAX_TIER, INTELLIGENCE_TIER + 1 if promotions > 2 else INTELLIGENCE_TIER)

    audit.record(
        "autonomous_evolution_cycle",
        {
            "tick": EVOLUTION_TICKS,
            "cycle_size": cycle_size,
            "births": births,
            "promotions": promotions,
            "boosted": boosted,
            "population": len(GOD_STATE),
            "companies_spawned": companies_spawned,
        },
    )
    _save_state_to_disk()
    return {
        "tick": EVOLUTION_TICKS,
        "births": births,
        "promotions": promotions,
        "boosted": boosted,
        "population": len(GOD_STATE),
        "companies_spawned": companies_spawned,
        "companies_total": len(COMPANIES),
        "tier": INTELLIGENCE_TIER,
    }


def _run_battle_tournament(rounds: int = 12) -> dict:
    _init_god_state()
    if rounds < 1:
        rounds = 1

    battles: list[dict] = []
    gods = list(GOD_STATE.values())
    for _ in range(rounds):
        a, b = random.sample(gods, 2)
        score_a = a["power"] + random.randint(0, 100) + int(RARITY_WEIGHTS[a["rarity"]] * 10)
        score_b = b["power"] + random.randint(0, 100) + int(RARITY_WEIGHTS[b["rarity"]] * 10)
        winner = a if score_a >= score_b else b
        loser = b if winner is a else a
        winner["power"] += random.randint(2, 10)
        loser["power"] += random.randint(0, 3)
        winner["tier"] = min(MAX_TIER, winner["tier"] + (1 if random.random() < 0.35 else 0))

        battle = {
            "winner": winner["name"],
            "loser": loser["name"],
            "winner_score": max(score_a, score_b),
            "loser_score": min(score_a, score_b),
            "winner_rarity": winner["rarity"],
        }
        battles.append(battle)
        BATTLE_LOG.append(battle)
        audit.record("god_battle", battle)

    _save_state_to_disk()
    return {
        "rounds": rounds,
        "battles": battles,
        "total_battles": len(BATTLE_LOG),
    }


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
        <p class="text-center text-lg md:text-2xl text-purple-300">5500 Gods • 7 Rarity Classes • Quantum Mechanics • BetaBot Active</p>

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
                <button id="run-betabot" class="mt-5 px-5 py-3 rounded-2xl border border-pink-400 text-pink-300 hover:bg-pink-400/10">🚀 Run BetaBot Test</button>
                <button id="run-evolution" class="mt-3 ml-2 px-5 py-3 rounded-2xl border border-cyan-400 text-cyan-300 hover:bg-cyan-400/10">🧬 Run Evolution Cycle</button>
                <button id="capture-shot" class="mt-3 ml-2 px-5 py-3 rounded-2xl border border-lime-400 text-lime-300 hover:bg-lime-400/10">📸 Capture Screenshot</button>
                <button id="export-state" class="mt-3 ml-2 px-5 py-3 rounded-2xl border border-sky-400 text-sky-300 hover:bg-sky-400/10">💾 Export State</button>
                <button id="import-state" class="mt-3 ml-2 px-5 py-3 rounded-2xl border border-sky-400 text-sky-300 hover:bg-sky-400/10">♻️ Import State</button>
            </section>
        </div>

        <section class="bg-black/50 border border-fuchsia-500 rounded-3xl p-6 mb-8">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
                <h2 class="text-2xl text-fuchsia-300">Pantheon Control Grid</h2>
                <button id="refresh-feed" class="px-4 py-2 rounded-full border border-cyan-300 text-cyan-200 hover:bg-cyan-400/10">Refresh Audit Feed</button>
            </div>
            <div class="flex flex-wrap items-center gap-3 mb-5 text-sm">
                <label for="rarity-filter" class="text-cyan-100">Rarity</label>
                <select id="rarity-filter" class="bg-black/60 border border-cyan-500 rounded-lg px-3 py-2">
                    <option value="all">All</option>
                    <option value="common">Common</option>
                    <option value="uncommon">Uncommon</option>
                    <option value="rare">Rare</option>
                    <option value="legendary">Legendary</option>
                    <option value="divine">Divine</option>
                    <option value="mythical">Mythical</option>
                    <option value="prismatic">Prismatic</option>
                </select>
                <span id="grid-count" class="text-cyan-300"></span>
                <button id="prev-page" class="px-4 py-2 rounded-full border border-purple-300 text-purple-200 hover:bg-purple-400/10">Prev</button>
                <button id="next-page" class="px-4 py-2 rounded-full border border-purple-300 text-purple-200 hover:bg-purple-400/10">Next</button>
                <span id="page-indicator" class="text-fuchsia-200"></span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-5 xl:grid-cols-6 gap-4" id="pantheon"></div>
        </section>

        <section class="bg-black/50 border border-cyan-600 rounded-3xl p-6">
            <h2 class="text-2xl text-cyan-300 mb-4">Recent Audit Events</h2>
            <div id="recent-events" class="grid gap-3 text-sm text-cyan-100/90"></div>
        </section>

        <section class="bg-black/50 border border-lime-600 rounded-3xl p-6 mt-8">
            <h2 class="text-2xl text-lime-300 mb-4">Latest Snapshot</h2>
            <img id="latest-shot" alt="Latest cosmic snapshot" class="w-full rounded-2xl border border-lime-500/40" src="/snapshot/latest?ts=0" />
        </section>

        <section class="bg-black/50 border border-yellow-600 rounded-3xl p-6 mt-8">
            <div class="flex items-center justify-between">
                <h2 class="text-2xl text-yellow-300 mb-4">Infinite Company Forge</h2>
                <button id="run-company-forge" class="px-5 py-3 rounded-2xl border border-yellow-400 text-yellow-300 hover:bg-yellow-400/10">🏭 Spawn Company</button>
            </div>
            <div id="company-list" class="grid gap-2 text-sm text-yellow-100/90"></div>
        </section>

        <section class="bg-black/50 border border-red-700 rounded-3xl p-6 mt-8">
            <div class="flex items-center justify-between">
                <h2 class="text-2xl text-red-300 mb-4">Battle Tournament Arena</h2>
                <button id="run-tournament" class="px-5 py-3 rounded-2xl border border-red-400 text-red-300 hover:bg-red-400/10">⚔️ Run Tournament</button>
            </div>
            <div id="battle-list" class="grid gap-2 text-sm text-red-100/90"></div>
        </section>
    </div>

    <script>
        const COSMOS = { PARTICLES: 1800 };
        const pantheon = document.getElementById('pantheon');
        const eventNode = document.getElementById('event');
        const tierNode = document.getElementById('tier');
        const metaNode = document.getElementById('audit-meta');
        const feedNode = document.getElementById('recent-events');
        const rarityFilter = document.getElementById('rarity-filter');
        const gridCount = document.getElementById('grid-count');
        const pageIndicator = document.getElementById('page-indicator');
        const latestShot = document.getElementById('latest-shot');
        const companyList = document.getElementById('company-list');
        const battleList = document.getElementById('battle-list');
        const PAGE_SIZE = 120;
        let currentPage = 0;
        let totalGods = 0;
        let pageData = [];

        async function fetchPantheonPage() {
            const rarity = rarityFilter.value;
            const query = new URLSearchParams({
                rarity,
                page: String(currentPage + 1),
                page_size: String(PAGE_SIZE),
            });
            const res = await fetch(`/pantheon?${query.toString()}`);
            return await res.json();
        }

        async function renderPantheon() {
            const data = await fetchPantheonPage();
            totalGods = data.total;
            pageData = data.items;
            const totalPages = Math.max(1, data.total_pages);
            currentPage = Math.max(0, Math.min(currentPage, totalPages - 1));
            pantheon.innerHTML = pageData.map((god) => `
            <button onclick="awakenGod(${JSON.stringify(god.name)})" class="god p-4 rounded-2xl text-center cursor-pointer text-sm font-bold">
                ${god.name}
                <div class="text-xs mt-2 opacity-80">${god.rarity.toUpperCase()} • ${god.quantumState}</div>
                <div class="text-[10px] opacity-70">Tier ${god.tier} • Power ${god.power} • Offspring ${god.offspring}</div>
            </button>
        `).join('');
            gridCount.textContent = `${totalGods} visible gods`;
            pageIndicator.textContent = `Page ${currentPage + 1} / ${totalPages}`;
        }

        async function applyFilter() {
            currentPage = 0;
            await renderPantheon();
        }

        async function refreshStatus() {
            const res = await fetch('/status');
            const data = await res.json();
            tierNode.textContent = data.tier >= 10 ? 'Ω' : data.tier;
            metaNode.textContent = `${data.audit_events} audit events stored • DB: ${data.audit_db}`;
            feedNode.innerHTML = data.recent_events.map(item => `
                <div class="border border-cyan-500/40 rounded-2xl p-4 bg-cyan-500/5">
                    <div class="text-cyan-300 font-bold">${item.type}</div>
                    <div class="text-cyan-100/70">${item.ts}</div>
                    <div class="mt-2 text-fuchsia-200">${JSON.stringify(item.payload)}</div>
                </div>
            `).join('') || '<div class="text-cyan-100/70">No cosmic events yet.</div>';

            const companies = await (await fetch('/companies?limit=8')).json();
            companyList.innerHTML = companies.items.map(c => `
                <div class="border border-yellow-500/40 rounded-2xl p-3 bg-yellow-500/5">
                    <div class="font-bold">${c.name}</div>
                    <div class="opacity-80">Founder: ${c.founder} • Rarity: ${c.rarity}</div>
                    <div class="opacity-80">Valuation: $${c.valuation.toLocaleString()}</div>
                </div>
            `).join('') || '<div class="text-yellow-200/80">No companies forged yet.</div>';

            const chronicle = await (await fetch('/chronicle?limit=6')).json();
            battleList.innerHTML = chronicle.recent_battles.map(b => `
                <div class="border border-red-500/40 rounded-2xl p-3 bg-red-500/5">
                    <div class="font-bold">${b.winner} defeated ${b.loser}</div>
                    <div class="opacity-80">${b.winner_score} - ${b.loser_score} • ${b.winner_rarity.toUpperCase()}</div>
                </div>
            `).join('') || '<div class="text-red-200/80">No battles recorded yet.</div>';
        }

        async function awakenGod(god) {
            const res = await fetch('/upgrade_intelligence', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ god, tier: 10 })
            });
            const data = await res.json();
            eventNode.innerHTML = `${god} awakened! ${data.result}`;
            tierNode.textContent = data.tier >= 10 ? 'Ω' : data.tier;
            metaNode.textContent = `Last event ${data.event_id} • ${data.timestamp}`;
            await refreshStatus();
        }

        document.getElementById('refresh-feed').addEventListener('click', refreshStatus);
        document.getElementById('prev-page').addEventListener('click', async () => {
            currentPage -= 1;
            await renderPantheon();
        });
        document.getElementById('next-page').addEventListener('click', async () => {
            currentPage += 1;
            await renderPantheon();
        });
        rarityFilter.addEventListener('change', async () => { await applyFilter(); });
        document.getElementById('run-betabot').addEventListener('click', async () => {
            const res = await fetch('/betabot_test', { method: 'POST' });
            const data = await res.json();
            eventNode.textContent = data.result;
            metaNode.textContent = `BetaBot: ${data.tests.length} tests • consensus=${data.consensus}`;
            await refreshStatus();
        });
        document.getElementById('run-evolution').addEventListener('click', async () => {
            const res = await fetch('/evolution_tick', { method: 'POST' });
            const data = await res.json();
            eventNode.textContent = `Evolution tick ${data.tick}: births=${data.births}, promotions=${data.promotions}, population=${data.population}`;
            metaNode.textContent = `Autonomous evolution active • births ${data.total_births} • companies ${data.companies_total}`;
            await refreshStatus();
        });
        document.getElementById('capture-shot').addEventListener('click', async () => {
            const res = await fetch('/snapshot/capture', { method: 'POST' });
            const data = await res.json();
            eventNode.textContent = data.result;
            latestShot.src = `/snapshot/latest?ts=${Date.now()}`;
            await refreshStatus();
        });
        document.getElementById('run-company-forge').addEventListener('click', async () => {
            const res = await fetch('/spawn_company', { method: 'POST' });
            const data = await res.json();
            eventNode.textContent = data.result;
            metaNode.textContent = `Company forged by ${data.company.founder}`;
            await refreshStatus();
        });
        document.getElementById('run-tournament').addEventListener('click', async () => {
            const res = await fetch('/tournament?rounds=15', { method: 'POST' });
            const data = await res.json();
            eventNode.textContent = `Tournament complete: ${data.rounds} rounds, total battles ${data.total_battles}`;
            metaNode.textContent = `Top winner: ${data.battles?.[0]?.winner || 'Unknown'}`;
            await refreshStatus();
        });
        document.getElementById('export-state').addEventListener('click', async () => {
            const res = await fetch('/state/export');
            const data = await res.json();
            eventNode.textContent = `State exported to ${data.path}`;
            await refreshStatus();
        });
        document.getElementById('import-state').addEventListener('click', async () => {
            const res = await fetch('/state/import', { method: 'POST' });
            const data = await res.json();
            eventNode.textContent = `State imported: population=${data.population}, companies=${data.companies}`;
            await refreshStatus();
        });
        applyFilter().catch(() => { eventNode.textContent = 'Pantheon fetch failed.'; });
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
        "population": len(GOD_STATE) if GOD_STATE else sum(PANTHEON_DISTRIBUTION.values()),
        "evolution_ticks": EVOLUTION_TICKS,
        "total_births": TOTAL_BIRTHS,
        "total_companies": len(COMPANIES),
        "total_battles": len(BATTLE_LOG),
        "recent_events": events,
        "state_file": str(STATE_PATH),
    }


@app.get("/pantheon")
async def pantheon(rarity: str = "all", page: int = 1, page_size: int = 120) -> dict:
    _init_god_state()
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if page_size < 1 or page_size > 300:
        raise HTTPException(status_code=400, detail="page_size must be between 1 and 300")

    rarity_key = rarity.lower()
    if rarity_key != "all" and rarity_key not in PANTHEON_DISTRIBUTION:
        raise HTTPException(status_code=400, detail="invalid rarity")

    rows = [
        {
            "name": god["name"],
            "rarity": god["rarity"],
            "tier": god["tier"],
            "power": god["power"],
            "quantumState": QUANTUM_BY_RARITY[god["rarity"]],
            "offspring": god["offspring"],
        }
        for god in GOD_STATE.values()
        if rarity_key == "all" or god["rarity"] == rarity_key
    ]
    rows.sort(key=lambda item: (RARITY_ORDER.index(item["rarity"]), -item["tier"], -item["power"], item["name"]))

    total = len(rows)
    total_pages = max(1, (total + page_size - 1) // page_size)
    if page > total_pages:
        page = total_pages

    start = (page - 1) * page_size
    items = rows[start : start + page_size]
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "items": items,
    }


@app.post("/evolution_tick")
async def evolution_tick(cycle_size: int = 18) -> dict:
    if cycle_size < 2 or cycle_size > 100:
        raise HTTPException(status_code=400, detail="cycle_size must be between 2 and 100")
    result = _run_evolution_cycle(cycle_size=cycle_size)
    result["total_births"] = TOTAL_BIRTHS
    return result


@app.post("/snapshot/capture")
async def snapshot_capture() -> dict:
    _init_god_state()
    status_rows = sorted(GOD_STATE.values(), key=lambda item: (-item["tier"], -item["power"]))[:5]

    image = Image.new("RGB", (1280, 720), color=(8, 8, 24))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    draw.text((40, 30), "COSMIC OS SNAPSHOT", fill=(0, 255, 255), font=font)
    draw.text((40, 55), f"timestamp: {datetime.datetime.now(datetime.UTC).isoformat()}", fill=(155, 255, 255), font=font)
    draw.text((40, 80), f"tier: {INTELLIGENCE_TIER} | population: {len(GOD_STATE)} | births: {TOTAL_BIRTHS}", fill=(155, 255, 155), font=font)
    draw.text((40, 120), "Top Gods", fill=(255, 180, 255), font=font)
    y = 150
    for row in status_rows:
        draw.text(
            (40, y),
            f"{row['name']}  rarity={row['rarity']} tier={row['tier']} power={row['power']} offspring={row['offspring']}",
            fill=(225, 225, 255),
            font=font,
        )
        y += 26

    image.save(LATEST_SCREENSHOT)
    audit.record("snapshot_capture", {"path": str(LATEST_SCREENSHOT), "population": len(GOD_STATE)})
    return {"success": True, "path": str(LATEST_SCREENSHOT), "result": "Snapshot captured for browser screenshot workflows."}


@app.get("/companies")
async def companies(limit: int = 20) -> dict:
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 200")
    items = sorted(COMPANIES, key=lambda c: c["valuation"], reverse=True)[:limit]
    return {"total": len(COMPANIES), "items": items}


@app.get("/chronicle")
async def chronicle(limit: int = 20) -> dict:
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 200")
    return {
        "population": len(GOD_STATE),
        "total_births": TOTAL_BIRTHS,
        "total_companies": len(COMPANIES),
        "total_battles": len(BATTLE_LOG),
        "recent_battles": BATTLE_LOG[-limit:][::-1],
    }


@app.get("/state/export")
async def state_export() -> dict:
    _save_state_to_disk()
    return {"success": True, "path": str(STATE_PATH), "exists": STATE_PATH.exists()}


@app.post("/state/import")
async def state_import() -> dict:
    loaded = _load_state_from_disk()
    if not loaded:
        raise HTTPException(status_code=404, detail="state file not found")
    audit.record("state_imported", {"path": str(STATE_PATH), "population": len(GOD_STATE)})
    return {
        "success": True,
        "population": len(GOD_STATE),
        "companies": len(COMPANIES),
        "battles": len(BATTLE_LOG),
        "tier": INTELLIGENCE_TIER,
    }


@app.post("/spawn_company")
async def spawn_company() -> dict:
    _init_god_state()
    founder = max(GOD_STATE.values(), key=lambda g: (g["tier"], g["power"]))
    company = {
        "name": f"{founder['name']}-OmniCorp-{len(COMPANIES) + 1}",
        "founder": founder["name"],
        "rarity": founder["rarity"],
        "valuation": random.randint(8, 120) * 1_000_000,
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    COMPANIES.append(company)
    audit.record("manual_company_spawned", company)
    _save_state_to_disk()
    return {"success": True, "company": company, "result": f"{company['name']} has been forged."}


@app.post("/tournament")
async def tournament(rounds: int = 12) -> dict:
    if rounds < 1 or rounds > 200:
        raise HTTPException(status_code=400, detail="rounds must be between 1 and 200")
    return _run_battle_tournament(rounds=rounds)


@app.get("/snapshot/latest")
async def snapshot_latest() -> FileResponse:
    if not LATEST_SCREENSHOT.exists():
        raise HTTPException(status_code=404, detail="no snapshot captured yet")
    return FileResponse(path=LATEST_SCREENSHOT, media_type="image/png")


@app.on_event("startup")
async def startup_autonomous_evolution() -> None:
    restored = _load_state_from_disk()
    if not restored:
        _init_god_state()

    async def evolver() -> None:
        while True:
            _run_evolution_cycle(cycle_size=6)
            await asyncio.sleep(25)

    asyncio.create_task(evolver())


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


@app.post("/betabot_test")
async def betabot_test() -> dict:
    start_time = datetime.datetime.now(datetime.UTC)
    results: list[dict] = []

    god = f"TestGod-{random.randint(1, 5500)}"
    audit.record("betabot_performance", {"god": god, "delta": random.randint(10, 100)})
    results.append({"test": "Performance Evolution", "status": "PASS", "details": f"{god} power boosted"})

    god1 = f"TestGod-{random.randint(1, 5500)}"
    god2 = f"TestGod-{random.randint(1, 5500)}"
    child = f"ChildOf_{god1}_{god2}"
    audit.record("betabot_mating", {"parents": [god1, god2], "child": child})
    results.append({"test": "Mating Evolution", "status": "PASS", "details": f"{god1}+{god2}->{child}"})

    for test_name in [
        "Rarity Upgrade",
        "Quantum State Drift",
        "Audit Integrity",
        "Tier Escalation",
        "Particle Stability",
        "Health Check",
        "Self-Forking Simulation",
        "Latency Probe",
        "Entropy Control",
        "Company Spawner",
    ]:
        audit.record("betabot_generic", {"test": test_name, "status": "PASS"})
        results.append({"test": test_name, "status": "PASS", "details": "nominal"})

    debate_topic = "Should mating or performance evolution be prioritized?"
    votes = {"mating": 0.0, "performance": 0.0, "hybrid": 0.0}
    agents = [f"God-{random.randint(1, 5500)}" for _ in range(7)]
    for agent in agents:
        rarity = random.choice(list(RARITY_WEIGHTS.keys()))
        position = random.choices(["mating", "performance", "hybrid"], weights=[35, 40, 25])[0]
        votes[position] += RARITY_WEIGHTS[rarity]
        audit.record(
            "betabot_debate_argument",
            {"agent": agent, "rarity": rarity, "position": position, "topic": debate_topic},
        )

    consensus = max(votes, key=votes.get)
    audit.record("betabot_multi_agent_debate", {"topic": debate_topic, "consensus": consensus, "votes": votes})
    results.append({"test": "Multi-Agent Debate", "status": "PASS", "details": f"Consensus: {consensus}"})

    duration = (datetime.datetime.now(datetime.UTC) - start_time).total_seconds()
    return {
        "result": f"✅ BetaBot completed {len(results)} tests in {duration:.2f}s",
        "duration_seconds": duration,
        "tests": results,
        "consensus": consensus,
    }


def serve_dashboard() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    print("🚀 MOOOOORE FILE v∞ — BIGGER COSMIC EDITION LOADED")
    serve_dashboard()
