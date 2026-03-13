import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, Copy, Check, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';
import type { Source } from '../../types/chat';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  citations?: unknown[];
  sources?: Source[];
  isLoading?: boolean;
  timestamp?: string;
}

function formatTimestamp(ts: string): string {
  const date = new Date(ts);
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

/** Extract confidence level and strip it + inline citations from content */
function parseAssistantContent(raw: string): { cleanContent: string; confidence: string | null } {
  let text = raw;

  // Extract "Confidence: High/Medium/Low"
  const confMatch = text.match(/\bConfidence:\s*(High|Medium|Low)\b/i);
  const confidence = confMatch ? confMatch[1] : null;
  if (confMatch) {
    text = text.replace(confMatch[0], '');
  }

  // Strip "Answer:" prefix if present
  text = text.replace(/^Answer:\s*/i, '');

  // Strip inline citations like [Document name, section, paragraph]
  // These are bracket-wrapped references that aren't markdown links
  text = text.replace(/\s*\[[^\]]*(?:Notes|Milestones|Checklist|docs|Document)[^\]]*\]/gi, '');

  // Clean up extra whitespace
  text = text.replace(/\n{3,}/g, '\n\n').trim();

  return { cleanContent: text, confidence };
}

const confidenceColors: Record<string, string> = {
  High: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  Medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  Low: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
};

export function Message({ role, content, sources = [], isLoading = false, timestamp }: MessageProps) {
  const { user } = useAuth();
  const isUser = role === 'user';
  const [copied, setCopied] = useState(false);
  const [sourcesExpanded, setSourcesExpanded] = useState(false);

  const { cleanContent, confidence } = !isUser ? parseAssistantContent(content) : { cleanContent: content, confidence: null };
  const displayContent = isUser ? content : cleanContent;

  const handleCopy = () => {
    navigator.clipboard.writeText(displayContent);
    setCopied(true);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  if (isLoading) {
    return (
      <div className="flex gap-4 p-6 bg-purple-50/50 dark:bg-slate-800/50">
        <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 bg-purple-600 text-white shadow-sm">
          <Bot className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="mb-1">
            <span className="font-semibold text-sm text-slate-900 dark:text-slate-100">WorkMate</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:0ms]" />
              <span className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:150ms]" />
              <span className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
            <span>Thinking...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`group flex gap-4 p-6 ${
        isUser
          ? 'bg-white dark:bg-slate-900'
          : 'bg-purple-50/50 dark:bg-slate-800/50'
      }`}
    >
      {/* Avatar */}
      {isUser ? (
        user?.picture ? (
          <img
            src={user.picture}
            alt={user.name}
            className="w-9 h-9 rounded-full flex-shrink-0 shadow-sm"
            referrerPolicy="no-referrer"
          />
        ) : (
          <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 font-semibold text-sm shadow-sm">
            {user?.name?.charAt(0).toUpperCase() ?? 'U'}
          </div>
        )
      ) : (
        <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 bg-purple-600 text-white shadow-sm">
          <Bot className="w-5 h-5" />
        </div>
      )}

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="mb-1 flex items-center gap-2">
          <span className="font-semibold text-sm text-slate-900 dark:text-slate-100">
            {isUser ? (user?.name ?? 'You') : 'WorkMate'}
          </span>
          {timestamp && (
            <span className="text-xs text-slate-400 dark:text-slate-500">
              {formatTimestamp(timestamp)}
            </span>
          )}
          {/* Confidence badge */}
          {confidence && (
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${confidenceColors[confidence] ?? ''}`}>
              {confidence}
            </span>
          )}
          {/* Copy button for assistant messages */}
          {!isUser && displayContent && (
            <button
              onClick={handleCopy}
              className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-green-500" />
              ) : (
                <Copy className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
              )}
            </button>
          )}
        </div>
        <div className="prose prose-sm max-w-none text-slate-700 dark:text-slate-300 dark:prose-invert">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => <p className="mb-3">{children}</p>,
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
            {displayContent}
          </ReactMarkdown>
        </div>

        {/* Sources section for assistant messages */}
        {!isUser && sources.length > 0 && (
          <div className="mt-3">
            <button
              onClick={() => setSourcesExpanded(!sourcesExpanded)}
              className="flex items-center gap-1.5 text-xs font-medium text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 transition-colors"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>{sources.length} source{sources.length !== 1 ? 's' : ''}</span>
              {sourcesExpanded ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </button>
            {sourcesExpanded && (
              <div className="mt-2 space-y-2">
                {sources.map((source, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2.5 rounded-lg border border-purple-200 dark:border-purple-800/50 bg-purple-50/50 dark:bg-purple-900/20 p-3"
                  >
                    <div className="flex items-center justify-center w-5 h-5 rounded-full bg-purple-100 dark:bg-purple-800/50 text-purple-700 dark:text-purple-300 text-xs font-semibold flex-shrink-0 mt-0.5">
                      {i + 1}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                        {source.title}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
                        {source.excerpt}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
