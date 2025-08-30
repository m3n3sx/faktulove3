// User Preference Detection Utilities
import { ThemeConfig, ThemeMode, ContrastMode } from '../providers/ThemeProvider';

// Media query strings
export const MEDIA_QUERIES = {
  DARK_MODE: '(prefers-color-scheme: dark)',
  LIGHT_MODE: '(prefers-color-scheme: light)',
  HIGH_CONTRAST: '(prefers-contrast: high)',
  REDUCED_MOTION: '(prefers-reduced-motion: reduce)',
  NO_PREFERENCE: '(prefers-color-scheme: no-preference)',
} as const;

// User preference detection
export interface UserPreferences {
  colorScheme: 'light' | 'dark' | 'no-preference';
  contrast: 'normal' | 'high';
  reducedMotion: boolean;
  supportsColorScheme: boolean;
  supportsContrast: boolean;
  supportsReducedMotion: boolean;
}

// Detect user preferences from system
export const detectUserPreferences = (): UserPreferences => {
  if (typeof window === 'undefined') {
    return {
      colorScheme: 'no-preference',
      contrast: 'normal',
      reducedMotion: false,
      supportsColorScheme: false,
      supportsContrast: false,
      supportsReducedMotion: false,
    };
  }

  try {
    const darkModeQuery = window.matchMedia(MEDIA_QUERIES.DARK_MODE);
    const lightModeQuery = window.matchMedia(MEDIA_QUERIES.LIGHT_MODE);
    const highContrastQuery = window.matchMedia(MEDIA_QUERIES.HIGH_CONTRAST);
    const reducedMotionQuery = window.matchMedia(MEDIA_QUERIES.REDUCED_MOTION);

    let colorScheme: 'light' | 'dark' | 'no-preference' = 'no-preference';
    
    if (darkModeQuery.matches) {
      colorScheme = 'dark';
    } else if (lightModeQuery.matches) {
      colorScheme = 'light';
    }

    return {
      colorScheme,
      contrast: highContrastQuery.matches ? 'high' : 'normal',
      reducedMotion: reducedMotionQuery.matches,
      supportsColorScheme: darkModeQuery.media !== 'not all',
      supportsContrast: highContrastQuery.media !== 'not all',
      supportsReducedMotion: reducedMotionQuery.media !== 'not all',
    };
  } catch (error) {
    console.warn('Failed to detect user preferences:', error);
    return {
      colorScheme: 'no-preference',
      contrast: 'normal',
      reducedMotion: false,
      supportsColorScheme: false,
      supportsContrast: false,
      supportsReducedMotion: false,
    };
  }
};

// Convert user preferences to theme config
export const userPreferencesToThemeConfig = (preferences: UserPreferences): Partial<ThemeConfig> => {
  const config: Partial<ThemeConfig> = {};

  // Map color scheme to theme mode
  switch (preferences.colorScheme) {
    case 'dark':
      config.mode = 'dark';
      break;
    case 'light':
      config.mode = 'light';
      break;
    case 'no-preference':
      config.mode = 'auto';
      break;
  }

  // Map contrast preference
  config.contrast = preferences.contrast;

  // Map reduced motion preference
  config.reducedMotion = preferences.reducedMotion;

  return config;
};

// Create media query listeners
export class UserPreferenceWatcher {
  private listeners: Map<string, MediaQueryList> = new Map();
  private callbacks: Map<string, (preferences: UserPreferences) => void> = new Map();

  constructor() {
    if (typeof window !== 'undefined') {
      this.setupListeners();
    }
  }

  private setupListeners(): void {
    try {
      // Create media query lists
      const darkModeQuery = window.matchMedia(MEDIA_QUERIES.DARK_MODE);
      const highContrastQuery = window.matchMedia(MEDIA_QUERIES.HIGH_CONTRAST);
      const reducedMotionQuery = window.matchMedia(MEDIA_QUERIES.REDUCED_MOTION);

      this.listeners.set('darkMode', darkModeQuery);
      this.listeners.set('highContrast', highContrastQuery);
      this.listeners.set('reducedMotion', reducedMotionQuery);

      // Add change listeners
      const handleChange = () => {
        const preferences = detectUserPreferences();
        this.callbacks.forEach(callback => callback(preferences));
      };

      darkModeQuery.addEventListener('change', handleChange);
      highContrastQuery.addEventListener('change', handleChange);
      reducedMotionQuery.addEventListener('change', handleChange);
    } catch (error) {
      console.warn('Failed to setup user preference listeners:', error);
    }
  }

  // Subscribe to preference changes
  public subscribe(id: string, callback: (preferences: UserPreferences) => void): void {
    this.callbacks.set(id, callback);
  }

  // Unsubscribe from preference changes
  public unsubscribe(id: string): void {
    this.callbacks.delete(id);
  }

  // Get current preferences
  public getCurrentPreferences(): UserPreferences {
    return detectUserPreferences();
  }

  // Cleanup listeners
  public destroy(): void {
    this.listeners.forEach(query => {
      try {
        query.removeEventListener('change', () => {});
      } catch (error) {
        console.warn('Failed to remove media query listener:', error);
      }
    });
    this.listeners.clear();
    this.callbacks.clear();
  }
}

