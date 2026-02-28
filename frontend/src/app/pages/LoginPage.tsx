import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";

export function LoginPage() {
  const { login } = useAuth();

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
      <div className="w-full max-w-sm space-y-6 text-center">
        <div>
          <h1 className="text-3xl font-bold text-purple-700 dark:text-purple-400">WorkMate</h1>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            Your AI-powered work assistant
          </p>
        </div>

        <Button
          onClick={login}
          variant="outline"
          className="w-full gap-3 border-slate-300 dark:border-slate-600 py-6 text-base dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700"
        >
          <img src="/google-icon.svg" alt="Google" className="h-5 w-5" />
          Sign in with Google
        </Button>
      </div>
    </div>
  );
}
