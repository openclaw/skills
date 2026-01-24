import { Command } from 'commander';
import chalk from 'chalk';
import Table from 'cli-table3';
import { listBoards, getBoard, createBoard, updateBoard, deleteBoard, archiveBoard } from '../lib/api.js';
import { isAuthenticated } from '../lib/config.js';

export function createBoardsCommands(): Command {
  const boards = new Command('boards')
    .description('Manage Fizzy boards');

  boards
    .command('list')
    .description('List all boards')
    .option('--archived', 'Show archived boards')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const boardList = await listBoards(options.archived);

        if (options.json) {
          console.log(JSON.stringify(boardList, null, 2));
          return;
        }

        if (boardList.length === 0) {
          console.log(chalk.yellow('No boards found.'));
          return;
        }

        const table = new Table({
          head: ['Slug', 'Name', 'Columns', 'Cards', 'Status'],
          colWidths: [20, 30, 10, 10, 12],
          wordWrap: true
        });

        boardList.forEach(board => {
          table.push([
            board.slug,
            board.name,
            board.columns_count,
            board.cards_count,
            board.archived ? chalk.dim('Archived') : chalk.green('Active')
          ]);
        });

        console.log(table.toString());
        console.log(chalk.dim(`\nTotal: ${boardList.length} boards`));
      } catch (error) {
        console.error(chalk.red('Failed to list boards:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  boards
    .command('get <slug>')
    .description('Get board details')
    .option('--json', 'Output as JSON')
    .action(async (slug: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const board = await getBoard(slug);

        if (options.json) {
          console.log(JSON.stringify(board, null, 2));
          return;
        }

        console.log(chalk.bold(board.name));
        console.log(chalk.dim(`Slug: ${board.slug}`));
        console.log(chalk.dim(`ID: ${board.id}`));
        console.log(chalk.dim(`Description: ${board.description || '-'}`));
        console.log(chalk.dim(`Columns: ${board.columns_count}`));
        console.log(chalk.dim(`Cards: ${board.cards_count}`));
        console.log(chalk.dim(`Status: ${board.archived ? 'Archived' : 'Active'}`));
        console.log(chalk.dim(`Created: ${new Date(board.created_at).toLocaleDateString()}`));
        console.log(chalk.dim(`URL: ${board.url}`));
      } catch (error) {
        console.error(chalk.red('Failed to get board:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  boards
    .command('create')
    .description('Create a new board')
    .requiredOption('-n, --name <name>', 'Board name')
    .option('-d, --description <description>', 'Board description')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const board = await createBoard(options.name, options.description);

        if (options.json) {
          console.log(JSON.stringify(board, null, 2));
          return;
        }

        console.log(chalk.green('✓ Board created'));
        console.log(chalk.dim(`Slug: ${board.slug}`));
        console.log(chalk.dim(`Name: ${board.name}`));
        console.log(chalk.dim(`URL: ${board.url}`));
      } catch (error) {
        console.error(chalk.red('Failed to create board:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  boards
    .command('update <slug>')
    .description('Update a board')
    .option('-n, --name <name>', 'New name')
    .option('-d, --description <description>', 'New description')
    .option('--json', 'Output as JSON')
    .action(async (slug: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const updates: { name?: string; description?: string } = {};
        if (options.name) updates.name = options.name;
        if (options.description) updates.description = options.description;

        if (Object.keys(updates).length === 0) {
          console.log(chalk.yellow('No updates provided. Use --name or --description.'));
          return;
        }

        const board = await updateBoard(slug, updates);

        if (options.json) {
          console.log(JSON.stringify(board, null, 2));
          return;
        }

        console.log(chalk.green('✓ Board updated'));
        console.log(chalk.dim(`Slug: ${board.slug}`));
        console.log(chalk.dim(`Name: ${board.name}`));
      } catch (error) {
        console.error(chalk.red('Failed to update board:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  boards
    .command('delete <slug>')
    .description('Delete a board')
    .action(async (slug: string) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        await deleteBoard(slug);
        console.log(chalk.green(`✓ Board "${slug}" deleted`));
      } catch (error) {
        console.error(chalk.red('Failed to delete board:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  boards
    .command('archive <slug>')
    .description('Archive a board')
    .action(async (slug: string) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        await archiveBoard(slug);
        console.log(chalk.green(`✓ Board "${slug}" archived`));
      } catch (error) {
        console.error(chalk.red('Failed to archive board:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  return boards;
}
