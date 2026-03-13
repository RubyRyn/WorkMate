import type { ChatMessage } from '../types/chat';

export function exportConversationAsMarkdown(messages: ChatMessage[], title?: string) {
  const lines: string[] = [];
  if (title) {
    lines.push(`# ${title}`, '');
  }

  for (const msg of messages) {
    const sender = msg.role === 'user' ? 'You' : 'WorkMate';
    const time = msg.timestamp
      ? new Date(msg.timestamp).toLocaleString()
      : '';
    lines.push(`**${sender}**${time ? ` (${time})` : ''}:`, msg.content, '');
  }

  const blob = new Blob([lines.join('\n')], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${(title || 'conversation').replace(/[^a-zA-Z0-9]/g, '_')}.md`;
  a.click();
  URL.revokeObjectURL(url);
}
