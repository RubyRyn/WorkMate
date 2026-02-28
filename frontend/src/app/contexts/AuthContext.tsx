import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { toast } from "sonner";
import type { User } from "../../types/auth";
import {
  clearToken,
  fetchCurrentUser,
  getGoogleAuthUrl,
  getToken,
  logout as logoutService,
  setToken,
} from "../../services/auth";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check URL for token from OAuth redirect
    const params = new URLSearchParams(window.location.search);
    const tokenFromUrl = params.get("token");

    if (tokenFromUrl) {
      setToken(tokenFromUrl);
      // Clean token from URL
      window.history.replaceState({}, "", window.location.pathname);
    }

    // Try to fetch user if we have a token
    const token = getToken();
    if (token) {
      fetchCurrentUser()
        .then((u) => {
          setUser(u);
          if (tokenFromUrl) toast.success(`Welcome back, ${u.name}!`);
        })
        .catch(() => clearToken())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async () => {
    const url = await getGoogleAuthUrl();
    window.location.href = url;
  };

  const updateUser = (updates: Partial<User>) => {
    setUser((prev) => (prev ? { ...prev, ...updates } : prev));
  };

  const logout = async () => {
    await logoutService();
    setUser(null);
    toast.success("Signed out successfully");
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
