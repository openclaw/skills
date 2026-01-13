import { overseerrFetch, parseArgs, printJson, toInt } from './lib.mjs';

function usage() {
  process.stderr.write(
    [
      'Usage:',
      '  node requests.mjs [--filter all|approved|available|pending|processing|unavailable|failed|deleted|completed] [--limit N] [--skip N] [--sort added|modified] [--requestedBy USER_ID]',
      '',
    ].join('\n')
  );
}

const args = parseArgs(process.argv.slice(2));
if (args.help) {
  usage();
  process.exit(0);
}

const take = args.limit ? toInt(args.limit, { name: 'limit' }) : 20;
const skip = args.skip ? toInt(args.skip, { name: 'skip' }) : 0;

const data = await overseerrFetch('/request', {
  query: {
    take,
    skip,
    filter: args.filter,
    sort: args.sort,
    requestedBy: args.requestedBy ? toInt(args.requestedBy, { name: 'requestedBy' }) : undefined,
  },
});

printJson(data);
