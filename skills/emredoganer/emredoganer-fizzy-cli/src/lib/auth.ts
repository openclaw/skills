import readline from 'readline';
import chalk from 'chalk';
import got from 'got';
import { setToken, clearToken, getToken, setCurrentAccountSlug } from './config.js';
import type { FizzyMe } from '../types/index.js';

const API_BASE = 'https://fizzy.do/api/v1';

function promptPassword(prompt: string): Promise<string> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    // Hide input
    const stdin = process.stdin;
    if (stdin.isTTY) {
      stdin.setRawMode(true);
    }

    process.stdout.write(prompt);

    let password = '';
    const onData = (char: Buffer) => {
      const c = char.toString();

      if (c === '\n' || c === '\r' || c === '\u0004') {
        // Enter or Ctrl+D
        if (stdin.isTTY) {
          stdin.setRawMode(false);
        }
        stdin.removeListener('data', onData);
        process.stdout.write('\n');
        rl.close();
        resolve(password);
      } else if (c === '\u0003') {
        // Ctrl+C
        process.exit(1);
      } else if (c === '\u007F' || c === '\b') {
        // Backspace
        if (password.length > 0) {
          password = password.slice(0, -1);
          process.stdout.clearLine(0);
          process.stdout.cursorTo(0);
          process.stdout.write(prompt + '*'.repeat(password.length));
        }
      } else {
        password += c;
        process.stdout.write('*');
      }
    };

    stdin.on('data', onData);
    stdin.resume();
  });
}

export async function login(): Promise<void> {
  console.log(chalk.blue('Fizzy CLI Login'));
  console.log(chalk.dim('Generate a Personal Access Token at: Profile → API → Generate token'));
  console.log();

  const token = await promptPassword('Enter your Personal Access Token: ');

  if (!token || token.trim() === '') {
    throw new Error('Token cannot be empty');
  }

  // Validate token by fetching user info
  try {
    const response = await got.get(`${API_BASE}/me`, {
      headers: {
        'Authorization': `Bearer ${token.trim()}`,
        'Accept': 'application/json',
        'User-Agent': 'Fizzy CLI (emredoganer@github.com)'
      }
    }).json<FizzyMe>();

    setToken(token.trim());
    console.log(chalk.green(`\n✓ Logged in as ${response.name} (${response.email})`));

    if (response.accounts.length > 0) {
      console.log(chalk.dim('\nAvailable accounts:'));
      response.accounts.forEach(a => {
        console.log(chalk.dim(`  ${a.slug}: ${a.name}`));
      });

      // Auto-select first account
      setCurrentAccountSlug(response.accounts[0].slug);
      console.log(chalk.green(`\n✓ Auto-selected account: ${response.accounts[0].name} (${response.accounts[0].slug})`));
    }
  } catch (error) {
    if (error instanceof got.HTTPError && error.response.statusCode === 401) {
      throw new Error('Invalid token. Please check your Personal Access Token.');
    }
    throw error;
  }
}

export async function getMe(): Promise<FizzyMe> {
  const token = getToken();
  if (!token) {
    throw new Error('Not authenticated. Please run: fizzy auth login');
  }

  const response = await got.get(`${API_BASE}/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json',
      'User-Agent': 'Fizzy CLI (emredoganer@github.com)'
    }
  }).json<FizzyMe>();

  return response;
}

export function logout(): void {
  clearToken();
}
