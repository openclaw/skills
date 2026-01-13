import { overseerrFetch, parseArgs, printJson } from './lib.mjs';

function usage() {
  process.stderr.write(
    [
      'Usage:',
      '  node search.mjs "query" [--type movie|tv] [--limit N]',
      '',
      'Examples:',
      '  node search.mjs "dune" --type movie',
      '  node search.mjs "bluey" --type tv --limit 5',
      '',
    ].join('\n')
  );
}

const args = parseArgs(process.argv.slice(2));
const query = args._.join(' ').trim();
if (!query) {
  usage();
  process.exit(2);
}

const type = args.type;
const limit = args.limit ? Number.parseInt(String(args.limit), 10) : 10;

const data = await overseerrFetch('/search', {
  query: { query, page: 1 },
});

let results = Array.isArray(data?.results) ? data.results : [];
if (type) results = results.filter((r) => r.mediaType === type);
results = results.slice(0, limit);

printJson({ query, count: results.length, results });
