import { overseerrFetch, parseArgs, printJson } from './lib.mjs';

function usage() {
  process.stderr.write('Usage: node request-by-id.mjs REQUEST_ID\n');
}

const args = parseArgs(process.argv.slice(2));
const requestId = args._[0];
if (!requestId) {
  usage();
  process.exit(2);
}

const data = await overseerrFetch(`/request/${encodeURIComponent(requestId)}`);
printJson(data);
