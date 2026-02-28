import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sun, Moon, Monitor, Link2 } from 'lucide-react';
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
import { useTheme } from '../contexts/ThemeContext';
import { updateProfile, deleteAccount } from '../../services/auth';

export function SettingsPage() {
  const { user, logout, updateUser } = useAuth();
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();

  const [name, setName] = useState(user?.name ?? '');
  const [saving, setSaving] = useState(false);

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
          <div className="flex items-center justify-between rounded-lg border border-slate-200 dark:border-slate-600 p-3">
            <div className="flex items-center gap-3">
              <Link2 className="h-5 w-5 text-slate-500 dark:text-slate-400" />
              <div>
                <p className="text-sm font-medium text-slate-900 dark:text-slate-100">Notion</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">Coming soon</p>
              </div>
            </div>
            <Button variant="outline" disabled className="dark:border-slate-600 dark:text-slate-400">
              Connect
            </Button>
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
