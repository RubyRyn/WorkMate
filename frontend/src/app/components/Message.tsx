import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Bot } from 'lucide-react';
import { CitationBubble } from './CitationBubble';
import { Skeleton } from './ui/skeleton';
import type { Citation } from '../../types/chat';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  isLoading?: boolean;
}

export function Message({ role, content, citations = [], isLoading = false }: MessageProps) {
  const isUser = role === 'user';

  if (isLoading) {
    return (
      <div className="flex gap-4 p-6 bg-white">
        <Skeleton className="w-8 h-8 rounded-full flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex gap-4 p-6 ${
        isUser ? 'bg-white' : 'bg-slate-50'
      }`}
    >
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser
            ? 'bg-slate-200 text-slate-700'
            : 'bg-purple-600 text-white'
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="mb-1">
          <span className="font-semibold text-sm text-slate-900">
            {isUser ? 'You' : 'WorkMate'}
          </span>
        </div>
        <div className="prose prose-sm max-w-none text-slate-700">
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
                    <code className="bg-purple-50 text-purple-800 px-1.5 py-0.5 rounded text-sm font-mono">
                      {children}
                    </code>
                  );
                }
                return (
                  <code className="block bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto">
                    {children}
                  </code>
                );
              },
              strong: ({ children }) => (
                <strong className="font-semibold text-slate-900">{children}</strong>
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
