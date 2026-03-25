export interface Citation {
  number: number;
  source: string;
  excerpt: string;
  url?: string;
}

export interface Source {
  title: string;
  excerpt: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  sources?: Source[];
  timestamp?: string;
}

export interface NotionWorkspace {
  id: number;
  workspace_id: string;
  workspace_name: string;
  workspace_icon: string | null;
  sync_status: string;
  last_synced_at: string | null;
  connected_at: string;
}

export interface RecentProject {
  id: string;
  name: string;
  lastAnalyzed: string;
  status: 'completed' | 'in-progress' | 'pending';
}

export interface ConversationSummary {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail {
  id: number;
  title: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

export interface SendMessageResponse {
  user_message: ChatMessage;
  assistant_message: ChatMessage;
}
