import {
  detectUserPreferences,
  userPreferencesToThemeConfig,
  UserPreferenceWatcher,
  getUserPreferenceWatcher,
  prefersDarkMode,
  prefersHighContrast,
  prefersReducedMotion,
  getRecommendedThemeConfig,
  calculateAccessibilityScore,
  getPolishBusinessAccessibilityRecommendations,
  MEDIA_QUERIES,
} from '../userPreferences';
import { ThemeConfig } from '../../providers/ThemeProvider';

// Mock matchMedia
const mockMatchMedia = (matches: boolean) => ({
  matches,
  media: '',
  onchange: null,
  addListener: jest.fn(),
  removeListener: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn(),
});

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(() => mockMatchMedia(false)),
});

describe('detectUserPreferences', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('detects dark mode preference', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === MEDIA_QUERIES.DARK_MODE) {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    const preferences = detectUserPreferences();
    expect(preferences.colorScheme).toBe('dark');
  });

  it('detects light mode preference', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === MEDIA_QUERIES.LIGHT_MODE) {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    const preferences = detectUserPreferences();
    expect(preferences.colorScheme).toBe('light');
  });

  it('detects high contrast preference', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === MEDIA_QUERIES.HIGH_CONTRAST) {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    const preferences = detectUserPreferences();
    expect(preferences.contrast).toBe('high');
  });

  it('detects reduced motion preference', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === MEDIA_QUERIES.REDUCED_MOTION) {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    const preferences = detectUserPreferences();
    expect(preferences.reducedMotion).toBe(true);
  });

  it('detects support for media queries', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      const mediaQuery = mockMatchMedia(false);
      mediaQuery.media = query; // Simulate supported media query
      return mediaQuery;
    });

    const preferences = detectUserPreferences();
    expect(preferences.supportsColorScheme).toBe(true);
    expect(preferences.supportsContrast).toBe(true);
    expect(preferences.supportsReducedMotion).toBe(true);
  });

  it('handles matchMedia errors gracefully', () => {
    window.matchMedia = jest.fn().mockImplementation(() => {
      throw new Error('matchMedia error');
    });

    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

    const preferences = detectUserPreferences();

    expect(preferences).toEqual({
      colorScheme: 'no-preference',
      contrast: 'normal',
      reducedMotion: false,
      supportsColorScheme: false,
      supportsContrast: false,
      supportsReducedMotion: false,
    });

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Failed to detect user preferences'),
      expect.any(Error)
    );

    consoleSpy.mockRestore();
  });

  it('returns default preferences for SSR', () => {
    const originalWindow = global.window;
    // @ts-ignore
    delete global.window;

    const preferences = detectUserPreferences();

    expect(preferences).toEqual({
      colorScheme: 'no-preference',
      contrast: 'normal',
      reducedMotion: false,
      supportsColorScheme: false,
      supportsContrast: false,
      supportsReducedMotion: false,
    });

    global.window = originalWindow;
  });
});

describe('userPreferencesToThemeConfig', () => {
  it('converts dark color scheme to dark mode', () => {
    const preferences = {
      colorScheme: 'dark' as const,
      contrast: 'normal' as const,
      reducedMotion: false,
      supportsColorScheme: true,
      supportsContrast: true,
      supportsReducedMotion: true,
    };

    const config = userPreferencesToThemeConfig(preferences);
    expect(config.mode).toBe('dark');
  });

  it('converts light color scheme to light mode', () => {
    const preferences = {
      colorScheme: 'light' as const,
      contrast: 'normal' as const,
      reducedMotion: false,
      supportsColorScheme: true,
      supportsContrast: true,
      supportsReducedMotion: true,
    };

    const config = userPreferencesToThemeConfig(preferences);
    expect(config.mode).toBe('light');
  });

  it('converts no-preference to auto mode', () => {
    const preferences = {
      colorScheme: 'no-preference' as const,
      contrast: 'normal' as const,
      reducedMotion: false,
      supportsColorScheme: true,
      supportsContrast: true,
      supportsReducedMotion: true,
    };

    const config = userPreferencesToThemeConfig(preferences);
    expect(config.mode).toBe('auto');
  });

  it('preserves contrast and reduced motion preferences', () => {
    const preferences = {
      colorScheme: 'dark' as const,
      contrast: 'high' as const,
      reducedMotion: true,
      supportsColorScheme: true,
      supportsContrast: true,
      supportsReducedMotion: true,
    };

    const config = userPreferencesToThemeConfig(preferences);
    expect(config.contrast).toBe('high');
    expect(config.reducedMotion).toBe(true);
  });
});

