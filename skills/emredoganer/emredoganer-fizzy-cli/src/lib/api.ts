import got, { Got, HTTPError } from 'got';
import chalk from 'chalk';
import { getToken, getCurrentAccountSlug } from './config.js';
import type {
  FizzyBoard,
  FizzyColumn,
  FizzyCard,
  FizzyStep,
  FizzyComment,
  FizzyTag,
  PaginatedResponse
} from '../types/index.js';

const USER_AGENT = 'Fizzy CLI (emredoganer@github.com)';

async function createClient(): Promise<Got> {
  const token = getToken();
  const accountSlug = getCurrentAccountSlug();

  if (!token) {
    throw new Error('Not authenticated. Please run: fizzy auth login');
  }

  if (!accountSlug) {
    throw new Error('No account selected. Please run: fizzy account set <slug>');
  }

  return got.extend({
    prefixUrl: `https://fizzy.do/api/v1/${accountSlug}/`,
    headers: {
      'Authorization': `Bearer ${token}`,
      'User-Agent': USER_AGENT,
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    responseType: 'json',
    hooks: {
      beforeError: [
        (error) => {
          if (error instanceof HTTPError) {
            const { response } = error;
            if (response.statusCode === 429) {
              console.error(chalk.yellow('Rate limited. Please wait and try again.'));
            } else if (response.statusCode === 401) {
              console.error(chalk.red('Authentication failed. Please run: fizzy auth login'));
            } else if (response.statusCode === 404) {
              console.error(chalk.red('Resource not found.'));
            }
          }
          return error;
        }
      ]
    }
  });
}

// Boards
export async function listBoards(archived?: boolean): Promise<FizzyBoard[]> {
  const client = await createClient();
  const params = archived !== undefined ? `?archived=${archived}` : '';
  const response = await client.get(`boards.json${params}`).json<FizzyBoard[]>();
  return response;
}

export async function getBoard(boardSlug: string): Promise<FizzyBoard> {
  const client = await createClient();
  const response = await client.get(`boards/${boardSlug}.json`).json<FizzyBoard>();
  return response;
}

export async function createBoard(name: string, description?: string): Promise<FizzyBoard> {
  const client = await createClient();
  const response = await client.post('boards.json', {
    json: { board: { name, description } }
  }).json<FizzyBoard>();
  return response;
}

export async function updateBoard(boardSlug: string, updates: { name?: string; description?: string }): Promise<FizzyBoard> {
  const client = await createClient();
  const response = await client.patch(`boards/${boardSlug}.json`, {
    json: { board: updates }
  }).json<FizzyBoard>();
  return response;
}

export async function deleteBoard(boardSlug: string): Promise<void> {
  const client = await createClient();
  await client.delete(`boards/${boardSlug}.json`);
}

export async function archiveBoard(boardSlug: string): Promise<FizzyBoard> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/archive.json`).json<FizzyBoard>();
  return response;
}

// Columns
export async function listColumns(boardSlug: string): Promise<FizzyColumn[]> {
  const client = await createClient();
  const response = await client.get(`boards/${boardSlug}/columns.json`).json<FizzyColumn[]>();
  return response;
}

export async function createColumn(boardSlug: string, name: string, position?: number): Promise<FizzyColumn> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/columns.json`, {
    json: { column: { name, position } }
  }).json<FizzyColumn>();
  return response;
}

export async function updateColumn(boardSlug: string, columnId: number, updates: { name?: string; position?: number }): Promise<FizzyColumn> {
  const client = await createClient();
  const response = await client.patch(`boards/${boardSlug}/columns/${columnId}.json`, {
    json: { column: updates }
  }).json<FizzyColumn>();
  return response;
}

export async function deleteColumn(boardSlug: string, columnId: number): Promise<void> {
  const client = await createClient();
  await client.delete(`boards/${boardSlug}/columns/${columnId}.json`);
}

// Cards
export async function listCards(
  boardSlug: string,
  options?: {
    column_id?: number;
    status?: 'open' | 'closed';
    assignee_id?: number;
    tag_id?: number;
    not_now?: boolean;
    page?: number;
  }
): Promise<FizzyCard[]> {
  const client = await createClient();
  const params = new URLSearchParams();
  if (options?.column_id) params.append('column_id', options.column_id.toString());
  if (options?.status) params.append('status', options.status);
  if (options?.assignee_id) params.append('assignee_id', options.assignee_id.toString());
  if (options?.tag_id) params.append('tag_id', options.tag_id.toString());
  if (options?.not_now !== undefined) params.append('not_now', options.not_now.toString());
  if (options?.page) params.append('page', options.page.toString());

  const queryString = params.toString() ? `?${params.toString()}` : '';
  const response = await client.get(`boards/${boardSlug}/cards.json${queryString}`).json<FizzyCard[]>();
  return response;
}

export async function getCard(boardSlug: string, cardNumber: number): Promise<FizzyCard> {
  const client = await createClient();
  const response = await client.get(`boards/${boardSlug}/cards/${cardNumber}.json`).json<FizzyCard>();
  return response;
}

