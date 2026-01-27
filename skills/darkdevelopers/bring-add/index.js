#!/usr/bin/env node

const { program } = require('commander');
const chalk = require('chalk');
const readline = require('readline');
const Bring = require('bring-shopping');

// Exit codes
const EXIT_SUCCESS = 0;
const EXIT_ERROR = 1;
const EXIT_USAGE = 2;
const EXIT_AUTH = 3;
const EXIT_LIST_NOT_FOUND = 4;

// Global state
let useColor = true;
let isDebug = false;

// Helpers
function isTTY() {
    return process.stdin.isTTY && process.stdout.isTTY;
}

function debug(msg) {
    if (isDebug) {
        console.error(chalk.gray(`[debug] ${msg}`));
    }
}

function info(msg) {
    console.error(msg);
}

function error(msg) {
    console.error(chalk.red(`Error: ${msg}`));
}

function warn(msg) {
    console.error(chalk.yellow(`Warning: ${msg}`));
}

// Validate environment
function validateEnv() {
    if (!process.env.BRING_EMAIL) {
        error('BRING_EMAIL not set');
        info('Set with: export BRING_EMAIL="your@email.com"');
        process.exit(EXIT_USAGE);
    }
    if (!process.env.BRING_PASSWORD) {
        error('BRING_PASSWORD not set');
        info('Set with: export BRING_PASSWORD="yourpassword"');
        process.exit(EXIT_USAGE);
    }
}

// Initialize Bring API
async function initBring() {
    debug('Initializing Bring API...');
    const bring = new Bring({
        mail: process.env.BRING_EMAIL,
        password: process.env.BRING_PASSWORD
    });

    try {
        await bring.login();
        debug(`Logged in as ${bring.name}`);
        return bring;
    } catch (err) {
        if (err.message.includes('Cannot Login')) {
            error('Authentication failed - invalid email or password');
            process.exit(EXIT_AUTH);
        }
        throw err;
    }
}

// Find list by name or UUID
async function findList(bring, listIdentifier) {
    const { lists } = await bring.loadLists();
    debug(`Found ${lists.length} lists`);

    if (!listIdentifier) {
        const defaultList = process.env.BRING_DEFAULT_LIST;
        if (defaultList) {
            const found = lists.find(l =>
                l.listUuid === defaultList ||
                l.name.toLowerCase() === defaultList.toLowerCase()
            );
            if (found) {
                debug(`Using default list: ${found.name}`);
                return found;
            }
            error(`Default list "${defaultList}" not found`);
            info('Available lists:');
            lists.forEach(l => info(`  - ${l.name}`));
            process.exit(EXIT_LIST_NOT_FOUND);
        }
        debug(`Using first list: ${lists[0].name}`);
        return lists[0];
    }

    const found = lists.find(l =>
        l.listUuid === listIdentifier ||
        l.name.toLowerCase() === listIdentifier.toLowerCase()
    );

    if (!found) {
        error(`List "${listIdentifier}" not found`);
        info('Available lists:');
        lists.forEach(l => info(`  - ${l.name}`));
        process.exit(EXIT_LIST_NOT_FOUND);
    }

    debug(`Using list: ${found.name}`);
    return found;
}

// Parse item string: "Tomaten 500g" → { item: "Tomaten", spec: "500g" }
function parseItem(input) {
    const trimmed = input.trim();
    if (!trimmed) return null;

    const words = trimmed.split(/\s+/);
    if (words.length === 1) {
        return { item: words[0], spec: '' };
    }

    const lastWord = words[words.length - 1];
    const specPattern = /\d|[gGkKlLmM][lLgG]?$|[sS]tück|[pP]ck/;

    if (specPattern.test(lastWord)) {
        return {
            item: words.slice(0, -1).join(' '),
            spec: lastWord
        };
    }

    return { item: trimmed, spec: '' };
}

// Parse batch input "Tomaten 500g, Zwiebeln, Käse 200g"
function parseBatch(input) {
    return input
        .split(',')
        .map(s => parseItem(s))
        .filter(Boolean);
}

// Read items from stdin
async function readStdin() {
    return new Promise((resolve) => {
        const lines = [];
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
            terminal: false
        });

        rl.on('line', (line) => {
            const parsed = parseItem(line);
            if (parsed) lines.push(parsed);
        });

        rl.on('close', () => {
            resolve(lines);
        });
    });
}

// Add items to list
async function addItems(bring, listUuid, items) {
    const batchItems = items.map(({ item, spec }) => ({
        itemId: item,
        spec: spec,
        operation: 'TO_PURCHASE'
    }));

    await bring.batchUpdateList(listUuid, batchItems);
    return items.length;
}

// Interactive mode
async function interactiveMode(bring, list, opts) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stderr
    });

    info(chalk.bold(`\nAdding to list: ${list.name}\n`));
    info(chalk.gray('Enter items (empty line to finish):'));

    const items = [];

    const askForItem = () => {
        return new Promise((resolve) => {
            rl.question(chalk.cyan('> '), (answer) => {
                resolve(answer);
            });
        });
    };

    while (true) {
        const input = await askForItem();

        if (!input || input.toLowerCase() === 'q') {
            break;
        }

        const parsed = parseItem(input);
        if (parsed) {
            items.push(parsed);
        }
    }

    rl.close();
    return items;
}

// Format output
function formatResult(list, items, opts) {
    if (opts.json) {
        const result = {
            list: {
                name: list.name,
                uuid: list.listUuid
            },
            added: items,
            count: items.length
        };
        console.log(JSON.stringify(result, null, 2));
    } else if (!opts.quiet && items.length > 0) {
        info(chalk.green(`\nAdded ${items.length} item${items.length === 1 ? '' : 's'} to "${list.name}"`));
    }
}

