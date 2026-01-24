import { Command } from 'commander';
import chalk from 'chalk';
import Table from 'cli-table3';
import { listTags, listColumns, createColumn, updateColumn, deleteColumn } from '../lib/api.js';
import { isAuthenticated } from '../lib/config.js';

export function createTagsCommands(): Command {
  const tags = new Command('tags')
    .description('Manage board tags');

  tags
    .command('list')
    .description('List tags on a board')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const tagList = await listTags(options.board);

        if (options.json) {
          console.log(JSON.stringify(tagList, null, 2));
          return;
        }

        if (tagList.length === 0) {
          console.log(chalk.yellow('No tags found.'));
          return;
        }

        const table = new Table({
          head: ['ID', 'Name', 'Color'],
          colWidths: [10, 30, 15]
        });

        tagList.forEach(tag => {
          table.push([
            tag.id,
            tag.name,
            chalk.hex(tag.color)(tag.color)
          ]);
        });

        console.log(table.toString());
        console.log(chalk.dim(`\nTotal: ${tagList.length} tags`));
      } catch (error) {
        console.error(chalk.red('Failed to list tags:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  return tags;
}

export function createColumnsCommands(): Command {
  const columns = new Command('columns')
    .description('Manage board columns');

  columns
    .command('list')
    .description('List columns on a board')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const columnList = await listColumns(options.board);

        if (options.json) {
          console.log(JSON.stringify(columnList, null, 2));
          return;
        }

        if (columnList.length === 0) {
          console.log(chalk.yellow('No columns found.'));
          return;
        }

        const table = new Table({
          head: ['ID', 'Name', 'Position', 'Cards'],
          colWidths: [10, 30, 12, 10]
        });

        columnList.forEach(column => {
          table.push([
            column.id,
            column.name,
            column.position,
            column.cards_count
          ]);
        });

        console.log(table.toString());
        console.log(chalk.dim(`\nTotal: ${columnList.length} columns`));
      } catch (error) {
        console.error(chalk.red('Failed to list columns:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  columns
    .command('create')
    .description('Create a column')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('-n, --name <name>', 'Column name')
    .option('-p, --position <position>', 'Column position')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        let position: number | undefined = undefined;
        if (options.position) {
          position = parseInt(options.position, 10);
          if (isNaN(position)) {
            console.error(chalk.red('Invalid position: must be a number'));
            process.exit(1);
          }
        }
        const column = await createColumn(options.board, options.name, position);

        if (options.json) {
          console.log(JSON.stringify(column, null, 2));
          return;
        }

        console.log(chalk.green('✓ Column created'));
        console.log(chalk.dim(`ID: ${column.id}`));
        console.log(chalk.dim(`Name: ${column.name}`));
      } catch (error) {
        console.error(chalk.red('Failed to create column:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  columns
    .command('update <id>')
    .description('Update a column')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .option('-n, --name <name>', 'New name')
    .option('-p, --position <position>', 'New position')
    .option('--json', 'Output as JSON')
    .action(async (id: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const columnId = parseInt(id, 10);
        if (isNaN(columnId)) {
          console.error(chalk.red('Invalid column ID: must be a number'));
          process.exit(1);
        }
        const updates: { name?: string; position?: number } = {};
        if (options.name) updates.name = options.name;
        if (options.position) {
          const positionValue = parseInt(options.position, 10);
          if (isNaN(positionValue)) {
            console.error(chalk.red('Invalid position: must be a number'));
            process.exit(1);
          }
          updates.position = positionValue;
        }

        if (Object.keys(updates).length === 0) {
          console.log(chalk.yellow('No updates provided.'));
          return;
        }

        const column = await updateColumn(options.board, columnId, updates);

        if (options.json) {
          console.log(JSON.stringify(column, null, 2));
          return;
        }

        console.log(chalk.green('✓ Column updated'));
        console.log(chalk.dim(`ID: ${column.id}`));
        console.log(chalk.dim(`Name: ${column.name}`));
      } catch (error) {
        console.error(chalk.red('Failed to update column:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  columns
    .command('delete <id>')
    .description('Delete a column')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .action(async (id: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const columnId = parseInt(id, 10);
        if (isNaN(columnId)) {
          console.error(chalk.red('Invalid column ID: must be a number'));
          process.exit(1);
        }
        await deleteColumn(options.board, columnId);
        console.log(chalk.green(`✓ Column ${columnId} deleted`));
      } catch (error) {
        console.error(chalk.red('Failed to delete column:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  return columns;
}
