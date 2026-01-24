import { Command } from 'commander';
import chalk from 'chalk';
import Table from 'cli-table3';
import { listComments, addComment, updateComment, deleteComment } from '../lib/api.js';
import { isAuthenticated } from '../lib/config.js';

export function createCommentsCommands(): Command {
  const comments = new Command('comments')
    .description('Manage card comments');

  comments
    .command('list')
    .description('List comments on a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('-c, --card <number>', 'Card number')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(options.card, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        const commentList = await listComments(options.board, cardNumber);

        if (options.json) {
          console.log(JSON.stringify(commentList, null, 2));
          return;
        }

        if (commentList.length === 0) {
          console.log(chalk.yellow('No comments found.'));
          return;
        }

        commentList.forEach(comment => {
          const time = new Date(comment.created_at).toLocaleString();
          console.log(chalk.dim(`[${comment.id}] ${time}`));
          console.log(chalk.blue(comment.author?.name || 'Unknown') + ':');
          console.log(comment.content);
          console.log();
        });

        console.log(chalk.dim(`Total: ${commentList.length} comments`));
      } catch (error) {
        console.error(chalk.red('Failed to list comments:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  comments
    .command('add')
    .description('Add a comment to a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('-c, --card <number>', 'Card number')
    .requiredOption('--content <content>', 'Comment content')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(options.card, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        const comment = await addComment(options.board, cardNumber, options.content);

        if (options.json) {
          console.log(JSON.stringify(comment, null, 2));
          return;
        }

        console.log(chalk.green('✓ Comment added'));
        console.log(chalk.dim(`ID: ${comment.id}`));
      } catch (error) {
        console.error(chalk.red('Failed to add comment:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  comments
    .command('update <id>')
    .description('Update a comment')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('-c, --card <number>', 'Card number')
    .requiredOption('--content <content>', 'New content')
    .option('--json', 'Output as JSON')
    .action(async (id: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(options.card, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        const commentId = parseInt(id, 10);
        if (isNaN(commentId)) {
          console.error(chalk.red('Invalid comment ID: must be a number'));
          process.exit(1);
        }
        const comment = await updateComment(options.board, cardNumber, commentId, options.content);

        if (options.json) {
          console.log(JSON.stringify(comment, null, 2));
          return;
        }

        console.log(chalk.green('✓ Comment updated'));
        console.log(chalk.dim(`ID: ${comment.id}`));
      } catch (error) {
        console.error(chalk.red('Failed to update comment:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  comments
    .command('delete <id>')
    .description('Delete a comment')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('-c, --card <number>', 'Card number')
    .action(async (id: string, options) => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const cardNumber = parseInt(options.card, 10);
        if (isNaN(cardNumber)) {
          console.error(chalk.red('Invalid card number: must be a number'));
          process.exit(1);
        }
        const commentId = parseInt(id, 10);
        if (isNaN(commentId)) {
          console.error(chalk.red('Invalid comment ID: must be a number'));
          process.exit(1);
        }
        await deleteComment(options.board, cardNumber, commentId);
        console.log(chalk.green(`✓ Comment ${commentId} deleted`));
      } catch (error) {
        console.error(chalk.red('Failed to delete comment:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  return comments;
}
