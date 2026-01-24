import { Command } from 'commander';
import chalk from 'chalk';
import Table from 'cli-table3';
import { listSteps, addStep, completeStep, uncompleteStep, deleteStep } from '../lib/api.js';
import { isAuthenticated } from '../lib/config.js';

export function createStepsCommands(): Command {
  const steps = new Command('steps')
    .description('Manage card steps (subtasks)');

  steps
    .command('list')
    .description('List steps on a card')
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
        const stepList = await listSteps(options.board, cardNumber);

        if (options.json) {
          console.log(JSON.stringify(stepList, null, 2));
          return;
        }

        if (stepList.length === 0) {
          console.log(chalk.yellow('No steps found.'));
          return;
        }

        const table = new Table({
          head: ['ID', 'Status', 'Content', 'Completed By'],
          colWidths: [10, 10, 45, 20],
          wordWrap: true
        });

        stepList.forEach(step => {
          table.push([
            step.id,
            step.completed ? chalk.green('✓') : chalk.dim('○'),
            step.content,
            step.completed_by?.name || '-'
          ]);
        });

        console.log(table.toString());

        const completed = stepList.filter(s => s.completed).length;
        console.log(chalk.dim(`\nProgress: ${completed}/${stepList.length} steps completed`));
      } catch (error) {
        console.error(chalk.red('Failed to list steps:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  steps
    .command('add')
    .description('Add a step to a card')
    .requiredOption('-b, --board <slug>', 'Board slug')
    .requiredOption('-c, --card <number>', 'Card number')
    .requiredOption('--content <content>', 'Step content')
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
        const step = await addStep(options.board, cardNumber, options.content);

        if (options.json) {
          console.log(JSON.stringify(step, null, 2));
          return;
        }

        console.log(chalk.green('✓ Step added'));
        console.log(chalk.dim(`ID: ${step.id}`));
        console.log(chalk.dim(`Content: ${step.content}`));
      } catch (error) {
        console.error(chalk.red('Failed to add step:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  steps
    .command('complete <id>')
    .description('Mark a step as complete')
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
        const stepId = parseInt(id, 10);
        if (isNaN(stepId)) {
          console.error(chalk.red('Invalid step ID: must be a number'));
          process.exit(1);
        }
        await completeStep(options.board, cardNumber, stepId);
        console.log(chalk.green(`✓ Step ${stepId} completed`));
      } catch (error) {
        console.error(chalk.red('Failed to complete step:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  steps
    .command('uncomplete <id>')
    .description('Mark a step as incomplete')
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
        const stepId = parseInt(id, 10);
        if (isNaN(stepId)) {
          console.error(chalk.red('Invalid step ID: must be a number'));
          process.exit(1);
        }
        await uncompleteStep(options.board, cardNumber, stepId);
        console.log(chalk.green(`✓ Step ${stepId} marked as incomplete`));
      } catch (error) {
        console.error(chalk.red('Failed to uncomplete step:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  steps
    .command('delete <id>')
    .description('Delete a step')
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
        const stepId = parseInt(id, 10);
        if (isNaN(stepId)) {
          console.error(chalk.red('Invalid step ID: must be a number'));
          process.exit(1);
        }
        await deleteStep(options.board, cardNumber, stepId);
        console.log(chalk.green(`✓ Step ${stepId} deleted`));
      } catch (error) {
        console.error(chalk.red('Failed to delete step:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  return steps;
}