describe('UserPreferenceWatcher', () => {
  let watcher: UserPreferenceWatcher;

  beforeEach(() => {
    jest.clearAllMocks();
    watcher = new UserPreferenceWatcher();
  });

  afterEach(() => {
    watcher.destroy();
  });

  it('creates media query listeners', () => {
    expect(window.matchMedia).toHaveBeenCalledWith(MEDIA_QUERIES.DARK_MODE);
    expect(window.matchMedia).toHaveBeenCalledWith(MEDIA_QUERIES.HIGH_CONTRAST);
    expect(window.matchMedia).toHaveBeenCalledWith(MEDIA_QUERIES.REDUCED_MOTION);
  });

  it('allows subscribing to preference changes', () => {
    const callback = jest.fn();
    watcher.subscribe('test', callback);

    // Simulate media query change
    const mockQuery = mockMatchMedia(true);
    mockQuery.addEventListener = jest.fn((event, handler) => {
      if (event === 'change') {
        handler();
      }
    });

    expect(callback).not.toHaveBeenCalled();
  });

  it('allows unsubscribing from preference changes', () => {
    const callback = jest.fn();
    watcher.subscribe('test', callback);
    watcher.unsubscribe('test');

    // Callback should not be called after unsubscribing
    expect(callback).not.toHaveBeenCalled();
  });

  it('returns current preferences', () => {
    const preferences = watcher.getCurrentPreferences();
    expect(preferences).toHaveProperty('colorScheme');
    expect(preferences).toHaveProperty('contrast');
    expect(preferences).toHaveProperty('reducedMotion');
  });

  it('handles setup errors gracefully', () => {
    window.matchMedia = jest.fn().mockImplementation(() => {
      throw new Error('matchMedia error');
    });

    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

    const errorWatcher = new UserPreferenceWatcher();

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Failed to setup user preference listeners'),
      expect.any(Error)
    );

    consoleSpy.mockRestore();
    errorWatcher.destroy();
  });
});

describe('getUserPreferenceWatcher', () => {
  it('returns singleton instance', () => {
    const watcher1 = getUserPreferenceWatcher();
    const watcher2 = getUserPreferenceWatcher();
    expect(watcher1).toBe(watcher2);
  });
});

describe('preference utility functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('prefersDarkMode returns correct value', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === MEDIA_QUERIES.DARK_MODE) {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    expect(prefersDarkMode()).toBe(true);
  });

  it('prefersHighContrast returns correct value', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === MEDIA_QUERIES.HIGH_CONTRAST) {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    expect(prefersHighContrast()).toBe(true);
  });

  it('prefersReducedMotion returns correct value', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === MEDIA_QUERIES.REDUCED_MOTION) {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    expect(prefersReducedMotion()).toBe(true);
  });

  it('handles errors gracefully', () => {
    window.matchMedia = jest.fn().mockImplementation(() => {
      throw new Error('matchMedia error');
    });

    expect(prefersDarkMode()).toBe(false);
    expect(prefersHighContrast()).toBe(false);
    expect(prefersReducedMotion()).toBe(false);
  });

  it('returns false for SSR', () => {
    const originalWindow = global.window;
    // @ts-ignore
    delete global.window;

    expect(prefersDarkMode()).toBe(false);
    expect(prefersHighContrast()).toBe(false);
    expect(prefersReducedMotion()).toBe(false);

    global.window = originalWindow;
  });
});

describe('getRecommendedThemeConfig', () => {
  it('returns recommended config based on user preferences', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === MEDIA_QUERIES.DARK_MODE) {
        return mockMatchMedia(true);
      }
      if (query === MEDIA_QUERIES.HIGH_CONTRAST) {
        return mockMatchMedia(true);
      }
      if (query === MEDIA_QUERIES.REDUCED_MOTION) {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    const config = getRecommendedThemeConfig();
    expect(config.mode).toBe('dark');
    expect(config.contrast).toBe('high');
    expect(config.reducedMotion).toBe(true);
  });
});

