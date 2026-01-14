#!/usr/bin/env node
import Bring from 'bring-shopping';

const args = process.argv.slice(2);
const command = args[0];

function getFlag(name, fallback) {
  const idx = args.indexOf(name);
  if (idx === -1) return fallback;
  const value = args[idx + 1];
  return value ?? fallback;
}

function hasFlag(name) {
  return args.includes(name);
}

function usage() {
  console.log(`Usage:
  bring_cli.mjs lists
  bring_cli.mjs items [--list "Willig"]
  bring_cli.mjs add --item "Milch" [--spec "2L"] [--list "Willig"]
  bring_cli.mjs remove --item "Milch" [--list "Willig"]
  bring_cli.mjs check --item "Milch" [--list "Willig"]
  bring_cli.mjs uncheck --item "Milch" [--spec "2L"] [--list "Willig"]

Env:
  BRING_EMAIL, BRING_PASSWORD
`);
}

async function main() {
  if (!command || hasFlag('--help')) {
    usage();
    process.exit(0);
  }

  const mail = process.env.BRING_EMAIL;
  const password = process.env.BRING_PASSWORD;
  if (!mail || !password) {
    console.error('Missing BRING_EMAIL or BRING_PASSWORD environment variables.');
    process.exit(1);
  }

  const bring = new Bring({ mail, password });
  await bring.login();

  if (command === 'lists') {
    const lists = await bring.loadLists();
    console.log(JSON.stringify(lists.lists, null, 2));
    return;
  }

  const listNameOrId = getFlag('--list', 'Willig');
  const lists = await bring.loadLists();
  const list = lists.lists.find((entry) => entry.listUuid === listNameOrId || entry.name === listNameOrId);
  if (!list) {
    console.error(`List not found: ${listNameOrId}`);
    process.exit(1);
  }

  if (command === 'items') {
    const items = await bring.getItems(list.listUuid);
    console.log(JSON.stringify(items, null, 2));
    return;
  }

  const item = getFlag('--item', null);
  if (!item) {
    console.error('Missing --item argument.');
    process.exit(1);
  }

  if (command === 'add') {
    const spec = getFlag('--spec', '');
    await bring.saveItem(list.listUuid, item, spec);
    console.log(`Added: ${item}`);
    return;
  }

  if (command === 'remove') {
    await bring.removeItem(list.listUuid, item);
    console.log(`Removed: ${item}`);
    return;
  }

  if (command === 'check') {
    await bring.moveToRecentList(list.listUuid, item);
    console.log(`Checked: ${item}`);
    return;
  }

  if (command === 'uncheck') {
    const spec = getFlag('--spec', '');
    await bring.saveItem(list.listUuid, item, spec);
    console.log(`Unchecked: ${item}`);
    return;
  }

  console.error(`Unknown command: ${command}`);
  usage();
  process.exit(1);
}

main().catch((error) => {
  console.error(error?.message ?? String(error));
  process.exit(1);
});
