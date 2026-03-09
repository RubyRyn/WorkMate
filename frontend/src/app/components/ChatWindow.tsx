import { useState, useRef, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { Message } from './Message';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { sendChatMessage } from '../../services/api';
import type { ChatMessage } from '../../types/chat';

export function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const aiMessage = await sendChatMessage(inputValue);
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Sorry, something went wrong. ${error instanceof Error ? error.message : 'Please try again.'}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="border-b border-slate-200 px-6 py-4">
        <h2 className="text-lg font-semibold text-slate-900">Chat</h2>
        <p className="text-sm text-slate-500">Ask questions about your workspace</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto min-h-0">
        <div className="divide-y divide-slate-200">
          {messages.map((message) => (
            <Message
              key={message.id}
              role={message.role}
              content={message.content}
              citations={message.citations}
            />
          ))}
          {isLoading && <Message role="assistant" content="" isLoading />}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-slate-200 p-4 bg-white">
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
              className="min-h-[60px] max-h-[200px] resize-none border-slate-300 focus-visible:ring-purple-600"
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              className="border-slate-300 text-slate-600 hover:bg-slate-50"
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
        <p className="text-xs text-slate-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
