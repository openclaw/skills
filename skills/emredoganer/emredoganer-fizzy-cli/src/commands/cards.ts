import { Command } from 'commander';
import chalk from 'chalk';
import Table from 'cli-table3';
import {
  listCards,
  getCard,
  createCard,
  updateCard,
  deleteCard,
  closeCard,
  reopenCard,
  moveCard,
  assignCard,
  unassignCard,
  tagCard,
  setNotNow
} from '../lib/api.js';
import { isAuthenticated } from '../lib/config.js';

export function createCardsCommands(): Command {
  const cards = new Command('cards')
    .description('Manage Fizzy cards');

  cards
    .command('list')
    .description('List cards in a board')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .option('-c, --column <id>', 'Filter by column ID')
    .option('-s, --status <status>', 'Filter by status (open/closed)')
    .option('--not-now', 'Show only "not now" cards')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        let columnId: number | undefined = undefined;
        if (options.column) {
          columnId = parseInt(options.column, 10);
          if (isNaN(columnId)) {
            console.error(chalk.red('Invalid column ID: must be a number'));
            process.exit(1);
          }
        }
        const cardList = await listCards(options.board, {
          column_id: columnId,
          status: options.status,
          not_now: options.notNow
        });

        if (options.json) {
          console.log(JSON.stringify(cardList, null, 2));
          return;
        }

        if (cardList.length === 0) {
          console.log(chalk.yellow('No cards found.'));
          return;
        }

        const table = new Table({
          head: ['#', 'Title', 'Column', 'Status', 'Priority', 'Assignees'],
          colWidths: [8, 30, 15, 10, 10, 20],
          wordWrap: true
        });

        cardList.forEach(card => {
          const statusIcon = card.status === 'closed' ? chalk.green('✓') : chalk.blue('○');
          const priority = card.priority ? chalk.yellow(card.priority) : '-';
          const assignees = card.assignees?.map(a => a.name).join(', ') || '-';

          table.push([
            card.number,
            card.title.substring(0, 27) + (card.title.length > 27 ? '...' : ''),
            card.column_name || '-',
            statusIcon,
            priority,
            assignees.substring(0, 17) + (assignees.length > 17 ? '...' : '')
          ]);
        });

        console.log(table.toString());
        console.log(chalk.dim(`\nTotal: ${cardList.length} cards`));
      } catch (error) {
        console.error(chalk.red('Failed to list cards:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('get <number>')
    .description('Get card details')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .option('--json', 'Output as JSON')
    .action(async (number: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(number, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        const card = await getCard(options.board, cardNumber);

        if (options.json) {
          console.log(JSON.stringify(card, null, 2));
          return;
        }

        console.log(chalk.bold(`#${card.number} ${card.title}`));
        console.log(chalk.dim(`Board: ${card.board_name}`));
        console.log(chalk.dim(`Column: ${card.column_name}`));
        console.log(chalk.dim(`Status: ${card.status}`));
        console.log(chalk.dim(`Priority: ${card.priority || '-'}`));
        console.log(chalk.dim(`Due: ${card.due_date || '-'}`));
        console.log(chalk.dim(`Assignees: ${card.assignees?.map(a => a.name).join(', ') || '-'}`));
        console.log(chalk.dim(`Tags: ${card.tags?.map(t => t.name).join(', ') || '-'}`));
        console.log(chalk.dim(`Steps: ${card.completed_steps_count}/${card.steps_count}`));
        console.log(chalk.dim(`Comments: ${card.comments_count}`));
        console.log(chalk.dim(`Not Now: ${card.not_now ? 'Yes' : 'No'}`));
        console.log(chalk.dim(`Created: ${new Date(card.created_at).toLocaleString()}`));
        console.log(chalk.dim(`URL: ${card.url}`));

        if (card.description) {
          console.log(chalk.dim('\nDescription:'));
          console.log(card.description);
        }
      } catch (error) {
        console.error(chalk.red('Failed to get card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('create')
    .description('Create a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('-t, --title <title>', 'Card title')
    .option('-d, --description <description>', 'Card description')
    .option('-c, --column <id>', 'Column ID')
    .option('-p, --priority <priority>', 'Priority (low/normal/high/urgent)')
    .option('--due <date>', 'Due date (YYYY-MM-DD)')
    .option('--assignees <ids>', 'Comma-separated assignee IDs')
    .option('--tags <ids>', 'Comma-separated tag IDs')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardOptions: {
          description?: string;
          column_id?: number;
          priority?: 'low' | 'normal' | 'high' | 'urgent';
          due_date?: string;
          assignee_ids?: number[];
          tag_ids?: number[];
        } = {};

        if (options.description) cardOptions.description = options.description;
        if (options.column) {
          const columnId = parseInt(options.column, 10);
          if (isNaN(columnId)) {
            console.error(chalk.red('Invalid column ID: must be a number'));
            process.exit(1);
          }
          cardOptions.column_id = columnId;
        }
        if (options.priority) cardOptions.priority = options.priority;
        if (options.due) cardOptions.due_date = options.due;
        if (options.assignees) {
          cardOptions.assignee_ids = options.assignees.split(',').map((id: string) => {
            const assigneeId = parseInt(id.trim(), 10);
            if (isNaN(assigneeId)) {
              console.error(chalk.red('Invalid assignee ID: must be a number'));
              process.exit(1);
            }
            return assigneeId;
          });
        }
        if (options.tags) {
          cardOptions.tag_ids = options.tags.split(',').map((id: string) => {
            const tagId = parseInt(id.trim(), 10);
            if (isNaN(tagId)) {
              console.error(chalk.red('Invalid tag ID: must be a number'));
              process.exit(1);
            }
            return tagId;
          });
        }

        const card = await createCard(options.board, options.title, cardOptions);

        if (options.json) {
          console.log(JSON.stringify(card, null, 2));
          return;
        }

        console.log(chalk.green('✓ Card created'));
        console.log(chalk.dim(`#${card.number}: ${card.title}`));
        console.log(chalk.dim(`URL: ${card.url}`));
      } catch (error) {
        console.error(chalk.red('Failed to create card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('update <number>')
    .description('Update a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .option('-t, --title <title>', 'New title')
    .option('-d, --description <description>', 'New description')
    .option('-p, --priority <priority>', 'Priority (low/normal/high/urgent)')
    .option('--due <date>', 'Due date (YYYY-MM-DD)')
    .option('--json', 'Output as JSON')
    .action(async (number: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(number, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        const updates: {
          title?: string;
          description?: string;
          priority?: 'low' | 'normal' | 'high' | 'urgent' | null;
          due_date?: string | null;
        } = {};

        if (options.title) updates.title = options.title;
        if (options.description) updates.description = options.description;
        if (options.priority) updates.priority = options.priority;
        if (options.due) updates.due_date = options.due;

        if (Object.keys(updates).length === 0) {
          console.log(chalk.yellow('No updates provided.'));
          return;
        }

        const card = await updateCard(options.board, cardNumber, updates);

        if (options.json) {
          console.log(JSON.stringify(card, null, 2));
          return;
        }

        console.log(chalk.green('✓ Card updated'));
        console.log(chalk.dim(`#${card.number}: ${card.title}`));
      } catch (error) {
        console.error(chalk.red('Failed to update card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('delete <number>')
    .description('Delete a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .action(async (number: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(number, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        await deleteCard(options.board, cardNumber);
        console.log(chalk.green(`✓ Card #${cardNumber} deleted`));
      } catch (error) {
        console.error(chalk.red('Failed to delete card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('close <number>')
    .description('Close a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .action(async (number: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(number, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        await closeCard(options.board, cardNumber);
        console.log(chalk.green(`✓ Card #${cardNumber} closed`));
      } catch (error) {
        console.error(chalk.red('Failed to close card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('reopen <number>')
    .description('Reopen a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .action(async (number: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(number, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        await reopenCard(options.board, cardNumber);
        console.log(chalk.green(`✓ Card #${cardNumber} reopened`));
      } catch (error) {
        console.error(chalk.red('Failed to reopen card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('move <number>')
    .description('Move a card to a different column')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('-c, --column <id>', 'Target column ID')
    .option('-p, --position <position>', 'Position in the column')
    .action(async (number: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(number, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        const columnId = parseInt(options.column, 10);
        if (isNaN(columnId)) {
          console.error(chalk.red('Invalid column ID: must be a number'));
          process.exit(1);
        }
        let position: number | undefined = undefined;
        if (options.position) {
          position = parseInt(options.position, 10);
          if (isNaN(position)) {
            console.error(chalk.red('Invalid position: must be a number'));
            process.exit(1);
          }
        }
        await moveCard(options.board, cardNumber, columnId, position);
        console.log(chalk.green(`✓ Card #${cardNumber} moved to column ${columnId}`));
      } catch (error) {
        console.error(chalk.red('Failed to move card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('assign <number>')
    .description('Assign users to a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('--users <ids>', 'Comma-separated user IDs')
    .action(async (number: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(number, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        const userIds = options.users.split(',').map((id: string) => {
          const userId = parseInt(id.trim(), 10);
          if (isNaN(userId)) {
            console.error(chalk.red('Invalid user ID: must be a number'));
            process.exit(1);
          }
          return userId;
        });
        await assignCard(options.board, cardNumber, userIds);
        console.log(chalk.green(`✓ Users assigned to card #${cardNumber}`));
      } catch (error) {
        console.error(chalk.red('Failed to assign card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('unassign <number>')
    .description('Unassign users from a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('--users <ids>', 'Comma-separated user IDs')
    .action(async (number: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(number, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        const userIds = options.users.split(',').map((id: string) => {
          const userId = parseInt(id.trim(), 10);
          if (isNaN(userId)) {
            console.error(chalk.red('Invalid user ID: must be a number'));
            process.exit(1);
          }
          return userId;
        });
        await unassignCard(options.board, cardNumber, userIds);
        console.log(chalk.green(`✓ Users unassigned from card #${cardNumber}`));
      } catch (error) {
        console.error(chalk.red('Failed to unassign card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('tag <number>')
    .description('Add tags to a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('--tags <ids>', 'Comma-separated tag IDs')
    .action(async (number: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(number, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        const tagIds = options.tags.split(',').map((id: string) => {
          const tagId = parseInt(id.trim(), 10);
          if (isNaN(tagId)) {
            console.error(chalk.red('Invalid tag ID: must be a number'));
            process.exit(1);
          }
          return tagId;
        });
        await tagCard(options.board, cardNumber, tagIds);
        console.log(chalk.green(`✓ Tags added to card #${cardNumber}`));
      } catch (error) {
        console.error(chalk.red('Failed to tag card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  cards
    .command('not-now <number>')
    .description('Mark a card as "not now"')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .option('--unset', 'Remove "not now" status')
    .action(async (number: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(number, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        await setNotNow(options.board, cardNumber, !options.unset);
        console.log(chalk.green(`✓ Card #${cardNumber} ${options.unset ? 'removed from' : 'marked as'} "not now"`));
      } catch (error) {
        console.error(chalk.red('Failed to update card:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  return cards;
}
