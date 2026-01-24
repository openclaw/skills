import { Command } from 'commander';
import chalk from 'chalk';
import Table from 'cli-table3';
import { login, logout, getMe } from '../lib/auth.js';
import { isAuthenticated, setCurrentAccountSlug, getCurrentAccountSlug, getToken } from '../lib/config.js';

export function createAuthCommands(): Command {
  const auth = new Command('auth')
    .description('Manage authentication');

  auth
    .command('login')
    .description('Login to Fizzy with a Personal Access Token')
    .action(async () => {
      try {
        if (isAuthenticated()) {
          console.log(chalk.yellow('Already authenticated. Use "fizzy auth logout" to logout first.'));
          return;
        }

        await login();
      } catch (error) {
        console.error(chalk.red('Login failed:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  auth
    .command('logout')
    .description('Logout from Fizzy')
    .action(() => {
      logout();
      console.log(chalk.green('✓ Successfully logged out'));
    });

  auth
    .command('status')
    .description('Show authentication status')
    .action(async () => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const me = await getMe();
        const currentSlug = getCurrentAccountSlug();

        console.log(chalk.green('✓ Authenticated'));
        console.log(chalk.dim(`User: ${me.name}`));
        console.log(chalk.dim(`Email: ${me.email}`));
        console.log(chalk.dim(`Current Account: ${currentSlug || 'Not set'}`));
        console.log(chalk.dim('Token: [configured]'));
      } catch (error) {
        console.error(chalk.red('Failed to get status:'), error instanceof Error ? error.message : error);
      }
    });

  return auth;
}

export function createAccountsCommand(): Command {
  const accounts = new Command('accounts')
    .description('List available Fizzy accounts')
    .action(async () => {
      if (!isAuthenticated()) {
        console.log(chalk.yellow('Not authenticated. Run "fizzy auth login" to login.'));
        return;
      }

      try {
        const me = await getMe();
        const currentSlug = getCurrentAccountSlug();

        if (me.accounts.length === 0) {
          console.log(chalk.yellow('No accounts found.'));
          return;
        }

        const table = new Table({
          head: ['Slug', 'Name', 'Current'],
          colWidths: [20, 40, 10]
        });

        me.accounts.forEach(account => {
          table.push([
            account.slug,
            account.name,
            account.slug === currentSlug ? chalk.green('✓') : ''
          ]);
        });

        console.log(table.toString());
      } catch (error) {
        console.error(chalk.red('Failed to list accounts:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  return accounts;
}

export function createAccountCommand(): Command {
  const account = new Command('account')
    .description('Manage current account');

  account
    .command('set <slug>')
    .description('Set current Fizzy account')
    .action(async (slug: string) => {
      try {
        const me = await getMe();
        const accountExists = me.accounts.find(a => a.slug === slug);

        if (!accountExists) {
          console.error(chalk.red(`Account "${slug}" not found`));
          console.log(chalk.dim('Available accounts:'));
          me.accounts.forEach(a => console.log(chalk.dim(`  ${a.slug}: ${a.name}`)));
          process.exit(1);
        }

        setCurrentAccountSlug(slug);
        console.log(chalk.green(`✓ Switched to account: ${accountExists.name} (${slug})`));
      } catch (error) {
        console.error(chalk.red('Failed to set account:'), error instanceof Error ? error.message : error);
        process.exit(1);
      }
    });

  account
    .command('current')
    .description('Show current account')
    .action(async () => {
      const currentSlug = getCurrentAccountSlug();
      if (!currentSlug) {
        console.log(chalk.yellow('No account selected. Run "fizzy account set <slug>" to select one.'));
        return;
      }

      try {
        const me = await getMe();
        const account = me.accounts.find(a => a.slug === currentSlug);

        if (account) {
          console.log(`Current account: ${account.name} (${account.slug})`);
        } else {
          console.log(`Current account slug: ${currentSlug}`);
        }
      } catch (error) {
        console.log(`Current account slug: ${currentSlug}`);
      }
    });

  return account;
}
