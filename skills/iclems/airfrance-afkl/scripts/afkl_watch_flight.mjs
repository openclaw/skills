#!/usr/bin/env node
// Generic watcher: emits JSON for the cron runner, or sends messages when invoked manually.
import fs from 'node:fs';
import path from 'node:path';
import { afklFetchJson, getStateDir } from './afkl_http.mjs';

const STATE_DIR = getStateDir();
try { fs.mkdirSync(STATE_DIR, { recursive: true }); } catch {}
const AIRCRAFT_CACHE_PATH = path.join(STATE_DIR, 'aircraft_intel_cache.json');
const AIRCRAFT_STATIC_CACHE_PATH = path.join(STATE_DIR, 'aircraft_static_cache.json');

function ymdInTz(date, timeZone) {
  const parts = new Intl.DateTimeFormat('en-CA', { timeZone, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(date);
  const get = (t) => parts.find(p => p.type === t)?.value;
  return `${get('year')}-${get('month')}-${get('day')}`;
}

function prettyWhen(iso, { timeZone, locale = 'fr-FR' } = {}) {
  if (!iso) return '';
  const d = new Date(iso);
  if (!Number.isFinite(d.getTime())) return iso;

  const now = new Date();
  const tz = timeZone || 'Europe/Paris';
  const ymdNow = ymdInTz(now, tz);
  const ymdEvt = ymdInTz(d, tz);

  const toDayNum = (ymd) => {
    const [Y,M,D] = ymd.split('-').map(Number);
    return Math.floor(Date.UTC(Y, M-1, D) / 86400000);
  };
  const diff = toDayNum(ymdEvt) - toDayNum(ymdNow);

  let dayLabel;
  // User preference: always show weekday + date (no today/tomorrow wording).
  const weekday = new Intl.DateTimeFormat(locale, { timeZone: tz, weekday: 'long' }).format(d);
  const dayMonth = new Intl.DateTimeFormat(locale, { timeZone: tz, day: '2-digit', month: 'short' }).format(d);
  const time = new Intl.DateTimeFormat(locale, { timeZone: tz, hour: '2-digit', minute: '2-digit' }).format(d).replace(':','h');
  return `${weekday} ${dayMonth} ${time}`;
}

function normalizeRegs(r) {
  const s = String(r || '').toUpperCase().replace(/\s+/g,'');
  const out = new Set([s]);
  if (/^F[A-Z0-9]{4}$/.test(s)) out.add(`F-${s.slice(1)}`);
  if (/^F-[A-Z0-9]{4}$/.test(s)) out.add(`F${s.slice(2)}`);
  return Array.from(out);
}

function loadJson(path) {
  if (!fs.existsSync(path)) return null;
  try { return JSON.parse(fs.readFileSync(path, 'utf8')); } catch { return null; }
}

async function aircraftIntel(reg) {
  if (!reg) return null;
  const tried = normalizeRegs(reg);
  const primary = tried[0];

  // 1) Static cache (never expires)
  const staticCache = loadJson(AIRCRAFT_STATIC_CACHE_PATH) || {};
  for (const t of tried) {
    if (staticCache[t]) return { reg: t, ...staticCache[t] };
  }

  // 2) Soft cache (expires)
  let cache = loadJson(AIRCRAFT_CACHE_PATH) || {};
  const now = Date.now();
  const cached = cache[primary];
  if (cached && cached.expiresAtMs && now < cached.expiresAtMs) return cached.intel;

  // 3) Best-effort Planespotters
  try {
    for (const t of tried) {
      try {
        const url = `https://api.planespotters.net/pub/photos/reg/${encodeURIComponent(t)}`;
        const resp = await fetch(url, { headers: { 'accept': 'application/json' } });
        const text = await resp.text();
        const j = JSON.parse(text);
        const photo = (j.photos && j.photos[0]) || null;
        const ac = photo && photo.aircraft || null;
        if (ac) {
          const intel = {
            reg: t,
            manufacturer: ac.manufacturer || null,
            model: ac.model || null,
            msn: ac.msn || null,
            firstFlightDate: ac.firstFlightDate || null,
            deliveryDate: ac.deliveryDate || null,
            ageYears: ac.ageYears ?? null,
          };
          cache[primary] = { intel, expiresAtMs: now + 30*24*3600*1000 };
          try { fs.writeFileSync(AIRCRAFT_CACHE_PATH, JSON.stringify(cache, null, 2)); } catch {}
          return intel;
        }
      } catch {}
    }
  } catch {}

  cache[primary] = { intel: { reg: primary, lookup: 'not_found' }, expiresAtMs: now + 24*3600*1000 };
  try { fs.writeFileSync(AIRCRAFT_CACHE_PATH, JSON.stringify(cache, null, 2)); } catch {}
  return cache[primary].intel;
}


function getArg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  if (i === -1) return def;
  const v = process.argv[i + 1];
  return (!v || v.startsWith('--')) ? def : v;
}

const carrier = (getArg('carrier', 'AF') || 'AF').toUpperCase();
const flight = String(parseInt(getArg('flight'), 10));
const origin = (getArg('origin') || '').toUpperCase();
const depDate = getArg('dep-date');
const prevDepth = parseInt(getArg('prev-depth', '2'), 10);
const stateKey = `${carrier}${flight}_${origin}_${depDate}`;
const statePath = path.join(STATE_DIR, `afkl_watch_${stateKey}.json`);

if (!flight || !depDate || !origin) {
  console.log(JSON.stringify({ shouldNotify: true, message: 'AFKL watcher: missing args. Need --carrier --flight --origin --dep-date' }));
  process.exit(0);
}

function parseIso(s) {
  const t = Date.parse(s || '');
  return Number.isFinite(t) ? t : null;
}

function originTimeZone(origin) {
  // Minimal mapping; extend as needed.
  if (origin === 'JFK' || origin === 'EWR') return 'America/New_York';
  if (origin === 'CDG' || origin === 'ORY') return 'Europe/Paris';
  return 'UTC';
}

function pickFlight(data, { origin, carrier, flight, depDate }) {
  const flights = data.operationalFlights || [];
  const tz = originTimeZone(origin);

  // Prefer the operational flight whose *departure local date* matches depDate.
  const matches = flights.filter(f =>
    (f.airline && f.airline.code) === carrier &&
    String(f.flightNumber) === String(flight) &&
    Array.isArray(f.route) && f.route[0] === origin
  );

  for (const f of matches) {
    const leg = (f.flightLegs && f.flightLegs[0]) || {};
    const depIso = leg?.departureInformation?.times?.scheduled;
    if (!depIso) continue;
    const ymd = ymdInTz(new Date(depIso), tz);
    if (ymd === depDate) return f;
  }

  return matches[0] || flights[0];
}

function summarizeFlight(f) {
  const leg = (f.flightLegs && f.flightLegs[0]) || {};
  const depTimes = (leg.departureInformation && leg.departureInformation.times) || {};
  const arrTimes = (leg.arrivalInformation && leg.arrivalInformation.times) || {};
  const boardingTimes = (leg.departureInformation && leg.departureInformation.boardingTimes) || {};
  const legStatuses = leg.otherFlightLegStatuses || {};
  const depPlaces = (((leg.departureInformation||{}).airport||{}).places) || {};
  const arrPlaces = (((leg.arrivalInformation||{}).airport||{}).places) || {};
  const route = Array.isArray(f.route) ? f.route : [];
  const aircraft = leg.aircraft || {};
  const depAirport = (leg.departureInformation && leg.departureInformation.airport) || {};
  const arrAirport = (leg.arrivalInformation && leg.arrivalInformation.airport) || {};
  const depCity = (depAirport.city && (depAirport.city.nameLangTranl || depAirport.city.name)) || '';
  const arrCity = (arrAirport.city && (arrAirport.city.nameLangTranl || arrAirport.city.name)) || '';
  const depAirportName = depAirport.nameLangTranl || depAirport.name || '';
  const arrAirportName = arrAirport.nameLangTranl || arrAirport.name || '';

  // In practice we see: scheduled, latestPublished, estimated.
  const depBest = depTimes.latestPublished || depTimes.estimated || depTimes.latest || depTimes.actual || '';
  const arrBest = arrTimes.latestPublished || arrTimes.estimated || arrTimes.latest || arrTimes.actual || '';

  return {
    id: f.id,
    carrier: (f.airline && f.airline.code) || '',
    flightNumber: String(f.flightNumber || ''),
    scheduleDate: f.flightScheduleDate,
    route,
    depCity,
    arrCity,
    depAirportName,
    arrAirportName,

    statusPublic: f.flightStatusPublic || '',
    statusPublicTxt: f.flightStatusPublicLangTransl || '',
    publishedStatus: leg.publishedStatus || leg.statusName || leg.status || '',

    // Times
    depScheduled: depTimes.scheduled || '',
    depBest,
    boardingPlanned: boardingTimes.plannedBoardingTime || '',
    boardingClosed: boardingTimes.gateCloseTime || '',
    boardingStatus: legStatuses.boardingStatus || '',
    arrScheduled: arrTimes.scheduled || '',
    arrBest,
    arrEstimated: arrTimes.estimated || '',

    // Places
    terminal: depPlaces.terminalCode || depPlaces.boardingTerminal || '',
    gate: (depPlaces.gateNumber && depPlaces.gateNumber.join(',')) || (depPlaces.paxDepartureGate && depPlaces.paxDepartureGate.join(',')) || '',
    checkInZone: (depPlaces.checkInZone && depPlaces.checkInZone.join(',')) || '',

    // Arrival position can hint gate vs remote stand when explicitly provided.
    arrivalPositionTerminal: (Array.isArray(arrPlaces.arrivalPositionTerminal) ? arrPlaces.arrivalPositionTerminal.join(',') : (arrPlaces.arrivalPositionTerminal || '')),
    arrivalPositionPier: (Array.isArray(arrPlaces.arrivalPositionPier) ? arrPlaces.arrivalPositionPier.join(',') : (arrPlaces.arrivalPositionPier || '')),

    // Aircraft
    aircraftReg: aircraft.registration || '',
    aircraftType: aircraft.typeCode || '',
    aircraftTypeName: aircraft.typeName || '',
    subFleet: aircraft.subFleetCodeId || '',
    physicalPaxConfiguration: aircraft.physicalPaxConfiguration || '',
    operationalConfiguration: aircraft.operationalConfiguration || '',
    wifiEnabled: aircraft.wifiEnabled ?? null,
    highSpeedWifi: aircraft.highSpeedWifi ?? null,
    satelliteConnectivityOnBoard: aircraft.satelliteConnectivityOnBoard ?? null,

    // Previous-flight chain
    prevId: (f.flightRelations && f.flightRelations.previousFlightData && f.flightRelations.previousFlightData.id) || '',
    prevDate: (f.flightRelations && f.flightRelations.previousFlightData && f.flightRelations.previousFlightData.flightScheduleDate) || '',
  };
}

function computeNextIntervalMs(nowMs, depMs) {
  if (!depMs) return 60*60*1000;
  const dt = depMs - nowMs;
  if (dt > 36*3600*1000) return 60*60*1000;
  if (dt > 12*3600*1000) return 30*60*1000;
  if (dt > 3*3600*1000) return 15*60*1000;
  if (dt > 0) return 10*60*1000;
  // after departure
  return 30*60*1000;
}

async function fetchById(id) {
  // Throttle is handled by caller (cron frequency + nextRunAt in state).
  return afklFetchJson(`https://api.airfranceklm.com/opendata/flightstatus/${encodeURIComponent(id)}`);
}

const now = Date.now();
let state = null;
if (fs.existsSync(statePath)) {
  try { state = JSON.parse(fs.readFileSync(statePath, 'utf8')); } catch {}
}

if (state?.nextCheckAtMs && now < state.nextCheckAtMs) {
  // No output = no notification.
  process.exit(0);
}

// Cache previous-flight path by tail to avoid extra API calls.
const prevPathCache = state?.prevPathCache || {};

// Query operational flights list
const startRange = `${depDate}T00:00:00Z`;
const endRange = new Date(Date.parse(`${depDate}T00:00:00Z`) + 48*3600*1000).toISOString().replace(/\.\d{3}Z$/, 'Z');
const listUrl = `https://api.airfranceklm.com/opendata/flightstatus/?${new URLSearchParams({
  startRange,
  endRange,
  movementType: 'D',
  origin,
  carrierCode: carrier,
  flightNumber: flight,
  pageSize: '10',
  pageNumber: '0',
  timeOriginType: 'S',
  timeType: 'L',
}).toString()}`;

let data;
try {
  data = await afklFetchJson(listUrl);
} catch (e) {
  const msg = `AF${flight} watcher: erreur API (${e.status||'?'})`;
  console.log(JSON.stringify({ shouldNotify: true, message: msg }));
  process.exit(0);
}

const f = pickFlight(data, { origin, carrier, flight, depDate });
if (!f) {
  console.log(JSON.stringify({ shouldNotify: true, message: `AF${flight} watcher: vol introuvable (API vide).` }));
  process.exit(0);
}

const snap = summarizeFlight(f);
// Enrich aircraft (best-effort, cached)
if (snap.aircraftReg) {
  snap.aircraftIntel = await aircraftIntel(snap.aircraftReg);
}
const depMs = parseIso(snap.depScheduled) || parseIso(snap.depBest);
const nextInterval = computeNextIntervalMs(now, depMs);

// Follow previous-flight chain (depth-limited)
// Note: we already did 1 API call to list flights; respect 1 req/s by sleeping before the first chained call.
const prevAlerts = [];
const prevChain = [];
let prevId = snap.prevId;

const tailKey = (snap.aircraftReg || '').replace(/^F([A-Z0-9]{4})$/, 'F-$1');
const cachedPrevPath = tailKey ? prevPathCache[tailKey] : null;
const effectivePrevDepth = cachedPrevPath ? Math.min(prevDepth, 1) : prevDepth;

if (effectivePrevDepth > 0 && prevId) await new Promise(r => setTimeout(r, 1100));
for (let d=0; d<effectivePrevDepth && prevId; d++) {
  // Respect 1 req/s: sleep 1100ms between calls when chaining
  if (d>0) await new Promise(r => setTimeout(r, 1100));
  let prev;
  try { prev = await fetchById(prevId); } catch { break; }
  const prevSnap = summarizeFlight(prev);
  prevChain.push({ depth: d+1, id: prevId, snap: prevSnap });

  const st = (prevSnap.statusPublic || prevSnap.publishedStatus || '').toUpperCase();
  if (st.includes('CANCEL') || st.includes('DELAY') || st.includes('DIVERT')) {
    prevAlerts.push({ depth: d+1, id: prevId, status: prevSnap.statusPublic || prevSnap.publishedStatus, depBest: prevSnap.depBest, arrBest: prevSnap.arrBest, route: prevSnap.route });
  }
  prevId = prevSnap.prevId;
}

// Compute previous-flight summary + build/cache previous-flight path like: Dubai → Paris → New York
if (prevChain.length) {
  const p = prevChain[0].snap;
  const prevArrBest = p.arrBest || p.arrScheduled;
  const prevArrMs = parseIso(prevArrBest);
  const prevArrSchedMs = parseIso(p.arrScheduled);
  let delayMin = 0;
  if (prevArrMs && prevArrSchedMs) delayMin = Math.round((prevArrMs - prevArrSchedMs) / 60000);
  const city = p.depCity || p.route[0];
  const st = (p.statusPublic || p.publishedStatus || '').toUpperCase();
  const label = st.includes('DELAY') ? 'DELAYED' : (st.includes('CANCEL') ? 'CANCELLED' : (st.includes('ON_TIME') || st.includes('ONTIME') ? 'ON TIME' : st || ''));
  snap.prevSummary = `${city}|${label}|${delayMin}`;
}

if (tailKey) {
  if (cachedPrevPath) {
    snap.prevPath = cachedPrevPath;
  } else if (prevChain.length >= 2) {
    const deep = prevChain[prevChain.length - 1].snap;
    const first = prevChain[0].snap;
    const cities = [deep.depCity || deep.route[0], deep.arrCity || deep.route[1], first.arrCity || first.route[1]].filter(Boolean);
    const uniq = cities.filter((c, i) => i === 0 || c !== cities[i - 1]);
    const pathStr = uniq.join(' → ');
    snap.prevPath = pathStr;
    prevPathCache[tailKey] = pathStr;
  }
}

// Compare to previous state
const prev = state?.snapshot || null;
const changes = [];
if (prev) {
  for (const k of ['statusPublic','publishedStatus','depScheduled','depBest','boardingClosed','boardingStatus','arrScheduled','arrBest','terminal','gate','arrivalPositionTerminal','aircraftReg','aircraftType','aircraftTypeName','physicalPaxConfiguration','operationalConfiguration','wifiEnabled','highSpeedWifi','satelliteConnectivityOnBoard','aircraftIntel','prevSummary','prevPath']) {
    if ((prev[k]||'') !== (snap[k]||'')) changes.push(k);
  }
}

const nextState = { snapshot: snap, nextCheckAtMs: now + nextInterval, updatedAt: new Date().toISOString(), prevPathCache };
fs.writeFileSync(statePath, JSON.stringify(nextState, null, 2));

// simple airport→tz mapping (extend as needed)
const tz = originTimeZone(origin) === 'UTC' ? 'Europe/Paris' : originTimeZone(origin);

if (!prev) {
  const depPretty = prettyWhen(snap.depScheduled || snap.depBest, { timeZone: tz });
  const routeStr = (snap.depCity && snap.arrCity) ? `${snap.depCity}→${snap.arrCity}` : snap.route.join('→');
  const where = `${snap.terminal ? ` • T${snap.terminal}` : ''}${snap.gate ? ` Gate ${snap.gate}` : ''}`;
  console.log(`🛫 ${carrier}${snap.flightNumber} (${routeStr}) — suivi activé\n🕤 Départ: ${depPretty}${where}`);
  process.exit(0);
}

if (changes.length === 0 && prevAlerts.length === 0) {
  // No output = no notification.
  process.exit(0);
}

function parseCabinConfig(cfg) {
  // Example: P004J058W028Y206
  const m = String(cfg||'').match(/P(\d+)J(\d+)W(\d+)Y(\d+)/);
  if (!m) return null;
  const [_, p, j, w, y] = m;
  return { first: Number(p), business: Number(j), premium: Number(w), economy: Number(y) };
}

function wifiLine(snap) {
  const hs = snap.highSpeedWifi;
  const we = snap.wifiEnabled;
  const sat = snap.satelliteConnectivityOnBoard;

  // Output format: emoji + the word "wifi" + text fast/slow.
  if (hs === true || hs === 'Y') return `⚡️📶 wifi fast${(sat === true || sat === 'Y') ? ' • 📡' : ''}`;
  if (we === true || we === 'Y') return `📶 wifi slow${(sat === true || sat === 'Y') ? ' • 📡' : ''}`;
  if (we === false || we === 'N') return `📶 wifi off`;
  return '';
}

const lines = [];

// Headline: highlight what changed
if (prev) {
  const old = prev;

  const headlineParts = [];

  // Time changes
  if (changes.includes('depBest') || changes.includes('depScheduled')) {
    headlineParts.push('🟡 nouveau départ');
  }
  if (changes.includes('arrBest') || changes.includes('arrScheduled')) {
    headlineParts.push('🟡 nouvelle arrivée');
  }

  // Gate/terminal
  if (changes.includes('terminal') || changes.includes('gate')) {
    headlineParts.push('🟦 gate/terminal update');
  }

  // Boarding started
  if (changes.includes('boardingStatus') && String(old.boardingStatus||'').toLowerCase().includes('not') && !String(snap.boardingStatus||'').toLowerCase().includes('not')) {
    headlineParts.push('🟢 boarding started');
  }

  // Aircraft/config
  if (changes.includes('aircraftReg') || changes.includes('aircraftType') || changes.includes('physicalPaxConfiguration') || changes.includes('operationalConfiguration')) {
    headlineParts.push('🚨 nouvel avion/config');
  }

  // Inbound impact
  if (changes.includes('prevSummary')) {
    const parts = String(snap.prevSummary||'').split('|');
    const label = (parts[1]||'').toUpperCase();
    const delayMin = Number(parts[2]||0);
    if (label === 'DELAYED' && delayMin >= 10) headlineParts.push(`⚠️ inbound +${delayMin}m`);
    if (label === 'CANCELLED') headlineParts.push('⚠️ inbound cancelled');
  }

  if (headlineParts.length) {
    lines.push(headlineParts.join(' • '));
  }

  // Extra detail for aircraft/config change
  if (changes.includes('aircraftReg') || changes.includes('aircraftType') || changes.includes('physicalPaxConfiguration') || changes.includes('operationalConfiguration')) {
    const oldCfg = old.operationalConfiguration || old.physicalPaxConfiguration || '';
    const newCfg = snap.operationalConfiguration || snap.physicalPaxConfiguration || '';
    if ((old.aircraftReg||'') && (snap.aircraftReg||'') && old.aircraftReg !== snap.aircraftReg) {
      lines.push(`Ancien tail: ${String(old.aircraftReg).replace(/^F([A-Z0-9]{4})$/, 'F-$1')} → Nouveau: ${String(snap.aircraftReg).replace(/^F([A-Z0-9]{4})$/, 'F-$1')}`);
    }
    if (oldCfg && newCfg && oldCfg !== newCfg) {
      lines.push(`Config: ${oldCfg} → ${newCfg}`);
    }
  }
}

const routeStr = (snap.depCity && snap.arrCity) ? `${snap.depCity}→${snap.arrCity}` : snap.route.join('→');
const statusRaw = snap.statusPublic || snap.publishedStatus || '—';
const statusPretty = String(statusRaw)
  .split('_')
  .map(w => w ? (w[0].toUpperCase() + w.slice(1).toLowerCase()) : '')
  .join(' ');
lines.push(`🛫 ${carrier}${snap.flightNumber} (${routeStr}) — ${statusPretty}`);
if (snap.depScheduled) {
  const depPretty = prettyWhen(snap.depScheduled, { timeZone: tz });
  const depBestPretty = snap.depBest ? prettyWhen(snap.depBest, { timeZone: tz }) : '';
  const depStr = (depBestPretty && depBestPretty !== depPretty) ? `${depPretty} → ${depBestPretty}` : depPretty;
  const closed = snap.boardingClosed ? prettyWhen(snap.boardingClosed, { timeZone: tz }) : '';
  const closedTime = closed ? closed.split(' ').slice(-1)[0] : '';
  const where = `${origin}${snap.terminal ? ` T${snap.terminal}` : ''}${snap.gate ? ` Gate ${snap.gate}` : ''}`;
  const bs = (snap.boardingStatus || '').trim();
  const bsShow = bs && !/^not\s*open$/i.test(bs) ? ` • boarding: ${bs}` : '';
  lines.push(`🕤 Départ: ${depStr}${closedTime ? ` (boarding close ${closedTime})` : ''}${bsShow} — ${where}`);
}
if (snap.arrScheduled) {
  const dstTz = (snap.route[1] === 'CDG') ? 'Europe/Paris' : tz;
  const arrPretty = prettyWhen(snap.arrScheduled, { timeZone: dstTz });
  const arrBestPretty = snap.arrBest ? prettyWhen(snap.arrBest, { timeZone: dstTz }) : '';
  const arrStr = (arrBestPretty && arrBestPretty !== arrPretty) ? `${arrPretty} → ${arrBestPretty}` : arrPretty;
  const dst = snap.route[1] || '';
  const dstTerm = snap.arrivalPositionTerminal ? ` ${snap.arrivalPositionTerminal}` : '';
  lines.push(`🛬 Arrivée: ${arrStr} — ${dst}${dstTerm}`);
}
// (terminal/gate already included in departure line)

// Aircraft line (compact + cabin config pretty)
if (snap.aircraftType || snap.aircraftReg) {
  const cfg = parseCabinConfig(snap.operationalConfiguration || snap.physicalPaxConfiguration);
  const cfgPretty = cfg ? ` • ${cfg.first} First / ${cfg.business} Business / ${cfg.premium} Premium / ${cfg.economy} Eco` : '';
  const wifi = wifiLine(snap);
  const age = (snap.aircraftIntel && (snap.aircraftIntel.ageYears != null)) ? `(~${snap.aircraftIntel.ageYears} ans)` : '';
  const tail = snap.aircraftReg ? snap.aircraftReg.replace(/^F([A-Z0-9]{4})$/, 'F-$1') : '';
  lines.push(`✈️ ${tail} ${age} • ${snap.aircraftType} ${snap.aircraftTypeName}${cfgPretty}`.trim());
  if (wifi) lines.push(wifi);

}

// Previous flight (short)
if (prevChain.length && snap.prevSummary) {
  const [city, label, delayMinRaw] = String(snap.prevSummary).split('|');
  const delayMin = Number(delayMinRaw || 0);
  const delayStr = (Math.abs(delayMin) >= 5) ? ` (${delayMin > 0 ? '+' : ''}${delayMin}m)` : '';
  const statusSuffix = label === 'ON TIME' ? '(on time)' : (label === 'DELAYED' ? `(delayed ${delayMin} mins)` : (label === 'CANCELLED' ? '(cancelled)' : `(${String(label||'').toLowerCase()})`));

  if (snap.prevPath) {
    lines.push(`↩️ ${snap.prevPath} ${statusSuffix}`);
  } else {
    lines.push(`↩️ ${city} • ${label}${delayStr}`);
  }
}
console.log(lines.join('\n'));
