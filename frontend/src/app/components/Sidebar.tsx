import { useState, useEffect } from 'react';
import {
  Database,
  ChevronRight,
  LogOut,
  Shield,
  MessageSquare,
  Plus,
  Trash2,
  Search,
  Pencil,
  X,
  Check,
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { useAuth } from '../contexts/AuthContext';
import { useIsAdmin } from '../../hooks/useIsAdmin';
import { listConversations, deleteConversation, renameConversation } from '../../services/api';
import { toast } from 'sonner';
import type { ConversationSummary, NotionWorkspace } from '../../types/chat';

const mockWorkspaces: NotionWorkspace[] = [
  { id: '1', name: 'Product Requirements', pageCount: 24, connected: true },
  { id: '2', name: 'Engineering Docs', pageCount: 156, connected: true },
  { id: '3', name: 'Team Wiki', pageCount: 89, connected: true },
];

interface SidebarProps {
  activeConversationId: number | null;
  onSelectConversation: (id: number | null, title?: string) => void;
  refreshKey: number;
  isOpen?: boolean;
  onClose?: () => void;
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

export function Sidebar({
  activeConversationId,
  onSelectConversation,
  refreshKey,
  isOpen = true,
  onClose,
}: SidebarProps) {
  const { user, logout } = useAuth();
  const isAdmin = useIsAdmin();
  const location = useLocation();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingTitle, setEditingTitle] = useState('');

  useEffect(() => {
    listConversations()
      .then(setConversations)
      .catch((err) => console.error('Failed to load conversations:', err));
  }, [refreshKey]);

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        onSelectConversation(null);
      }
      toast.success('Conversation deleted');
    } catch (err) {
      toast.error('Failed to delete conversation');
    }
  };

  const handleRenameStart = (e: React.MouseEvent, conv: ConversationSummary) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditingTitle(conv.title);
  };

  const handleRenameSubmit = async (id: number) => {
    if (!editingTitle.trim()) {
      setEditingId(null);
      return;
    }
    try {
      const updated = await renameConversation(id, editingTitle.trim());
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? { ...c, title: updated.title } : c)),
      );
      toast.success('Conversation renamed');
    } catch {
      toast.error('Failed to rename');
    }
    setEditingId(null);
  };

  const handleSelectConversation = (conv: ConversationSummary) => {
    onSelectConversation(conv.id, conv.title);
    onClose?.();
  };

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && onClose && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
        />
      )}
      <div
        className={`
          w-80 bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700
          h-screen overflow-hidden p-6 flex flex-col
          fixed md:relative z-50 md:z-auto
          transition-transform duration-200 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {/* Logo */}
        <div className="mb-6 flex-shrink-0 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-purple-700 dark:text-purple-400">WorkMate</h1>
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">Your AI Work Assistant</p>
          </div>
          {onClose && (
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden h-8 w-8 text-slate-400"
              onClick={onClose}
            >
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Conversations */}
        <div className="flex-1 min-h-0 flex flex-col mb-4">
          <div className="flex items-center justify-between mb-3 flex-shrink-0">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">Conversations</h2>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/30"
              onClick={() => {
                onSelectConversation(null);
                onClose?.();
              }}
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>

          {/* Search */}
          <div className="relative mb-3 flex-shrink-0">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="w-full pl-8 pr-3 py-1.5 text-sm rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
          </div>

          <div className="flex-1 overflow-y-auto space-y-1.5">
            {filteredConversations.length === 0 && (
              <p className="text-xs text-slate-400 text-center py-4">
                {searchQuery ? 'No matches' : 'No conversations yet'}
              </p>
            )}
            {filteredConversations.map((conv) => (
              <Card
                key={conv.id}
                onClick={() => handleSelectConversation(conv)}
                className={`p-2.5 transition-colors cursor-pointer border-slate-200 dark:border-slate-700 group ${
                  activeConversationId === conv.id
                    ? 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-700'
                    : 'hover:bg-white dark:hover:bg-slate-800'
                }`}
              >
                <div className="flex items-start gap-1.5">
                  <div className="flex-1 min-w-0">
                    {editingId === conv.id ? (
                      <div className="flex items-center gap-1">
                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleRenameSubmit(conv.id);
                            if (e.key === 'Escape') setEditingId(null);
                          }}
                          onClick={(e) => e.stopPropagation()}
                          autoFocus
                          className="w-full text-sm px-1 py-0.5 rounded border border-purple-300 dark:border-purple-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none"
                        />
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRenameSubmit(conv.id);
                          }}
                          className="p-0.5 text-green-500 hover:text-green-600"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <h3 className="font-medium text-sm text-slate-900 dark:text-slate-100 truncate">
                          {conv.title}
                        </h3>
                        <span className="text-xs text-slate-500 dark:text-slate-400">
                          {formatTime(conv.updated_at)}
                        </span>
                      </>
                    )}
                  </div>
                  {editingId !== conv.id && (
                    <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 text-slate-400 hover:text-purple-500"
                        onClick={(e) => handleRenameStart(e, conv)}
                      >
                        <Pencil className="w-3 h-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 text-slate-400 hover:text-red-500"
                        onClick={(e) => handleDelete(e, conv.id)}
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Connected Notion Workspaces */}
        <div className="mb-4 flex-shrink-0">
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            <h2 className="font-semibold text-slate-900 dark:text-slate-100">Connected Workspaces</h2>
          </div>
          <div className="space-y-1.5">
            {mockWorkspaces.map((workspace) => (
              <Card
                key={workspace.id}
                className="p-2.5 hover:bg-white dark:hover:bg-slate-800 transition-colors cursor-pointer border-slate-200 dark:border-slate-700"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-green-500" />
                      <h3 className="font-medium text-sm text-slate-900 dark:text-slate-100">{workspace.name}</h3>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      {workspace.pageCount} pages indexed
                    </p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Navigation Links */}
        <div className="space-y-1 flex-shrink-0">
          <Link
            to="/"
            className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              location.pathname === '/'
                ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300'
                : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800'
            }`}
          >
            <MessageSquare className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            Chat
          </Link>
          {isAdmin && (
            <Link
              to="/admin"
              className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                location.pathname === '/admin'
                  ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300'
                  : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800'
              }`}
            >
              <Shield className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              User Management
            </Link>
          )}
        </div>

        {/* User Info */}
        {user && (
          <div className="mt-4 border-t border-slate-200 dark:border-slate-700 pt-4 flex-shrink-0">
            <div className="flex items-center gap-3">
              {user.picture ? (
                <img
                  src={user.picture}
                  alt={user.name}
                  className="h-9 w-9 rounded-full"
                  referrerPolicy="no-referrer"
                />
              ) : (
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900 text-sm font-medium text-purple-700 dark:text-purple-300">
                  {user.name.charAt(0).toUpperCase()}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">{user.name}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{user.email}</p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={logout}
                className="h-8 w-8 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
