import { overseerrFetch, parseArgs } from './lib.mjs';

function usage() {
  process.stderr.write(
    [
      'Usage:',
      '  node monitor.mjs [--interval SECONDS] [--filter pending|processing|failed|...] [--requestedBy USER_ID] [--limit N]',
      '',
      'Prints a JSON line whenever a request changes status/updatedAt.',
      '',
    ].join('\n')
  );
}

const args = parseArgs(process.argv.slice(2));
if (args.help) {
  usage();
  process.exit(0);
}

const intervalSec = args.interval ? Number.parseInt(String(args.interval), 10) : 30;
const filter = args.filter;
const requestedBy = args.requestedBy ? Number.parseInt(String(args.requestedBy), 10) : undefined;
const take = args.limit ? Number.parseInt(String(args.limit), 10) : 50;

if (!Number.isFinite(intervalSec) || intervalSec <= 0) throw new Error('Invalid --interval');

const seen = new Map();

async function pollOnce() {
  const data = await overseerrFetch('/request', {
    query: {
      take,
      skip: 0,
      filter,
      sort: 'modified',
      requestedBy,
    },
  });

  const results = Array.isArray(data?.results) ? data.results : [];

  for (const r of results) {
    const key = String(r.id);
    const fingerprint = JSON.stringify({
      status: r.status,
      updatedAt: r.updatedAt,
      modifiedAt: r.modifiedAt,
      media: r.media?.id,
    });

    const prev = seen.get(key);
    if (prev !== fingerprint) {
      seen.set(key, fingerprint);
      process.stdout.write(`${JSON.stringify({ event: 'request', id: r.id, status: r.status, updatedAt: r.updatedAt, data: r })}\n`);
    }
  }
}

// eslint-disable-next-line no-constant-condition
while (true) {
  try {
    await pollOnce();
  } catch (err) {
    process.stdout.write(`${JSON.stringify({ event: 'error', message: err?.message || String(err) })}\n`);
  }
  await new Promise((r) => setTimeout(r, intervalSec * 1000));
}
