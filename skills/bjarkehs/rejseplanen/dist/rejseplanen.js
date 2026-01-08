#!/usr/bin/env node

// src/rejseplanen.ts
var BASE_URL = "https://www.rejseplanen.dk/bin/rest.exe";
var TRAIN_TYPES = ["REG", "IC", "ICL", "LYN", "TOG", "S", "RE"];
var BUS_TYPES = ["BUS", "EXB", "NB", "TB"];
function toStation(s) {
  return { id: s.id, name: cleanStationName(s.name) };
}
function toDeparture(d) {
  return {
    line: d.name,
    type: d.type,
    scheduledTime: d.time,
    realtimeTime: d.rtTime !== d.time ? d.rtTime : undefined,
    delayed: !!(d.rtTime && d.rtTime !== d.time),
    destination: d.direction,
    track: d.rtTrack || d.track
  };
}
function toArrival(a) {
  return {
    line: a.name,
    type: a.type,
    scheduledTime: a.time,
    realtimeTime: a.rtTime !== a.time ? a.rtTime : undefined,
    delayed: !!(a.rtTime && a.rtTime !== a.time),
    origin: a.origin,
    track: a.rtTrack || a.track
  };
}
function toTrip(t) {
  const legs = Array.isArray(t.Leg) ? t.Leg : [t.Leg];
  const first = legs[0];
  const last = legs[legs.length - 1];
  const depTime = first.Origin.rtTime || first.Origin.time;
  const arrTime = last.Destination.rtTime || last.Destination.time;
  const [depH, depM] = depTime.split(":").map(Number);
  const [arrH, arrM] = arrTime.split(":").map(Number);
  let duration = arrH * 60 + arrM - (depH * 60 + depM);
  if (duration < 0)
    duration += 24 * 60;
  return {
    departureTime: depTime,
    arrivalTime: arrTime,
    duration,
    line: first.name,
    delayed: !!(first.Origin.rtTime && first.Origin.rtTime !== first.Origin.time),
    track: first.Origin.rtTrack,
    changes: legs.length - 1
  };
}
function toJourneyStop(s) {
  const hasSchedule = !!(s.arrTime || s.depTime);
  return {
    name: s.name,
    arrivalTime: s.arrTime,
    departureTime: s.depTime,
    realtimeArrival: s.rtArrTime !== s.arrTime ? s.rtArrTime : undefined,
    realtimeDeparture: s.rtDepTime !== s.depTime ? s.rtDepTime : undefined,
    delayed: !!(s.rtArrTime && s.arrTime && s.rtArrTime !== s.arrTime) || !!(s.rtDepTime && s.depTime && s.rtDepTime !== s.depTime),
    track: s.rtTrack || s.track,
    passThrough: !hasSchedule
  };
}
async function searchStations(query) {
  const url = `${BASE_URL}/location.name?input=${encodeURIComponent(query)}&format=json`;
  const res = await fetch(url);
  const data = await res.json();
  return (data.LocationList.StopLocation || []).map(toStation);
}
async function getStationId(query) {
  if (/^\d+$/.test(query))
    return { id: query, name: query };
  const stations = await searchStations(query);
  return stations.length > 0 ? stations[0] : null;
}
async function getDepartures(stationId, options = {}) {
  const { limit = 10, filter = "all", to } = options;
  const url = `${BASE_URL}/departureBoard?id=${stationId}&format=json`;
  const res = await fetch(url);
  const data = await res.json();
  let deps = data.DepartureBoard.Departure || [];
  if (filter === "trains")
    deps = deps.filter((d) => TRAIN_TYPES.includes(d.type));
  else if (filter === "buses")
    deps = deps.filter((d) => BUS_TYPES.includes(d.type));
  if (to) {
    const toLower = to.toLowerCase();
    deps = deps.filter((d) => d.direction.toLowerCase().includes(toLower) || d.finalStop.toLowerCase().includes(toLower));
  }
  return deps.slice(0, limit).map(toDeparture);
}
async function getArrivals(stationId, options = {}) {
  const { limit = 10, filter = "all", from } = options;
  const url = `${BASE_URL}/arrivalBoard?id=${stationId}&format=json`;
  const res = await fetch(url);
  const data = await res.json();
  let arrs = data.ArrivalBoard.Arrival || [];
  if (filter === "trains")
    arrs = arrs.filter((a) => TRAIN_TYPES.includes(a.type));
  else if (filter === "buses")
    arrs = arrs.filter((a) => BUS_TYPES.includes(a.type));
  if (from) {
    const fromLower = from.toLowerCase();
    arrs = arrs.filter((a) => a.origin.toLowerCase().includes(fromLower));
  }
  return arrs.slice(0, limit).map(toArrival);
}
async function getTrips(originId, destId, options = {}) {
  const { time, trainsOnly = true } = options;
  let url = `${BASE_URL}/trip?originId=${originId}&destId=${destId}&format=json`;
  if (trainsOnly)
    url += "&useBus=0";
  if (time)
    url += `&time=${time}`;
  const res = await fetch(url);
  const data = await res.json();
  return (data.TripList.Trip || []).map(toTrip);
}
async function getJourneyStops(stationId, lineQuery) {
  const url = `${BASE_URL}/departureBoard?id=${stationId}&format=json`;
  const res = await fetch(url);
  const data = await res.json();
  const deps = data.DepartureBoard.Departure || [];
  const matching = deps.find((d) => d.line === lineQuery || d.name.toLowerCase().includes(lineQuery.toLowerCase()));
  if (!matching?.JourneyDetailRef)
    return null;
  const detailUrl = matching.JourneyDetailRef.ref.replace("http://", "https://");
  const detailRes = await fetch(detailUrl);
  const detail = await detailRes.json();
  return {
    line: matching.name,
    destination: matching.direction,
    stops: detail.JourneyDetail.Stop.map(toJourneyStop)
  };
}
function formatDeparture(d) {
  const time = d.realtimeTime || d.scheduledTime;
  const delayed = d.delayed ? ` (was ${d.scheduledTime})` : "";
  const track = d.track ? ` [Spor ${d.track}]` : "";
  const isTrain = TRAIN_TYPES.includes(d.type);
  const typeLabel = isTrain ? "" : ` (${d.type})`;
  return `${time}${delayed} ${d.line} → ${d.destination}${track}${typeLabel}`;
}
function formatArrival(a) {
  const time = a.realtimeTime || a.scheduledTime;
  const delayed = a.delayed ? ` (was ${a.scheduledTime})` : "";
  const track = a.track ? ` [Spor ${a.track}]` : "";
  const isTrain = TRAIN_TYPES.includes(a.type);
  const typeLabel = isTrain ? "" : ` (${a.type})`;
  return `${time}${delayed} ${a.line} ← ${a.origin}${track}${typeLabel}`;
}
function formatTrip(t) {
  const delayed = t.delayed ? ` (delayed)` : "";
  const track = t.track ? ` [Spor ${t.track}]` : "";
  const changes = t.changes > 0 ? ` (${t.changes} skift)` : "";
  return `${t.departureTime} → ${t.arrivalTime}  ${t.line}  (${t.duration} min)${track}${delayed}${changes}`;
}
function formatJourneyStop(s, isFirst, isLast) {
  const track = s.track ? ` [Spor ${s.track}]` : "";
  if (s.passThrough)
    return `             ${s.name} (gennemkørsel)${track}`;
  const arr = s.realtimeArrival || s.arrivalTime;
  const dep = s.realtimeDeparture || s.departureTime;
  const arrDelayed = s.realtimeArrival ? ` (was ${s.arrivalTime})` : "";
  const depDelayed = s.realtimeDeparture ? ` (was ${s.departureTime})` : "";
  let timeStr;
  if (isFirst && dep)
    timeStr = `     ${dep}${depDelayed}`;
  else if (isLast && arr)
    timeStr = `${arr}${arrDelayed}     `;
  else if (!arr && dep)
    timeStr = `     ${dep}${depDelayed}`;
  else if (arr && !dep)
    timeStr = `${arr}${arrDelayed}     `;
  else if (arr === dep)
    timeStr = `     ${arr}${arrDelayed}     `;
  else
    timeStr = `${arr}${arrDelayed} → ${dep}${depDelayed}`;
  return `${timeStr}  ${s.name}${track}`;
}
function cleanStationName(name) {
  return name.replace(/ St\.$/, "");
}
function output(data, mode, textFn) {
  if (mode === "json")
    console.log(JSON.stringify(data, null, 2));
  else
    textFn();
}
function parseArgs(args) {
  const flags = {};
  const rest = [];
  let i = 0;
  while (i < args.length) {
    const arg = args[i];
    if (arg === "--trains") {
      flags.trains = true;
      i++;
    } else if (arg === "--buses") {
      flags.buses = true;
      i++;
    } else if (arg === "--to" && i + 1 < args.length) {
      flags.to = args[i + 1];
      i += 2;
    } else if (arg.startsWith("--to=")) {
      flags.to = arg.slice(5);
      i++;
    } else if (arg === "--from" && i + 1 < args.length) {
      flags.from = args[i + 1];
      i += 2;
    } else if (arg.startsWith("--from=")) {
      flags.from = arg.slice(7);
      i++;
    } else if (arg === "--time" && i + 1 < args.length) {
      flags.time = args[i + 1];
      i += 2;
    } else if (arg.startsWith("--time=")) {
      flags.time = arg.slice(7);
      i++;
    } else if (arg === "--output" && i + 1 < args.length) {
      flags.output = args[i + 1];
      i += 2;
    } else if (arg.startsWith("--output=")) {
      flags.output = arg.slice(9);
      i++;
    } else if (arg === "--json") {
      flags.output = "json";
      i++;
    } else {
      rest.push(arg);
      i++;
    }
  }
  return { flags, rest };
}
async function main() {
  const { flags, rest: args } = parseArgs(process.argv.slice(2));
  let filter = "all";
  if (flags.trains)
    filter = "trains";
  else if (flags.buses)
    filter = "buses";
  const to = flags.to;
  const from = flags.from;
  const time = flags.time;
  const outputMode = flags.output === "json" ? "json" : "text";
  const [command, ...rest] = args;
  switch (command) {
    case "search": {
      const query = rest.join(" ");
      if (!query) {
        console.log("Usage: rejseplanen search <station name>");
        process.exit(1);
      }
      const stations = await searchStations(query);
      output(stations, outputMode, () => {
        if (stations.length === 0)
          console.log("No stations found");
        else {
          console.log("Stations found:");
          for (const s of stations.slice(0, 10))
            console.log(`  ${s.id}: ${s.name}`);
        }
      });
      break;
    }
    case "departures": {
      const query = rest.join(" ");
      if (!query) {
        console.log("Usage: rejseplanen departures <station> [--trains|--buses] [--to <dest>]");
        process.exit(1);
      }
      const station = await getStationId(query);
      if (!station) {
        console.log(`No station found for "${query}"`);
        process.exit(1);
      }
      const departures = await getDepartures(station.id, { filter, to });
      output(departures, outputMode, () => {
        if (departures.length === 0)
          console.log(`No departures found for ${station.name}${to ? ` to ${to}` : ""}`);
        else {
          const modeLabel = filter === "all" ? "" : ` (${filter} only)`;
          const destLabel = to ? ` → ${to}` : "";
          console.log(`Departures from ${station.name}${destLabel}${modeLabel}:
`);
          for (const d of departures)
            console.log(`  ${formatDeparture(d)}`);
        }
      });
      break;
    }
    case "arrivals": {
      const query = rest.join(" ");
      if (!query) {
        console.log("Usage: rejseplanen arrivals <station> [--trains|--buses] [--from <origin>]");
        process.exit(1);
      }
      const station = await getStationId(query);
      if (!station) {
        console.log(`No station found for "${query}"`);
        process.exit(1);
      }
      const arrivals = await getArrivals(station.id, { filter, from });
      output(arrivals, outputMode, () => {
        if (arrivals.length === 0)
          console.log(`No arrivals found for ${station.name}${from ? ` from ${from}` : ""}`);
        else {
          const modeLabel = filter === "all" ? "" : ` (${filter} only)`;
          const originLabel = from ? ` ← ${from}` : "";
          console.log(`Arrivals at ${station.name}${originLabel}${modeLabel}:
`);
          for (const a of arrivals)
            console.log(`  ${formatArrival(a)}`);
        }
      });
      break;
    }
    case "trip": {
      if (rest.length < 2) {
        console.log("Usage: rejseplanen trip <from> <to> [--time HH:MM]");
        process.exit(1);
      }
      const fromStation = await getStationId(rest[0]);
      const toStation2 = await getStationId(rest.slice(1).join(" "));
      if (!fromStation) {
        console.log(`No station found for "${rest[0]}"`);
        process.exit(1);
      }
      if (!toStation2) {
        console.log(`No station found for "${rest.slice(1).join(" ")}"`);
        process.exit(1);
      }
      const trips = await getTrips(fromStation.id, toStation2.id, { time, trainsOnly: filter !== "buses" });
      const result = trips.slice(0, 5);
      output(result, outputMode, () => {
        if (result.length === 0)
          console.log(`No trips found from ${fromStation.name} to ${toStation2.name}`);
        else {
          const timeLabel = time ? ` (from ${time})` : "";
          console.log(`${fromStation.name} → ${toStation2.name}${timeLabel}:
`);
          for (const t of result)
            console.log(`  ${formatTrip(t)}`);
        }
      });
      break;
    }
    case "journey": {
      if (rest.length < 2) {
        console.log("Usage: rejseplanen journey <station> <line>");
        process.exit(1);
      }
      const station = await getStationId(rest[0]);
      if (!station) {
        console.log(`No station found for "${rest[0]}"`);
        process.exit(1);
      }
      const journey = await getJourneyStops(station.id, rest.slice(1).join(" "));
      if (!journey) {
        console.log(`No train matching "${rest.slice(1).join(" ")}" found`);
        process.exit(1);
      }
      output(journey, outputMode, () => {
        console.log(`${journey.line} → ${journey.destination}:
`);
        for (let i = 0;i < journey.stops.length; i++) {
          console.log(`  ${formatJourneyStop(journey.stops[i], i === 0, i === journey.stops.length - 1)}`);
        }
      });
      break;
    }
    default:
      console.log(`Rejseplanen CLI - Danish Public Transport

Usage:
  rejseplanen search <query>                     Search for stations
  rejseplanen departures <station>               Get departures
  rejseplanen arrivals <station>                 Get arrivals
  rejseplanen trip <from> <to>                   Journey planner
  rejseplanen journey <station> <line>           Show train stops

Options:
  --trains              Show only trains
  --buses               Show only buses
  --to <station>        Filter departures by destination
  --from <station>      Filter arrivals by origin
  --time HH:MM          Departures after specified time
  --output json|text    Output format (default: text)
  --json                Shorthand for --output json

Examples:
  rejseplanen departures Odense --trains --to Aalborg
  rejseplanen trip Odense Aalborg --time 07:00 --json
`);
  }
}
main().catch(console.error);