function formatDryRun(list, items, opts) {
    if (opts.json) {
        const result = {
            list: {
                name: list.name,
                uuid: list.listUuid
            },
            wouldAdd: items,
            count: items.length,
            dryRun: true
        };
        console.log(JSON.stringify(result, null, 2));
    } else {
        info(chalk.yellow(`\nWould add to "${list.name}":`));
        items.forEach(({ item, spec }) => {
            const specStr = spec ? ` (${spec})` : '';
            info(`  - ${item}${specStr}`);
        });
    }
}

// Lists command action
async function listsAction() {
    const opts = program.opts();
    debug(`listsAction opts: ${JSON.stringify(opts)}`);
    validateEnv();
    try {
        const bring = await initBring();
        const { lists } = await bring.loadLists();

        if (opts.json) {
            console.log(JSON.stringify({
                lists: lists.map(l => ({
                    name: l.name,
                    uuid: l.listUuid,
                    isDefault: process.env.BRING_DEFAULT_LIST &&
                        (l.listUuid === process.env.BRING_DEFAULT_LIST ||
                         l.name.toLowerCase() === process.env.BRING_DEFAULT_LIST.toLowerCase())
                }))
            }, null, 2));
        } else {
            info(chalk.bold('\nYour Bring! lists:\n'));
            lists.forEach((list, i) => {
                const isDefault = process.env.BRING_DEFAULT_LIST &&
                    (list.listUuid === process.env.BRING_DEFAULT_LIST ||
                     list.name.toLowerCase() === process.env.BRING_DEFAULT_LIST.toLowerCase());

                const marker = isDefault ? chalk.green(' (default)') : '';
                info(`  ${i + 1}. ${chalk.cyan(list.name)}${marker}`);
                if (opts.verbose) {
                    info(chalk.gray(`     UUID: ${list.listUuid}`));
                }
            });
            info('');
        }
    } catch (err) {
        error(err.message);
        process.exit(EXIT_ERROR);
    }
}

// Add command action
async function addAction(item, spec) {
    const opts = program.opts();
    validateEnv();

    try {
        const bring = await initBring();
        const list = await findList(bring, opts.list);
        let items = [];

        if (opts.batch) {
            // Batch mode
            items = parseBatch(opts.batch);
            if (items.length === 0) {
                error('No valid items in batch input');
                process.exit(EXIT_USAGE);
            }
            debug(`Parsed ${items.length} items from batch`);

        } else if (item === '-') {
            // Stdin mode
            debug('Reading items from stdin...');
            items = await readStdin();
            if (items.length === 0) {
                if (opts.noInput) {
                    error('No items provided via stdin');
                    process.exit(EXIT_USAGE);
                }
                warn('No items read from stdin');
                return;
            }
            debug(`Read ${items.length} items from stdin`);

        } else if (item) {
            // Quick mode - single item
            items = [{ item, spec: spec || '' }];
            debug(`Quick mode: adding "${item}" with spec "${spec || ''}"`);

        } else {
            // Interactive or stdin based on TTY
            if (opts.noInput) {
                error('No items provided and --no-input specified');
                info('Provide items via arguments, --batch, or stdin');
                process.exit(EXIT_USAGE);
            }

            if (isTTY()) {
                // Interactive mode
                items = await interactiveMode(bring, list, opts);
            } else {
                // Read from stdin
                debug('No TTY detected, reading from stdin...');
                items = await readStdin();
            }

            if (items.length === 0) {
                if (!opts.quiet) {
                    info('No items added');
                }
                return;
            }
        }

        // Dry-run mode
        if (opts.dryRun) {
            formatDryRun(list, items, opts);
            return;
        }

        // Actually add items
        await addItems(bring, list.listUuid, items);
        formatResult(list, items, opts);

    } catch (err) {
        error(err.message);
        if (isDebug) {
            console.error(err.stack);
        }
        process.exit(EXIT_ERROR);
    }
}

// Setup color handling
function setupColor(opts) {
    if (opts.noColor || process.env.NO_COLOR || process.env.TERM === 'dumb' || !isTTY()) {
        chalk.level = 0;
        useColor = false;
    }
}

// Main
function main() {
    // Check for debug mode
    isDebug = !!process.env.DEBUG;

    program
        .name('bring-add')
        .description('Add items to Bring! shopping lists')
        .version('1.1.0')
        .option('-l, --list <name>', 'target list (name or UUID)')
        .option('-b, --batch <items>', 'comma-separated items: "Milk 1L, Bread, Eggs"')
        .option('-n, --dry-run', 'show what would be added without modifying')
        .option('-q, --quiet', 'suppress all non-error output')
        .option('-v, --verbose', 'show detailed progress')
        .option('--json', 'output JSON to stdout')
        .option('--no-color', 'disable colored output')
        .option('--no-input', 'never prompt, fail if input required')
        .argument('[item]', 'item to add (use "-" for stdin)')
        .argument('[spec]', 'specification (e.g., "500g")')
        .hook('preAction', () => {
            const opts = program.opts();
            setupColor(opts);
            if (opts.verbose) {
                isDebug = true;
            }
        })
        .action(addAction);

    program
        .command('lists')
        .description('show available shopping lists')
        .action(listsAction);

    program.parse();
}

// Signal handling
process.on('SIGINT', () => {
    console.error(chalk.yellow('\n\nInterrupted'));
    process.exit(130);
});

process.on('SIGTERM', () => {
    process.exit(130);
});

main();
