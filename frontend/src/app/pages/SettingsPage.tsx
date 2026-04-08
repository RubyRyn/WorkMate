import { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Sun, Moon, Monitor, Link2, RefreshCw, Unplug, Plus, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from 'next-themes';
import { updateProfile, deleteAccount } from '../../services/auth';
import { getNotionAuthUrl, getWorkspaces, disconnectWorkspace, syncWorkspace } from '../../services/api';
import type { NotionWorkspace } from '../../types/chat';

export function SettingsPage() {
  const { user, logout, updateUser } = useAuth();
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();

  const [searchParams, setSearchParams] = useSearchParams();
  const [name, setName] = useState(user?.name ?? '');
  const [saving, setSaving] = useState(false);
  const [workspaces, setWorkspaces] = useState<NotionWorkspace[]>([]);
  const [loadingWorkspaces, setLoadingWorkspaces] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [syncingId, setSyncingId] = useState<number | null>(null);

  useEffect(() => {
    loadWorkspaces();
    // Handle redirect from Notion OAuth callback
    if (searchParams.get('notion') === 'connected') {
      toast.success('Notion workspace connected! Ingestion is running in the background.');
      searchParams.delete('notion');
      setSearchParams(searchParams, { replace: true });
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Poll for status updates while any workspace is syncing
  const isSyncingRef = useRef(false);
  isSyncingRef.current = workspaces.some((w) => w.sync_status === 'syncing');

  useEffect(() => {
    if (!isSyncingRef.current) return;

    const poll = () => {
      getWorkspaces().then((ws) => {
        setWorkspaces(ws);
        if (!ws.some((w) => w.sync_status === 'syncing')) {
          const failed = ws.find((w) => w.sync_status === 'error');
          if (failed) {
            toast.error(`Sync failed for ${failed.workspace_name}`);
          } else {
            toast.success('Sync complete!');
          }
        }
      }).catch(() => {});
    };

    // Poll immediately, then every 5 seconds
    const timeout = setTimeout(poll, 2000);
    const interval = setInterval(poll, 5000);

    return () => {
      clearTimeout(timeout);
      clearInterval(interval);
    };
  }, [isSyncingRef.current]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadWorkspaces = async () => {
    try {
      const ws = await getWorkspaces();
      setWorkspaces(ws);
    } catch {
      // Silently fail — user may not have any workspaces
    } finally {
      setLoadingWorkspaces(false);
    }
  };

  const handleConnectNotion = async () => {
    setConnecting(true);
    try {
      const url = await getNotionAuthUrl();
      window.location.href = url;
    } catch {
      toast.error('Failed to initiate Notion connection');
      setConnecting(false);
    }
  };

  const handleDisconnect = async (wsId: number) => {
    try {
      await disconnectWorkspace(wsId);
      setWorkspaces((prev) => prev.filter((w) => w.id !== wsId));
      toast.success('Workspace disconnected');
    } catch {
      toast.error('Failed to disconnect workspace');
    }
  };

  const handleSync = async (wsId: number) => {
    setSyncingId(wsId);
    try {
      const result = await syncWorkspace(wsId);
      if (result.status === 'already_syncing') {
        toast.info('Sync is already in progress');
      } else {
        toast.success('Sync started — this may take a few minutes');
        setWorkspaces((prev) =>
          prev.map((w) => (w.id === wsId ? { ...w, sync_status: 'syncing' } : w))
        );
      }
    } catch {
      toast.error('Failed to start sync');
    } finally {
      setSyncingId(null);
    }
  };

  const formatTimeAgo = (dateStr: string | null) => {
    if (!dateStr) return 'Never';
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const handleSaveName = async () => {
    const trimmed = name.trim();
    if (!trimmed || trimmed === user?.name) return;
    setSaving(true);
    try {
      const updated = await updateProfile({ name: trimmed });
      updateUser({ name: updated.name });
      toast.success('Name updated');
    } catch {
      toast.error('Failed to update name');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    try {
      await deleteAccount();
      await logout();
      navigate('/login');
    } catch {
      toast.error('Failed to delete account');
    }
  };

  const themeOptions: { value: 'light' | 'dark' | 'system'; label: string; icon: typeof Sun }[] = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'dark', label: 'Dark', icon: Moon },
    { value: 'system', label: 'System', icon: Monitor },
  ];

  return (
    <div className="flex-1 overflow-y-auto bg-white dark:bg-slate-900">
      <div className="mx-auto max-w-2xl px-6 py-6 space-y-4">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Settings</h1>

        {/* Profile */}
        <Card className="p-4 border-slate-200 dark:border-slate-700 dark:bg-slate-800/50">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3">Profile</h2>
          <div className="flex items-start gap-3">
            {user?.picture ? (
              <img
                src={user.picture}
                alt={user.name}
                className="h-10 w-10 rounded-full object-cover"
              />
            ) : (
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900/50 text-sm font-medium text-purple-700 dark:text-purple-300">
                {user?.name?.charAt(0).toUpperCase() ?? 'U'}
              </div>
            )}
            <div className="flex-1 space-y-2">
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1 block">
                  Display name
                </label>
                <div className="flex gap-2">
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="dark:bg-slate-800 dark:border-slate-600 dark:text-slate-100"
                  />
                  <Button
                    onClick={handleSaveName}
                    disabled={saving || !name.trim() || name.trim() === user?.name}
                    className="bg-purple-600 hover:bg-purple-700 text-white"
                  >
                    {saving ? 'Saving...' : 'Save'}
                  </Button>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div>
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-0.5 block">
                    Email
                  </label>
                  <p className="text-sm text-slate-500 dark:text-slate-400">{user?.email}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-0.5 block">
                    Role
                  </label>
                  <Badge variant={user?.role === 'admin' ? 'default' : 'secondary'}>
                    {user?.role}
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Theme */}
        <Card className="p-4 border-slate-200 dark:border-slate-700 dark:bg-slate-800/50">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3">Theme</h2>
          <div className="flex gap-2">
            {themeOptions.map(({ value, label, icon: Icon }) => (
              <Button
                key={value}
                variant={theme === value ? 'default' : 'outline'}
                onClick={() => setTheme(value)}
                className={
                  theme === value
                    ? 'bg-purple-600 hover:bg-purple-700 text-white'
                    : 'dark:border-slate-600 dark:text-slate-300'
                }
              >
                <Icon className="h-4 w-4 mr-2" />
                {label}
              </Button>
            ))}
          </div>
        </Card>

        {/* Connected Accounts */}
        <Card className="p-4 border-slate-200 dark:border-slate-700 dark:bg-slate-800/50">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3">
            Connected Accounts
          </h2>
          <div className="space-y-3">
            {loadingWorkspaces ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-5 w-5 animate-spin text-slate-400" />
              </div>
            ) : (
              <>
                {workspaces.map((ws) => (
                  <div
                    key={ws.id}
                    className="flex items-center justify-between rounded-lg border border-slate-200 dark:border-slate-600 p-3"
                  >
                    <div className="flex items-center gap-3">
                      <Link2 className="h-5 w-5 text-purple-500" />
                      <div>
                        <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                          {ws.workspace_name}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          Connected {formatTimeAgo(ws.connected_at)}
                          {ws.last_synced_at && ` · Last synced ${formatTimeAgo(ws.last_synced_at)}`}
                          {ws.sync_status === 'syncing' && (
                            <span className="ml-1 text-purple-500">· Syncing...</span>
                          )}
                          {ws.sync_status === 'error' && (
                            <span className="ml-1 text-red-500">· Sync failed</span>
                          )}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSync(ws.id)}
                        disabled={syncingId === ws.id || ws.sync_status === 'syncing'}
                        className="dark:border-slate-600 dark:text-slate-300"
                      >
                        <RefreshCw className={`h-3.5 w-3.5 mr-1 ${syncingId === ws.id || ws.sync_status === 'syncing' ? 'animate-spin' : ''}`} />
                        Sync
                      </Button>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-red-500 hover:text-red-600 dark:border-slate-600"
                          >
                            <Unplug className="h-3.5 w-3.5 mr-1" />
                            Disconnect
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Disconnect {ws.workspace_name}?</AlertDialogTitle>
                            <AlertDialogDescription>
                              This will remove your connection to this Notion workspace.
                              If no other users are connected, the workspace data will also be removed.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={() => handleDisconnect(ws.id)}
                              className="bg-red-600 hover:bg-red-700 text-white"
                            >
                              Disconnect
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </div>
                ))}
                <Button
                  variant="outline"
                  onClick={handleConnectNotion}
                  disabled={connecting}
                  className="w-full dark:border-slate-600 dark:text-slate-300"
                >
                  {connecting ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4 mr-2" />
                  )}
                  {workspaces.length > 0 ? 'Connect another Notion workspace' : 'Connect Notion workspace'}
                </Button>
              </>
            )}
          </div>
        </Card>

        {/* Danger Zone */}
        <Card className="p-4 border-red-300 dark:border-red-800">
          <h2 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-1">Danger Zone</h2>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
            Permanently delete your account and all associated data. This action cannot be undone.
          </p>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive">Delete Account</Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete your account?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete your account and all associated data. This action
                  cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDeleteAccount}
                  className="bg-red-600 hover:bg-red-700 text-white"
                >
                  Delete Account
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </Card>
      </div>
    </div>
  );
}
