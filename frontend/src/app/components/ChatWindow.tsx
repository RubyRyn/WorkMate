import { useEffect, useRef, useState } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { toast } from 'sonner';
import { Message } from './Message';
import { TypingIndicator } from './TypingIndicator';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { ScrollArea } from './ui/scroll-area';
import { sendChatMessage } from '../../services/api';
import type { ChatMessage } from '../../types/chat';

const initialMessages: ChatMessage[] = [
  {
    id: '1',
    role: 'user',
    content: 'Can you summarize the key features from our Q1 product roadmap?',
    timestamp: Date.now() - 3600000,
  },
  {
    id: '2',
    role: 'assistant',
    content: `Based on your Q1 product roadmap, here are the key features planned:

**1. Advanced Analytics Dashboard** [1]
The team is planning to build a comprehensive analytics dashboard with real-time data visualization and customizable reports.

**2. Mobile App Integration** [2]
A native mobile application for both iOS and Android is scheduled for development, enabling users to access core features on the go.

**3. API Enhancements** [3]
Major improvements to the REST API including better rate limiting, webhook support, and enhanced documentation.

These features align with the company's strategic goals of improving user engagement and expanding platform capabilities.`,
    citations: [
      {
        number: 1,
        source: 'Q1 Feature Roadmap - Analytics Section',
        excerpt: 'Priority 1: Develop advanced analytics dashboard with customizable widgets and real-time data streaming capabilities',
      },
      {
        number: 2,
        source: 'Q1 Feature Roadmap - Mobile Strategy',
        excerpt: 'Native mobile apps planned for Q1 release, focusing on core workflow features with offline support',
      },
      {
        number: 3,
        source: 'Engineering Docs - API Specifications',
        excerpt: 'API v2.0 will include webhook subscriptions, improved rate limiting (10k req/hour), and comprehensive OpenAPI documentation',
      },
    ],
    timestamp: Date.now() - 3540000,
  },
];

export function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const aiMessage = await sendChatMessage(inputValue);
      aiMessage.timestamp = Date.now();
      setMessages((prev) => [...prev, aiMessage]);
    } catch {
      toast.error('Failed to get a response. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-white dark:bg-slate-900">
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-slate-700 px-6 py-4">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Chat</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">Ask questions about your workspace</p>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 min-h-0">
        <div className="divide-y divide-slate-200 dark:divide-slate-700">
          {messages.map((message) => (
            <Message
              key={message.id}
              role={message.role}
              content={message.content}
              citations={message.citations}
              timestamp={message.timestamp}
            />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="shrink-0 border-t border-slate-200 dark:border-slate-700 p-4 bg-white dark:bg-slate-900">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <Textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask WorkMate anything about your workspace..."
              className="min-h-[60px] max-h-[200px] resize-none border-slate-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 focus-visible:ring-purple-600"
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              className="border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
            >
              <Paperclip className="w-5 h-5" />
            </Button>
            <Button
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              className="bg-purple-600 hover:bg-purple-700 text-white"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