// Singleton instance
let preferenceWatcher: UserPreferenceWatcher | null = null;

export const getUserPreferenceWatcher = (): UserPreferenceWatcher => {
  if (!preferenceWatcher) {
    preferenceWatcher = new UserPreferenceWatcher();
  }
  return preferenceWatcher;
};

// React hook for user preferences
export const useUserPreferences = () => {
  if (typeof window === 'undefined') {
    return {
      colorScheme: 'no-preference' as const,
      contrast: 'normal' as const,
      reducedMotion: false,
      supportsColorScheme: false,
      supportsContrast: false,
      supportsReducedMotion: false,
    };
  }

  const [preferences, setPreferences] = React.useState<UserPreferences>(detectUserPreferences);

  React.useEffect(() => {
    const watcher = getUserPreferenceWatcher();
    const id = `useUserPreferences-${Date.now()}`;

    watcher.subscribe(id, setPreferences);

    return () => {
      watcher.unsubscribe(id);
    };
  }, []);

  return preferences;
};

// Utility functions for specific preferences
export const prefersDarkMode = (): boolean => {
  if (typeof window === 'undefined') return false;
  
  try {
    return window.matchMedia(MEDIA_QUERIES.DARK_MODE).matches;
  } catch {
    return false;
  }
};

export const prefersHighContrast = (): boolean => {
  if (typeof window === 'undefined') return false;
  
  try {
    return window.matchMedia(MEDIA_QUERIES.HIGH_CONTRAST).matches;
  } catch {
    return false;
  }
};

export const prefersReducedMotion = (): boolean => {
  if (typeof window === 'undefined') return false;
  
  try {
    return window.matchMedia(MEDIA_QUERIES.REDUCED_MOTION).matches;
  } catch {
    return false;
  }
};

// Theme recommendation based on user preferences
export const getRecommendedThemeConfig = (): ThemeConfig => {
  const preferences = detectUserPreferences();
  const baseConfig = userPreferencesToThemeConfig(preferences);
  
  return {
    mode: baseConfig.mode || 'auto',
    contrast: baseConfig.contrast || 'normal',
    reducedMotion: baseConfig.reducedMotion || false,
  };
};

// Accessibility score calculation
export const calculateAccessibilityScore = (config: ThemeConfig, preferences: UserPreferences): number => {
  let score = 0;
  const maxScore = 100;

  // Color scheme alignment (30 points)
  if (config.mode === 'auto') {
    score += 30; // Auto mode respects user preference
  } else if (
    (config.mode === 'dark' && preferences.colorScheme === 'dark') ||
    (config.mode === 'light' && preferences.colorScheme === 'light')
  ) {
    score += 25; // Manual mode matches preference
  } else if (preferences.colorScheme === 'no-preference') {
    score += 20; // No preference, any mode is acceptable
  }

  // Contrast alignment (35 points)
  if (config.contrast === preferences.contrast) {
    score += 35; // Perfect contrast match
  } else if (preferences.contrast === 'normal' && config.contrast === 'high') {
    score += 25; // High contrast is better than normal for accessibility
  }

  // Reduced motion alignment (35 points)
  if (config.reducedMotion === preferences.reducedMotion) {
    score += 35; // Perfect motion preference match
  } else if (config.reducedMotion && !preferences.reducedMotion) {
    score += 25; // Reduced motion is safer when not required
  }

  return Math.min(score, maxScore);
};

// Polish business accessibility recommendations
export const getPolishBusinessAccessibilityRecommendations = (
  config: ThemeConfig,
  preferences: UserPreferences
): string[] => {
  const recommendations: string[] = [];

  // Color scheme recommendations
  if (preferences.colorScheme === 'dark' && config.mode !== 'dark' && config.mode !== 'auto') {
    recommendations.push('Rozważ włączenie ciemnego motywu dla lepszego komfortu oczu');
  }

  // Contrast recommendations
  if (preferences.contrast === 'high' && config.contrast !== 'high') {
    recommendations.push('Włącz wysoki kontrast dla lepszej czytelności');
  }

  // Motion recommendations
  if (preferences.reducedMotion && !config.reducedMotion) {
    recommendations.push('Wyłącz animacje dla lepszej dostępności');
  }

  // Polish business specific recommendations
  if (config.contrast === 'normal' && !preferences.supportsContrast) {
    recommendations.push('Rozważ włączenie wysokiego kontrastu dla lepszej czytelności dokumentów księgowych');
  }

  if (config.mode === 'light' && preferences.colorScheme === 'no-preference') {
    recommendations.push('Ciemny motyw może być bardziej komfortowy podczas długiej pracy z fakturami');
  }

  return recommendations;
};

// Export React import for the hook
import React from 'react';

export default {
  detectUserPreferences,
  userPreferencesToThemeConfig,
  UserPreferenceWatcher,
  getUserPreferenceWatcher,
  useUserPreferences,
  prefersDarkMode,
  prefersHighContrast,
  prefersReducedMotion,
  getRecommendedThemeConfig,
  calculateAccessibilityScore,
  getPolishBusinessAccessibilityRecommendations,
};