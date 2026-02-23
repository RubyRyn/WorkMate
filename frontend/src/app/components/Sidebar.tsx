import { FileText, Database, Clock, ChevronRight, LogOut } from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { useAuth } from '../contexts/AuthContext';
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

export function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <div className="w-80 bg-slate-50 border-r border-slate-200 h-screen overflow-y-auto p-6 flex flex-col">
      {/* Logo */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-purple-700">WorkMate</h1>
        <p className="text-sm text-slate-600 mt-1">Your AI Work Assistant</p>
      </div>

      {/* Connected Notion Workspaces */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-5 h-5 text-purple-600" />
          <h2 className="font-semibold text-slate-900">Connected Workspaces</h2>
        </div>
        <div className="space-y-2">
          {mockWorkspaces.map((workspace) => (
            <Card
              key={workspace.id}
              className="p-3 hover:bg-white transition-colors cursor-pointer border-slate-200"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <h3 className="font-medium text-sm text-slate-900">{workspace.name}</h3>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
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
          <Clock className="w-5 h-5 text-purple-600" />
          <h2 className="font-semibold text-slate-900">Recent Analysis</h2>
        </div>
        <div className="space-y-2">
          {mockProjects.map((project) => (
            <Card
              key={project.id}
              className="p-3 hover:bg-white transition-colors cursor-pointer border-slate-200"
            >
              <div className="flex items-start gap-2">
                <FileText className="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-sm text-slate-900 truncate">
                    {project.name}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-slate-500">{project.lastAnalyzed}</span>
                    {project.status === 'completed' && (
                      <span className="text-xs text-green-600">✓</span>
                    )}
                    {project.status === 'in-progress' && (
                      <span className="text-xs text-purple-600">●</span>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* User Info */}
      {user && (
        <div className="mt-6 border-t border-slate-200 pt-4">
          <div className="flex items-center gap-3">
            {user.picture ? (
              <img
                src={user.picture}
                alt={user.name}
                className="h-9 w-9 rounded-full"
                referrerPolicy="no-referrer"
              />
            ) : (
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-purple-100 text-sm font-medium text-purple-700">
                {user.name.charAt(0).toUpperCase()}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-900 truncate">{user.name}</p>
              <p className="text-xs text-slate-500 truncate">{user.email}</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={logout}
              className="h-8 w-8 text-slate-400 hover:text-slate-600"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
