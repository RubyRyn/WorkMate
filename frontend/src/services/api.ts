import type { ChatMessage, NotionWorkspace } from '../types/chat';

const BASE_URL = import.meta.env.VITE_API_URL ?? '/api';

/**
 * Send a chat message and get an AI response.
 * Currently returns a mock response. Uncomment the fetch call
 * when the Python backend is ready.
 */
export async function sendChatMessage(message: string): Promise<ChatMessage> {
  // --- Uncomment when backend is ready ---
  // const res = await fetch(`${BASE_URL}/chat`, {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ message }),
  // });
  // if (!res.ok) throw new Error(`Chat request failed: ${res.status}`);
  // return res.json();

  // Mock response (simulates ~2s latency)
  await new Promise((resolve) => setTimeout(resolve, 2000));

  return {
    id: (Date.now() + 1).toString(),
    role: 'assistant',
    content: `I've analyzed your question about "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}".

Based on the information in your connected Notion workspaces, here's what I found:

This is a **simulated response** to demonstrate the chat interface. In a production environment, this would connect to your actual knowledge base and provide contextual answers with proper citations.

Key points:
- Real-time analysis of workspace data
- Contextual understanding of your documents
- Citation-backed responses for transparency`,
  };
}

/**
 * Fetch connected Notion workspaces.
 * Currently returns mock data.
 */
export async function getWorkspaces(): Promise<NotionWorkspace[]> {
  // --- Uncomment when backend is ready ---
  // const res = await fetch(`${BASE_URL}/workspaces`);
  // if (!res.ok) throw new Error(`Workspaces request failed: ${res.status}`);
  // return res.json();

  return [
    { id: '1', name: 'Product Requirements', pageCount: 24, connected: true },
    { id: '2', name: 'Engineering Docs', pageCount: 156, connected: true },
    { id: '3', name: 'Team Wiki', pageCount: 89, connected: true },
  ];
}
