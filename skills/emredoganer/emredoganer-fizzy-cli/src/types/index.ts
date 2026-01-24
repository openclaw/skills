export interface FizzyConfig {
  token?: string;
  currentAccountSlug?: string;
}

export interface FizzyAccount {
  slug: string;
  name: string;
}

export interface FizzyBoard {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  columns_count: number;
  cards_count: number;
  archived: boolean;
  url: string;
}

export interface FizzyColumn {
  id: number;
  name: string;
  position: number;
  cards_count: number;
  board_id: number;
  created_at: string;
  updated_at: string;
}

export interface FizzyCard {
  id: number;
  number: number;
  title: string;
  description: string | null;
  status: 'open' | 'closed';
  priority: 'low' | 'normal' | 'high' | 'urgent' | null;
  position: number;
  column_id: number;
  column_name: string;
  board_id: number;
  board_name: string;
  assignees: FizzyUser[];
  tags: FizzyTag[];
  steps_count: number;
  completed_steps_count: number;
  comments_count: number;
  due_date: string | null;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
  creator: FizzyUser;
  url: string;
  not_now: boolean;
}

export interface FizzyUser {
  id: number;
  name: string;
  email: string;
  avatar_url: string | null;
}

export interface FizzyTag {
  id: number;
  name: string;
  color: string;
}

export interface FizzyStep {
  id: number;
  content: string;
  completed: boolean;
  position: number;
  card_id: number;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  completed_by: FizzyUser | null;
}

export interface FizzyComment {
  id: number;
  content: string;
  card_id: number;
  author: FizzyUser;
  created_at: string;
  updated_at: string;
}

export interface FizzyMe {
  id: number;
  name: string;
  email: string;
  avatar_url: string | null;
  accounts: FizzyAccount[];
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    current_page: number;
    total_pages: number;
    total_count: number;
    per_page: number;
  };
}
