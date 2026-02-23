import { useAuth } from "../app/contexts/AuthContext";

export function useIsAdmin(): boolean {
  const { user } = useAuth();
  return user?.role === "admin";
}
