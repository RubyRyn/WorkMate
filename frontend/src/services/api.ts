import type { ChatMessage, NotionWorkspace } from '../types/chat';
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

/**
 * Send a chat message and get an AI response.
 * Currently returns a mock response. Uncomment the fetch call
 * when the Python backend is ready.
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

/**
 * Fetch connected Notion workspaces.
 * Currently returns mock data.
 */
export async function getWorkspaces(): Promise<NotionWorkspace[]> {
  // --- Uncomment when backend is ready ---
  // const res = await fetch(`${BASE_URL}/workspaces`, {
  //   headers: authHeaders(),
  // });
  // if (!res.ok) throw new Error(`Workspaces request failed: ${res.status}`);
  // return res.json();

  return [
    { id: '1', name: 'Product Requirements', pageCount: 24, connected: true },
    { id: '2', name: 'Engineering Docs', pageCount: 156, connected: true },
    { id: '3', name: 'Team Wiki', pageCount: 89, connected: true },
  ];
}
