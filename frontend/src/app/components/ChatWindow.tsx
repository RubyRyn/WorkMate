import { useEffect, useRef, useState } from 'react';
import { Send, Paperclip, Bot } from 'lucide-react';
import { toast } from 'sonner';
import { Message } from './Message';
import { TypingIndicator } from './TypingIndicator';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { ScrollArea } from './ui/scroll-area';
import { sendChatMessage } from '../../services/api';
import type { ChatMessage } from '../../types/chat';

const suggestedPrompts = [
  'Summarize the key features from our Q1 product roadmap',
  'What are the latest updates in our engineering docs?',
  'Find action items from recent sprint planning notes',
  'Compare priorities across our connected workspaces',
];

export function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
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
        {messages.length === 0 && !isLoading ? (
          <div className="flex flex-col items-center justify-center h-full px-6 py-20">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-purple-600 text-white mb-4">
              <Bot className="h-7 w-7" />
            </div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
              How can I help you today?
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-8 text-center max-w-md">
              Ask me anything about your connected workspaces. I'll find answers backed by your Notion docs.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
              {suggestedPrompts.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => setInputValue(prompt)}
                  className="text-left rounded-lg border border-slate-200 dark:border-slate-700 p-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
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
        )}
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