describe('calculateAccessibilityScore', () => {
  const mockPreferences = {
    colorScheme: 'dark' as const,
    contrast: 'high' as const,
    reducedMotion: true,
    supportsColorScheme: true,
    supportsContrast: true,
    supportsReducedMotion: true,
  };

  it('gives perfect score for matching preferences', () => {
    const config: ThemeConfig = {
      mode: 'dark',
      contrast: 'high',
      reducedMotion: true,
    };

    const score = calculateAccessibilityScore(config, mockPreferences);
    expect(score).toBe(95); // 25 + 35 + 35 = 95 (not 100 because mode is not auto)
  });

  it('gives high score for auto mode', () => {
    const config: ThemeConfig = {
      mode: 'auto',
      contrast: 'high',
      reducedMotion: true,
    };

    const score = calculateAccessibilityScore(config, mockPreferences);
    expect(score).toBe(100); // 30 + 35 + 35 = 100
  });

  it('gives lower score for mismatched preferences', () => {
    const config: ThemeConfig = {
      mode: 'light',
      contrast: 'normal',
      reducedMotion: false,
    };

    const score = calculateAccessibilityScore(config, mockPreferences);
    expect(score).toBeLessThan(50);
  });

  it('handles no-preference color scheme', () => {
    const preferences = {
      ...mockPreferences,
      colorScheme: 'no-preference' as const,
    };

    const config: ThemeConfig = {
      mode: 'light',
      contrast: 'high',
      reducedMotion: true,
    };

    const score = calculateAccessibilityScore(config, preferences);
    expect(score).toBe(90); // 20 + 35 + 35 = 90
  });
});

describe('getPolishBusinessAccessibilityRecommendations', () => {
  it('recommends dark mode when user prefers it', () => {
    const config: ThemeConfig = {
      mode: 'light',
      contrast: 'normal',
      reducedMotion: false,
    };

    const preferences = {
      colorScheme: 'dark' as const,
      contrast: 'normal' as const,
      reducedMotion: false,
      supportsColorScheme: true,
      supportsContrast: true,
      supportsReducedMotion: true,
    };

    const recommendations = getPolishBusinessAccessibilityRecommendations(config, preferences);
    expect(recommendations.some(rec => rec.includes('ciemnego motywu'))).toBe(true);
  });

  it('recommends high contrast when user prefers it', () => {
    const config: ThemeConfig = {
      mode: 'light',
      contrast: 'normal',
      reducedMotion: false,
    };

    const preferences = {
      colorScheme: 'light' as const,
      contrast: 'high' as const,
      reducedMotion: false,
      supportsColorScheme: true,
      supportsContrast: true,
      supportsReducedMotion: true,
    };

    const recommendations = getPolishBusinessAccessibilityRecommendations(config, preferences);
    expect(recommendations.some(rec => rec.includes('wysoki kontrast'))).toBe(true);
  });

  it('recommends reduced motion when user prefers it', () => {
    const config: ThemeConfig = {
      mode: 'light',
      contrast: 'normal',
      reducedMotion: false,
    };

    const preferences = {
      colorScheme: 'light' as const,
      contrast: 'normal' as const,
      reducedMotion: true,
      supportsColorScheme: true,
      supportsContrast: true,
      supportsReducedMotion: true,
    };

    const recommendations = getPolishBusinessAccessibilityRecommendations(config, preferences);
    expect(recommendations.some(rec => rec.includes('animacje'))).toBe(true);
  });

  it('provides Polish business specific recommendations', () => {
    const config: ThemeConfig = {
      mode: 'light',
      contrast: 'normal',
      reducedMotion: false,
    };

    const preferences = {
      colorScheme: 'no-preference' as const,
      contrast: 'normal' as const,
      reducedMotion: false,
      supportsColorScheme: false,
      supportsContrast: false,
      supportsReducedMotion: true,
    };

    const recommendations = getPolishBusinessAccessibilityRecommendations(config, preferences);
    expect(recommendations.length).toBeGreaterThan(0);
    expect(recommendations.some(rec => rec.includes('księgowych') || rec.includes('fakturami'))).toBe(true);
  });

  it('returns empty array when no recommendations needed', () => {
    const config: ThemeConfig = {
      mode: 'auto',
      contrast: 'high',
      reducedMotion: true,
    };

    const preferences = {
      colorScheme: 'no-preference' as const,
      contrast: 'high' as const,
      reducedMotion: true,
      supportsColorScheme: true,
      supportsContrast: true,
      supportsReducedMotion: true,
    };

    const recommendations = getPolishBusinessAccessibilityRecommendations(config, preferences);
    expect(recommendations).toHaveLength(0);
  });
});