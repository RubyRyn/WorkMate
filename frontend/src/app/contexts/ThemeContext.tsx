import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

type ThemePreference = "light" | "dark" | "system";
type ResolvedTheme = "light" | "dark";

interface ThemeContextType {
  theme: ThemePreference;
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: ThemePreference) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | null>(null);

function getSystemTheme(): ResolvedTheme {
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function resolve(pref: ThemePreference): ResolvedTheme {
  return pref === "system" ? getSystemTheme() : pref;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemePreference>(() => {
    const stored = localStorage.getItem("workmate_theme");
    if (stored === "dark" || stored === "light" || stored === "system")
      return stored;
    return "system";
  });

  const [resolvedTheme, setResolved] = useState<ResolvedTheme>(() =>
    resolve(theme),
  );

  // Apply class + persist
  useEffect(() => {
    const resolved = resolve(theme);
    setResolved(resolved);
    document.documentElement.classList.toggle("dark", resolved === "dark");
    localStorage.setItem("workmate_theme", theme);
  }, [theme]);

  // Listen for OS changes when preference is "system"
  useEffect(() => {
    if (theme !== "system") return;
    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      const resolved = getSystemTheme();
      setResolved(resolved);
      document.documentElement.classList.toggle("dark", resolved === "dark");
    };
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, [theme]);

  const setTheme = (t: ThemePreference) => setThemeState(t);
  const toggleTheme = () =>
    setThemeState((t) => {
      const current = t === "system" ? getSystemTheme() : t;
      return current === "light" ? "dark" : "light";
    });

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
