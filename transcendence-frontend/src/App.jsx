import React, { useCallback, useMemo, useState } from 'react';
import { FixedSizeList as List } from 'react-window';
import InfiniteLoader from 'react-window-infinite-loader';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8080';

const rarityNames = {
  common: 'StarFragment',
  uncommon: 'AstralVeil',
  rare: 'NovaReaver',
  legendary: 'HeliosSovereign',
  divine: 'AetherionPrime',
  mythical: 'ChronosVeil',
  prismatic: 'PrismaticOverlord',
};

const rarities = Object.keys(rarityNames);
const itemCount = 5000;

function buildGod(index) {
  const rarity = rarities[index % rarities.length];
  return {
    name: `${rarityNames[rarity]}-${index + 1}`,
    rarity,
  };
}

export default function App() {
  const [tier, setTier] = useState(0);
  const [eventLog, setEventLog] = useState('The Pantheon is infinite...');
  const [selectedForMate, setSelectedForMate] = useState(null);
  const [search, setSearch] = useState('');
  const [rarityFilter, setRarityFilter] = useState('all');

  const gods = useMemo(() => Array.from({ length: itemCount }, (_, index) => buildGod(index)), []);
  const filteredGods = useMemo(
    () =>
      gods.filter((god) => {
        const matchesSearch = !search || god.name.toLowerCase().includes(search.toLowerCase());
        const matchesRarity = rarityFilter === 'all' || god.rarity === rarityFilter;
        return matchesSearch && matchesRarity;
      }),
    [gods, rarityFilter, search]
  );

  const loadMoreItems = useCallback(async () => new Promise((resolve) => setTimeout(resolve, 120)), []);
  const isItemLoaded = useCallback((index) => index < filteredGods.length, [filteredGods.length]);

  const postJson = useCallback(async (path, payload) => {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return response.json();
  }, []);

  const awakenGod = useCallback(
    async (god) => {
      const data = await postJson('/upgrade_intelligence', { god, tier: 10 });
      setTier(data.tier ?? 0);
      setEventLog(data.result ?? `${god} awakened`);
    },
    [postJson]
  );

  const evolvePerformance = useCallback(
    async (god) => {
      const data = await postJson('/evolve_performance', { god });
      setEventLog(data.result);
    },
    [postJson]
  );

  const mateGod = useCallback(
    async (god) => {
      if (!selectedForMate) {
        setSelectedForMate(god);
        setEventLog(`Selected ${god} for mating — click another god`);
        return;
      }
      if (selectedForMate === god) {
        setSelectedForMate(null);
        setEventLog(`${god} released from mating selection.`);
        return;
      }
      const data = await postJson('/mate_gods', { god1: selectedForMate, god2: god });
      setEventLog(data.result);
      setSelectedForMate(null);
    },
    [postJson, selectedForMate]
  );

  const Row = ({ index, style }) => {
    const god = filteredGods[index];
    if (!god) {
      return <div style={style} className="row" />;
    }
    return (
      <div style={style} className="row">
        <div className={`god-card ${god.rarity}`}>
          <div>
            <div className="god-name">{god.name}</div>
            <div className="god-rarity">{god.rarity.toUpperCase()}</div>
          </div>
          <div className="actions">
            <button className="action-upgrade" onClick={() => awakenGod(god.name)}>
              ASCEND
            </button>
            <button className="action-performance" onClick={() => evolvePerformance(god.name)}>
              PERFORMANCE
            </button>
            <button className="action-mate" onClick={() => mateGod(god.name)}>
              MATE
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="app-shell">
      <header className="hero">
        <h1 className="neon">THE PANTHEON OF MOOOOORE</h1>
        <p>Infinite Scroll • 7 Rarity Classes • 5000+ Gods</p>
      </header>

      <section className="metrics">
        <div className="metric-card">
          Tier
          <strong>{tier >= 10 ? 'Ω' : tier}</strong>
        </div>
        <div className="metric-card">
          Loaded Gods
          <strong>{filteredGods.length}</strong>
        </div>
        <div className="metric-card">
          Mating Queue
          <strong>{selectedForMate ?? 'Idle'}</strong>
        </div>
      </section>

      <section className="list-shell">
        <div className="list-header">
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search the infinite pantheon" />
          <select value={rarityFilter} onChange={(event) => setRarityFilter(event.target.value)}>
            <option value="all">All rarities</option>
            {rarities.map((rarity) => (
              <option key={rarity} value={rarity}>
                {rarity.toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        <div className="virtual-list">
          <InfiniteLoader isItemLoaded={isItemLoaded} itemCount={filteredGods.length} loadMoreItems={loadMoreItems}>
            {({ onItemsRendered, ref }) => (
              <List
                className="list"
                height={Math.max(window.innerHeight - 310, 420)}
                itemCount={filteredGods.length}
                itemSize={110}
                onItemsRendered={onItemsRendered}
                ref={ref}
                width="100%"
              >
                {Row}
              </List>
            )}
          </InfiniteLoader>
        </div>
      </section>

      <div className="console-wrap">
        <div className="event-console">{eventLog}</div>
      </div>
    </div>
  );
}
