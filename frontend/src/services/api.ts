import type {
  ChatMessage,
  ConversationDetail,
  ConversationSummary,
  NotionWorkspace,
  SendMessageResponse,
  Source,
} from '../types/chat';
import { getToken } from './auth';

const BASE_URL = import.meta.env.VITE_API_URL ?? '/api';

function authHeaders(): Record<string, string> {
  const token = getToken();
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

function authHeadersRaw(): Record<string, string> {
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Send a chat message and get an AI response (stateless, legacy endpoint).
 */
export async function sendChatMessage(message: string): Promise<ChatMessage> {
  const res = await fetch(`${BASE_URL}/chat/ask`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ question: message }),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Chat request failed (${res.status}): ${detail}`);
  }

  const data = await res.json();

  return {
    id: Date.now().toString(),
    role: 'assistant',
    content: data.answer,
  };
}

// --- Conversation endpoints ---

export async function createConversation(): Promise<ConversationSummary> {
  const res = await fetch(`${BASE_URL}/api/conversations/`, {
    method: 'POST',
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Failed to create conversation (${res.status})`);
  return res.json();
}

export async function listConversations(): Promise<ConversationSummary[]> {
  const res = await fetch(`${BASE_URL}/api/conversations/`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Failed to list conversations (${res.status})`);
  return res.json();
}

export async function getConversation(id: number): Promise<ConversationDetail> {
  const res = await fetch(`${BASE_URL}/api/conversations/${id}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Failed to get conversation (${res.status})`);
  return res.json();
}

export async function sendConversationMessage(
  conversationId: number,
  question: string,
): Promise<SendMessageResponse> {
  const res = await fetch(`${BASE_URL}/api/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Failed to send message (${res.status}): ${detail}`);
  }
  return res.json();
}

export async function sendConversationMessageStream(
  conversationId: number,
  question: string,
  onChunk: (text: string) => void,
  onSources?: (sources: Source[]) => void,
): Promise<{ messageId?: number }> {
  const res = await fetch(`${BASE_URL}/api/conversations/${conversationId}/messages/stream`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Stream failed (${res.status}): ${detail}`);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let messageId: number | undefined;
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.done) {
            messageId = data.message_id;
            if (data.sources && onSources) {
              onSources(data.sources);
            }
          } else if (data.chunk) {
            onChunk(data.chunk);
          }
        } catch {
          // Ignore parse errors
        }
      }
    }
  }

  return { messageId };
}

export async function deleteConversation(id: number): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/conversations/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Failed to delete conversation (${res.status})`);
}

export async function renameConversation(id: number, title: string): Promise<ConversationSummary> {
  const res = await fetch(`${BASE_URL}/api/conversations/${id}`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(`Failed to rename conversation (${res.status})`);
  return res.json();
}

// --- File upload ---

export interface UploadResponse {
  filename: string;
  chunk_count: number;
  status: string;
  message: string;
}

export async function uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${BASE_URL}/api/upload/`, {
    method: 'POST',
    headers: authHeadersRaw(),
    body: formData,
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Upload failed (${res.status}): ${detail}`);
  }

  return res.json();
}

export async function uploadFiles(files: File[]): Promise<UploadResponse[]> {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }

  const res = await fetch(`${BASE_URL}/api/upload/batch`, {
    method: 'POST',
    headers: authHeadersRaw(),
    body: formData,
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Batch upload failed (${res.status}): ${detail}`);
  }

  return res.json();
}

/**
 * Fetch connected Notion workspaces.
 * Currently returns mock data.
 */
export async function getWorkspaces(): Promise<NotionWorkspace[]> {
  return [
    { id: '1', name: 'Product Requirements', pageCount: 24, connected: true },
    { id: '2', name: 'Engineering Docs', pageCount: 156, connected: true },
    { id: '3', name: 'Team Wiki', pageCount: 89, connected: true },
  ];
}
