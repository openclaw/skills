import { overseerrFetch, parseArgs, parseCsvInts, printJson, toInt } from './lib.mjs';

function usage() {
  process.stderr.write(
    [
      'Usage:',
      '  node request.mjs "title" --type movie|tv [--seasons all|1,2] [--is4k] [--serverId N] [--profileId N] [--rootFolder PATH] [--languageProfileId N] [--userId N]',
      '',
      'Notes:',
      '- For TV, default is --seasons all unless you specify a list.',
      '',
    ].join('\n')
  );
}

const args = parseArgs(process.argv.slice(2));
const title = args._.join(' ').trim();
const type = args.type;

if (!title || !type || !['movie', 'tv'].includes(type)) {
  usage();
  process.exit(2);
}

const search = await overseerrFetch('/search', { query: { query: title, page: 1 } });
const candidates = (search?.results || []).filter((r) => r.mediaType === type);
if (candidates.length === 0) {
  throw new Error(`No ${type} results found for query: ${title}`);
}

const chosen = candidates[0];

let seasons;
if (type === 'tv') {
  if (!args.seasons || args.seasons === 'all') seasons = 'all';
  else seasons = parseCsvInts(args.seasons, { name: 'seasons' });
}

const body = {
  mediaType: type,
  mediaId: chosen.id,
  is4k: Boolean(args.is4k),
};

if (seasons !== undefined) body.seasons = seasons;
if (args.tvdbId !== undefined) body.tvdbId = toInt(args.tvdbId, { name: 'tvdbId' });
if (args.serverId !== undefined) body.serverId = toInt(args.serverId, { name: 'serverId' });
if (args.profileId !== undefined) body.profileId = toInt(args.profileId, { name: 'profileId' });
if (args.rootFolder !== undefined) body.rootFolder = String(args.rootFolder);
if (args.languageProfileId !== undefined)
  body.languageProfileId = toInt(args.languageProfileId, { name: 'languageProfileId' });
if (args.userId !== undefined) body.userId = toInt(args.userId, { name: 'userId' });

const created = await overseerrFetch('/request', { method: 'POST', body });

printJson({ requested: { title, type, chosen: { id: chosen.id, name: chosen.name, title: chosen.title } }, body, created });
