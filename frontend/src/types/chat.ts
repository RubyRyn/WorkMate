export interface Citation {
  number: number;
  source: string;
  excerpt: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

export interface NotionWorkspace {
  id: string;
  name: string;
  pageCount: number;
  connected: boolean;
}

export interface RecentProject {
  id: string;
  name: string;
  lastAnalyzed: string;
  status: 'completed' | 'in-progress' | 'pending';
}