export async function createCard(
  boardSlug: string,
  title: string,
  options?: {
    description?: string;
    column_id?: number;
    priority?: 'low' | 'normal' | 'high' | 'urgent';
    due_date?: string;
    assignee_ids?: number[];
    tag_ids?: number[];
  }
): Promise<FizzyCard> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards.json`, {
    json: { card: { title, ...options } }
  }).json<FizzyCard>();
  return response;
}

export async function updateCard(
  boardSlug: string,
  cardNumber: number,
  updates: {
    title?: string;
    description?: string;
    priority?: 'low' | 'normal' | 'high' | 'urgent' | null;
    due_date?: string | null;
  }
): Promise<FizzyCard> {
  const client = await createClient();
  const response = await client.patch(`boards/${boardSlug}/cards/${cardNumber}.json`, {
    json: { card: updates }
  }).json<FizzyCard>();
  return response;
}

export async function deleteCard(boardSlug: string, cardNumber: number): Promise<void> {
  const client = await createClient();
  await client.delete(`boards/${boardSlug}/cards/${cardNumber}.json`);
}

export async function closeCard(boardSlug: string, cardNumber: number): Promise<FizzyCard> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards/${cardNumber}/close.json`).json<FizzyCard>();
  return response;
}

export async function reopenCard(boardSlug: string, cardNumber: number): Promise<FizzyCard> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards/${cardNumber}/reopen.json`).json<FizzyCard>();
  return response;
}

export async function moveCard(boardSlug: string, cardNumber: number, columnId: number, position?: number): Promise<FizzyCard> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards/${cardNumber}/move.json`, {
    json: { column_id: columnId, position }
  }).json<FizzyCard>();
  return response;
}

export async function assignCard(boardSlug: string, cardNumber: number, assigneeIds: number[]): Promise<FizzyCard> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards/${cardNumber}/assign.json`, {
    json: { assignee_ids: assigneeIds }
  }).json<FizzyCard>();
  return response;
}

export async function unassignCard(boardSlug: string, cardNumber: number, assigneeIds: number[]): Promise<FizzyCard> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards/${cardNumber}/unassign.json`, {
    json: { assignee_ids: assigneeIds }
  }).json<FizzyCard>();
  return response;
}

export async function tagCard(boardSlug: string, cardNumber: number, tagIds: number[]): Promise<FizzyCard> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards/${cardNumber}/tag.json`, {
    json: { tag_ids: tagIds }
  }).json<FizzyCard>();
  return response;
}

export async function setNotNow(boardSlug: string, cardNumber: number, notNow: boolean): Promise<FizzyCard> {
  const client = await createClient();
  const response = await client.patch(`boards/${boardSlug}/cards/${cardNumber}.json`, {
    json: { card: { not_now: notNow } }
  }).json<FizzyCard>();
  return response;
}

// Steps
export async function listSteps(boardSlug: string, cardNumber: number): Promise<FizzyStep[]> {
  const client = await createClient();
  const response = await client.get(`boards/${boardSlug}/cards/${cardNumber}/steps.json`).json<FizzyStep[]>();
  return response;
}

export async function addStep(boardSlug: string, cardNumber: number, content: string): Promise<FizzyStep> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards/${cardNumber}/steps.json`, {
    json: { step: { content } }
  }).json<FizzyStep>();
  return response;
}

export async function completeStep(boardSlug: string, cardNumber: number, stepId: number): Promise<FizzyStep> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards/${cardNumber}/steps/${stepId}/complete.json`).json<FizzyStep>();
  return response;
}

export async function uncompleteStep(boardSlug: string, cardNumber: number, stepId: number): Promise<FizzyStep> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards/${cardNumber}/steps/${stepId}/uncomplete.json`).json<FizzyStep>();
  return response;
}

export async function deleteStep(boardSlug: string, cardNumber: number, stepId: number): Promise<void> {
  const client = await createClient();
  await client.delete(`boards/${boardSlug}/cards/${cardNumber}/steps/${stepId}.json`);
}

// Comments
export async function listComments(boardSlug: string, cardNumber: number): Promise<FizzyComment[]> {
  const client = await createClient();
  const response = await client.get(`boards/${boardSlug}/cards/${cardNumber}/comments.json`).json<FizzyComment[]>();
  return response;
}

export async function addComment(boardSlug: string, cardNumber: number, content: string): Promise<FizzyComment> {
  const client = await createClient();
  const response = await client.post(`boards/${boardSlug}/cards/${cardNumber}/comments.json`, {
    json: { comment: { content } }
  }).json<FizzyComment>();
  return response;
}

export async function updateComment(boardSlug: string, cardNumber: number, commentId: number, content: string): Promise<FizzyComment> {
  const client = await createClient();
  const response = await client.patch(`boards/${boardSlug}/cards/${cardNumber}/comments/${commentId}.json`, {
    json: { comment: { content } }
  }).json<FizzyComment>();
  return response;
}

export async function deleteComment(boardSlug: string, cardNumber: number, commentId: number): Promise<void> {
  const client = await createClient();
  await client.delete(`boards/${boardSlug}/cards/${cardNumber}/comments/${commentId}.json`);
}

// Tags
export async function listTags(boardSlug: string): Promise<FizzyTag[]> {
  const client = await createClient();
  const response = await client.get(`boards/${boardSlug}/tags.json`).json<FizzyTag[]>();
  return response;
}
