import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, Copy, Check } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from './ui/button';
import { CitationBubble } from './CitationBubble';
import { useAuth } from '../contexts/AuthContext';
import type { Citation } from '../../types/chat';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp?: number;
}

function formatTime(ts: number): string {
  const date = new Date(ts);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const mins = Math.floor(diff / 60000);

  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function stripMarkdown(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/`{3}[\s\S]*?`{3}/g, (m) => m.replace(/`{3}.*?\n?/g, ''))
    .replace(/`(.*?)`/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\[(\d+)\]/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/^[-*+]\s+/gm, '- ')
    .trim();
}

export function Message({ role, content, citations = [], timestamp }: MessageProps) {
  const { user } = useAuth();
  const [imgError, setImgError] = useState(false);
  const [copied, setCopied] = useState(false);
  const isUser = role === 'user';

  const userInitial = user?.name?.charAt(0).toUpperCase() ?? 'U';
  const showPicture = isUser && user?.picture && !imgError;

  const handleCopy = async () => {
    const plain = stripMarkdown(content);
    await navigator.clipboard.writeText(plain);
    setCopied(true);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`group relative flex gap-4 p-6 ${
        isUser
          ? 'bg-white dark:bg-slate-900'
          : 'bg-slate-50 dark:bg-slate-800/50'
      }`}
    >
      {/* Copy button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={handleCopy}
        className="absolute top-2 right-2 h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
      >
        {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
      </Button>
      {/* Avatar */}
      {isUser ? (
        showPicture ? (
          <img
            src={user.picture!}
            alt={user.name}
            className="w-8 h-8 rounded-full object-cover flex-shrink-0"
            loading="eager"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-sm font-medium">
            {userInitial}
          </div>
        )
      ) : (
        <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-purple-600 text-white">
          <Bot className="w-5 h-5" />
        </div>
      )}

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="mb-1 flex items-baseline gap-2">
          <span className="font-semibold text-sm text-slate-900 dark:text-slate-100">
            {isUser ? (user?.name ?? 'You') : 'WorkMate'}
          </span>
          {timestamp && (
            <span className="text-xs text-slate-400 dark:text-slate-500">
              {formatTime(timestamp)}
            </span>
          )}
        </div>
        <div className="prose prose-sm max-w-none text-slate-700 dark:text-slate-300">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => {
                // Process text to add citation bubbles
                if (typeof children === 'string' && citations.length > 0) {
                  const parts = [];
                  let lastIndex = 0;
                  const citationRegex = /\[(\d+)\]/g;
                  let match;

                  while ((match = citationRegex.exec(children)) !== null) {
                    // Add text before citation
                    if (match.index > lastIndex) {
                      parts.push(children.substring(lastIndex, match.index));
                    }

                    // Add citation bubble
                    const citationNum = parseInt(match[1]);
                    const citation = citations.find(c => c.number === citationNum);
                    if (citation) {
                      parts.push(
                        <CitationBubble
                          key={`cite-${citationNum}-${match.index}`}
                          number={citation.number}
                          source={citation.source}
                          excerpt={citation.excerpt}
                        />
                      );
                    }

                    lastIndex = match.index + match[0].length;
                  }

                  // Add remaining text
                  if (lastIndex < children.length) {
                    parts.push(children.substring(lastIndex));
                  }

                  return <p className="mb-3">{parts.length > 0 ? parts : children}</p>;
                }
                return <p className="mb-3">{children}</p>;
              },
              ul: ({ children }) => (
                <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>
              ),
              code: ({ className, children }) => {
                const isInline = !className;
                if (isInline) {
                  return (
                    <code className="bg-purple-50 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 px-1.5 py-0.5 rounded text-sm font-mono">
                      {children}
                    </code>
                  );
                }
                return (
                  <code className="block bg-slate-900 dark:bg-slate-950 text-slate-100 p-4 rounded-lg overflow-x-auto">
                    {children}
                  </code>
                );
              },
              strong: ({ children }) => (
                <strong className="font-semibold text-slate-900 dark:text-slate-100">{children}</strong>
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
