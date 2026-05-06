/* eslint-disable react-refresh/only-export-components */
/**
 * Tema: variables CSS en `globals.css` (`data-theme` en <html>).
 * - Preferencia `system`: sigue `prefers-color-scheme` y reacciona al cambio en tiempo real (p. ej. macOS).
 * - `light` / `dark`: fijados y guardados en localStorage (`nivo-theme-preference`).
 */
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

type Theme = 'light' | 'dark';
type ThemePreference = Theme | 'system';

type ThemeContextValue = {
  preference: ThemePreference;
  resolvedTheme: Theme;
  setTheme: (theme: ThemePreference) => void;
};

const STORAGE_KEY = 'nivo-theme-preference';
const MEDIA_QUERY = '(prefers-color-scheme: dark)';

const ThemeContext = createContext<ThemeContextValue | null>(null);

const isThemePreference = (value: string | null): value is ThemePreference =>
  value === 'light' || value === 'dark' || value === 'system';

const getStoredThemePreference = (): ThemePreference => {
  if (typeof window === 'undefined') return 'system';
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return isThemePreference(stored) ? stored : 'system';
};

const getSystemTheme = (): Theme => {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia(MEDIA_QUERY).matches ? 'dark' : 'light';
};

const applyThemeToDocument = (theme: Theme) => {
  const root = document.documentElement;
  root.dataset.theme = theme;
  root.style.colorScheme = theme;

  const themeColor = document.querySelector('meta[name="theme-color"]');
  if (themeColor) {
    themeColor.setAttribute('content', theme === 'dark' ? '#0B0E0D' : '#FFFFFF');
  }
};

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [preference, setPreferenceState] = useState<ThemePreference>(() =>
    getStoredThemePreference()
  );
  const [systemTheme, setSystemTheme] = useState<Theme>(() => getSystemTheme());

  const resolvedTheme = preference === 'system' ? systemTheme : preference;

  useEffect(() => {
    const mediaQuery = window.matchMedia(MEDIA_QUERY);
    const syncSystemTheme = (event?: MediaQueryListEvent) => {
      const nextTheme = (event?.matches ?? mediaQuery.matches) ? 'dark' : 'light';
      setSystemTheme(nextTheme);
    };

    syncSystemTheme();
    mediaQuery.addEventListener('change', syncSystemTheme);
    return () => mediaQuery.removeEventListener('change', syncSystemTheme);
  }, []);

  useEffect(() => {
    applyThemeToDocument(resolvedTheme);
  }, [resolvedTheme]);

  useEffect(() => {
    const syncStorage = (event: StorageEvent) => {
      if (event.key === STORAGE_KEY) {
        setPreferenceState(getStoredThemePreference());
      }
    };

    window.addEventListener('storage', syncStorage);
    return () => window.removeEventListener('storage', syncStorage);
  }, []);

  const setTheme = (next: ThemePreference) => {
    setPreferenceState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  };

  const value = useMemo(
    () => ({
      preference,
      resolvedTheme,
      setTheme,
    }),
    [preference, resolvedTheme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }

  return context;
};
