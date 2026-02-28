import { FileText, Database, Clock, ChevronRight, LogOut, Shield, Sun, Moon, MessageSquare, Settings } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { useIsAdmin } from '../../hooks/useIsAdmin';
import type { NotionWorkspace, RecentProject } from '../../types/chat';

const mockWorkspaces: NotionWorkspace[] = [
  { id: '1', name: 'Product Requirements', pageCount: 24, connected: true },
  { id: '2', name: 'Engineering Docs', pageCount: 156, connected: true },
  { id: '3', name: 'Team Wiki', pageCount: 89, connected: true },
];

const mockProjects: RecentProject[] = [
  { id: '1', name: 'Q1 Feature Roadmap', lastAnalyzed: '2 hours ago', status: 'completed' },
  { id: '2', name: 'API Documentation Review', lastAnalyzed: '5 hours ago', status: 'completed' },
  { id: '3', name: 'Sprint Planning Notes', lastAnalyzed: '1 day ago', status: 'in-progress' },
];

interface SidebarContentProps {
  onNavigate?: () => void;
}

export function SidebarContent({ onNavigate }: SidebarContentProps) {
  const { user, logout } = useAuth();
  const { resolvedTheme, toggleTheme } = useTheme();
  const isAdmin = useIsAdmin();

  return (
    <div className="w-80 bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700 h-screen overflow-y-auto p-6 flex flex-col">
      {/* Logo + Theme Toggle */}
      <div className="mb-8 flex items-start justify-between">
        <Link to="/" onClick={onNavigate} className="block">
          <h1 className="text-2xl font-bold text-purple-700 dark:text-purple-400">WorkMate</h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">Your AI Work Assistant</p>
        </Link>
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="h-8 w-8 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
        >
          {resolvedTheme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
        </Button>
      </div>

      {/* Connected Notion Workspaces */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          <h2 className="font-semibold text-slate-900 dark:text-slate-100">Connected Workspaces</h2>
        </div>
        <div className="space-y-2">
          {mockWorkspaces.map((workspace) => (
            <Card
              key={workspace.id}
              className="p-3 hover:bg-white dark:hover:bg-slate-800 transition-colors cursor-pointer border-slate-200 dark:border-slate-700 dark:bg-slate-800/50"
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

      {/* Recent Project Analysis */}
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-4">
          <Clock className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          <h2 className="font-semibold text-slate-900 dark:text-slate-100">Recent Analysis</h2>
        </div>
        <div className="space-y-2">
          {mockProjects.map((project) => (
            <Card
              key={project.id}
              className="p-3 hover:bg-white dark:hover:bg-slate-800 transition-colors cursor-pointer border-slate-200 dark:border-slate-700 dark:bg-slate-800/50"
            >
              <div className="flex items-start gap-2">
                <FileText className="w-4 h-4 text-purple-500 dark:text-purple-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-sm text-slate-900 dark:text-slate-100 truncate">
                    {project.name}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-slate-500 dark:text-slate-400">{project.lastAnalyzed}</span>
                    {project.status === 'completed' && (
                      <span className="text-xs text-green-600 dark:text-green-400">✓</span>
                    )}
                    {project.status === 'in-progress' && (
                      <span className="text-xs text-purple-600 dark:text-purple-400">●</span>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Navigation */}
      <div className="mt-4 space-y-1">
        <Link
          to="/"
          onClick={onNavigate}
          className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
        >
          <MessageSquare className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          Chat
        </Link>
        <Link
          to="/settings"
          onClick={onNavigate}
          className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
        >
          <Settings className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          Settings
        </Link>
        {isAdmin && (
          <Link
            to="/admin"
            onClick={onNavigate}
            className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
          >
            <Shield className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            User Management
          </Link>
        )}
      </div>

      {/* User Info */}
      {user && (
        <div className="mt-6 border-t border-slate-200 dark:border-slate-700 pt-4">
          <div className="flex items-center gap-3">
            {user.picture ? (
              <img
                src={user.picture}
                alt={user.name}
                className="h-9 w-9 rounded-full"
                loading="eager"
              />
            ) : (
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900/50 text-sm font-medium text-purple-700 dark:text-purple-300">
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
              onClick={() => { logout(); onNavigate?.(); }}
              className="h-8 w-8 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export function Sidebar() {
  return <SidebarContent />;
}
