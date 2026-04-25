import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Send, Paperclip, MessageSquare, Upload, Sparkles, Download, Menu, Database } from 'lucide-react';
import { Message } from './Message';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { ThemeToggle } from './ThemeToggle';
import { toast } from 'sonner';
import {
  createConversation,
  getConversation,
  sendConversationMessageStream,
  uploadFile,
  uploadFiles,
  getWorkspaces,
} from '../../services/api';
import { exportConversationAsMarkdown } from '../../utils/exportMarkdown';
import type { ChatMessage, NotionWorkspace } from '../../types/chat';

interface ChatWindowProps {
  conversationId: number | null;
  conversationTitle?: string | null;
  onConversationCreated: (id: number) => void;
  onTitleChange?: (title: string) => void;
  onMenuClick?: () => void;
}

export function ChatWindow({ conversationId, conversationTitle, onConversationCreated, onTitleChange, onMenuClick }: ChatWindowProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [workspaces, setWorkspaces] = useState<NotionWorkspace[] | null>(null);

  useEffect(() => {
    getWorkspaces()
      .then(setWorkspaces)
      .catch(() => setWorkspaces([]));
  }, []);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const quickSendRef = useRef<((msg: string) => void) | null>(null);
  const justCreatedRef = useRef<number | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  useEffect(() => {
    if (conversationId === null) {
      setMessages([]);
      return;
    }

    if (justCreatedRef.current === conversationId) {
      justCreatedRef.current = null;
      return;
    }

    let cancelled = false;
    getConversation(conversationId)
      .then((conv) => {
        if (!cancelled) {
          setMessages(
            conv.messages.map((m) => ({
              id: String(m.id),
              role: m.role as 'user' | 'assistant',
              content: m.content,
              timestamp: m.timestamp,
            })),
          );
        }
      })
      .catch((err) => {
        if (!cancelled) console.error('Failed to load conversation:', err);
      });

    return () => {
      cancelled = true;
    };
  }, [conversationId]);

  const sendMessage = async (message: string) => {
    if (!message.trim()) return;

    const question = message;
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      let activeId = conversationId;
      if (activeId === null) {
        const conv = await createConversation();
        activeId = conv.id;
        justCreatedRef.current = activeId;
        onConversationCreated(activeId);
        // Set title from first message (will be auto-titled by backend)
        const shortTitle = question.slice(0, 50) + (question.length > 50 ? '...' : '');
        onTitleChange?.(shortTitle);
      }

      // Streaming response
      const aiMessageId = `ai-${Date.now()}`;
      let firstChunk = true;

      await sendConversationMessageStream(
        activeId,
        question,
        (chunk) => {
          if (firstChunk) {
            firstChunk = false;
            setIsLoading(false);
            setMessages((prev) => [
              ...prev,
              { id: aiMessageId, role: 'assistant', content: chunk, timestamp: new Date().toISOString() },
            ]);
          } else {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === aiMessageId ? { ...m, content: m.content + chunk } : m,
              ),
            );
          }
        },
        (sources) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiMessageId ? { ...m, sources } : m,
            ),
          );
        },
      );
    } catch (error) {
      setIsLoading(false);
      toast.error(
        error instanceof Error ? error.message : 'Something went wrong. Please try again.',
      );
    }
  };

  const handleSend = () => sendMessage(inputValue);
  quickSendRef.current = sendMessage;

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (!fileList || fileList.length === 0) return;
    e.target.value = '';

    const files = Array.from(fileList);

    // Client-side size check
    for (const file of files) {
      if (file.size > 10 * 1024 * 1024) {
        toast.error(`"${file.name}" is too large. Maximum size is 10 MB.`);
        return;
      }
    }

    setIsUploading(true);
    try {
      if (files.length === 1) {
        const result = await uploadFile(files[0]);
        toast.success(result.message);
      } else {
        const results = await uploadFiles(files);
        const totalChunks = results.reduce((sum, r) => sum + r.chunk_count, 0);
        toast.success(`${results.length} files uploaded (${totalChunks} chunks indexed)`);
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleExport = () => {
    if (messages.length === 0) return;
    exportConversationAsMarkdown(messages, 'WorkMate Conversation');
    toast.success('Conversation exported');
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-white dark:bg-slate-900">
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-slate-700 px-4 md:px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {onMenuClick && (
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden h-8 w-8 text-slate-500"
              onClick={onMenuClick}
            >
              <Menu className="w-5 h-5" />
            </Button>
          )}
          <div>
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              {conversationTitle && conversationId ? conversationTitle : 'Chat'}
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {conversationTitle && conversationId ? 'Conversation' : 'Ask questions about your workspace'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
              onClick={handleExport}
              title="Export conversation"
            >
              <Download className="w-4 h-4" />
            </Button>
          )}
          <ThemeToggle />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto min-h-0">
        {messages.length === 0 && !isLoading && workspaces !== null && workspaces.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full px-6 text-center">
            <div className="w-16 h-16 rounded-2xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mb-6">
              <Database className="w-8 h-8 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
              Welcome to WorkMate 👋
            </h3>
            <p className="text-slate-500 dark:text-slate-400 mb-8 max-w-md">
              Connect a Notion workspace to start asking questions across your docs. WorkMate will search your pages and answer with sources cited.
            </p>
            <Link to="/app/settings">
              <Button className="bg-purple-600 hover:bg-purple-700 text-white px-6 h-11">
                Connect Notion
              </Button>
            </Link>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-6 max-w-md">
              You can also upload PDF, TXT, or Markdown files to chat with — use the paperclip below.
            </p>
          </div>
        ) : messages.length === 0 && !isLoading ? (
          <div className="flex flex-col items-center justify-center h-full px-6 text-center">
            <div className="w-16 h-16 rounded-2xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mb-6">
              <Sparkles className="w-8 h-8 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
              Welcome to WorkMate
            </h3>
            <p className="text-slate-500 dark:text-slate-400 mb-8 max-w-md">
              Your AI-powered workspace assistant. Ask questions about your Notion docs, upload files for analysis, or start a conversation.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-lg w-full">
              <button
                onClick={() => setInputValue('What are the key takeaways from my workspace?')}
                className="flex flex-col items-center gap-2 rounded-xl border border-slate-200 dark:border-slate-700 p-4 text-left hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-purple-200 dark:hover:border-purple-700 transition-colors"
              >
                <MessageSquare className="w-5 h-5 text-purple-500" />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Ask a question</span>
                <span className="text-xs text-slate-400">Query your workspace docs</span>
              </button>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex flex-col items-center gap-2 rounded-xl border border-slate-200 dark:border-slate-700 p-4 text-left hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-purple-200 dark:hover:border-purple-700 transition-colors"
              >
                <Upload className="w-5 h-5 text-purple-500" />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Upload files</span>
                <span className="text-xs text-slate-400">PDF, TXT, or Markdown</span>
              </button>
              <button
                onClick={() => {
                  setInputValue('Summarize the latest project updates');
                  setTimeout(() => quickSendRef.current?.('Summarize the latest project updates'), 0);
                }}
                className="flex flex-col items-center gap-2 rounded-xl border border-slate-200 dark:border-slate-700 p-4 text-left hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-purple-200 dark:hover:border-purple-700 transition-colors"
              >
                <Sparkles className="w-5 h-5 text-purple-500" />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Get insights</span>
                <span className="text-xs text-slate-400">Summaries and analysis</span>
              </button>
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
                sources={message.sources}
                timestamp={message.timestamp}
              />
            ))}
            {isLoading && <Message role="assistant" content="" isLoading />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-slate-200 dark:border-slate-700 p-4 bg-white dark:bg-slate-900">
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
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.md"
              multiple
              className="hidden"
              onChange={handleFileUpload}
            />
            <Button
              variant="outline"
              size="icon"
              className="border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
              disabled={isUploading}
              onClick={() => fileInputRef.current?.click()}
            >
              <Paperclip className={`w-5 h-5 ${isUploading ? 'animate-pulse' : ''}`} />
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
