import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";

export function LoginPage() {
  const { login } = useAuth();

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="w-full max-w-sm space-y-6 text-center">
        <div>
          <h1 className="text-3xl font-bold text-purple-700">WorkMate</h1>
          <p className="mt-2 text-slate-600">
            Your AI-powered work assistant
          </p>
        </div>

        <Button
          onClick={login}
          variant="outline"
          className="w-full gap-3 border-slate-300 py-6 text-base"
        >
          <img src="/google-icon.svg" alt="Google" className="h-5 w-5" />
          Sign in with Google
        </Button>
      </div>
    </div>
  );
}
