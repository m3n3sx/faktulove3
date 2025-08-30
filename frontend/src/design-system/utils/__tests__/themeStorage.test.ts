import {
  ThemeStorageManager,
  themeStorage,
  saveThemeConfig,
  loadThemeConfig,
  saveUserPreferences,
  loadUserPreferences,
  clearThemeData,
  exportThemeData,
  importThemeData,
  getInitialThemeConfig,
  getSystemPreferences,
  validateThemeConfig,
  sanitizeThemeConfig,
  applyThemePreset,
  THEME_STORAGE_KEYS,
  DEFAULT_THEME_CONFIG,
  POLISH_BUSINESS_THEME_PRESETS,
} from '../themeStorage';
import { ThemeConfig } from '../../providers/ThemeProvider';

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

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

describe('ThemeStorageManager', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  describe('singleton pattern', () => {
    it('returns the same instance', () => {
      const instance1 = ThemeStorageManager.getInstance();
      const instance2 = ThemeStorageManager.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('saveThemeConfig', () => {
    it('saves theme config to localStorage', () => {
      const config: ThemeConfig = {
        mode: 'dark',
        contrast: 'high',
        reducedMotion: true,
      };

      themeStorage.saveThemeConfig(config);

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        THEME_STORAGE_KEYS.MODE,
        'dark'
      );
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        THEME_STORAGE_KEYS.CONTRAST,
        'high'
      );
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        THEME_STORAGE_KEYS.REDUCED_MOTION,
        'true'
      );
    });

    it('handles localStorage errors gracefully', () => {
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('localStorage error');
      });

      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

      const config: ThemeConfig = {
        mode: 'dark',
        contrast: 'normal',
        reducedMotion: false,
      };

      expect(() => themeStorage.saveThemeConfig(config)).not.toThrow();
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Failed to save theme config'),
        expect.any(Error)
      );

      consoleSpy.mockRestore();
    });
  });

  describe('loadThemeConfig', () => {
    it('loads theme config from localStorage', () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        switch (key) {
          case THEME_STORAGE_KEYS.MODE:
            return 'dark';
          case THEME_STORAGE_KEYS.CONTRAST:
            return 'high';
          case THEME_STORAGE_KEYS.REDUCED_MOTION:
            return 'true';
          default:
            return null;
        }
      });

      const config = themeStorage.loadThemeConfig();

      expect(config).toEqual({
        mode: 'dark',
        contrast: 'high',
        reducedMotion: true,
      });
    });

    it('returns default config when localStorage is empty', () => {
      const config = themeStorage.loadThemeConfig();
      expect(config).toEqual(DEFAULT_THEME_CONFIG);
    });

    it('handles localStorage errors gracefully', () => {
      mockLocalStorage.getItem.mockImplementation(() => {
        throw new Error('localStorage error');
      });

      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

      const config = themeStorage.loadThemeConfig();

      expect(config).toEqual(DEFAULT_THEME_CONFIG);
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Failed to load theme config'),
        expect.any(Error)
      );

      consoleSpy.mockRestore();
    });
  });

  describe('saveUserPreferences', () => {
    it('saves extended user preferences', () => {
      const preferences = {
        mode: 'dark' as const,
        contrast: 'high' as const,
        reducedMotion: true,
        customColors: { '--color-primary': '#ff0000' },
        fontSize: 'large' as const,
        compactMode: true,
      };

      themeStorage.saveUserPreferences(preferences);

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        THEME_STORAGE_KEYS.USER_PREFERENCES,
        expect.stringContaining('"mode":"dark"')
      );
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        THEME_STORAGE_KEYS.USER_PREFERENCES,
        expect.stringContaining('"customColors"')
      );
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        THEME_STORAGE_KEYS.USER_PREFERENCES,
        expect.stringContaining('"lastUpdated"')
      );
    });
  });

  describe('loadUserPreferences', () => {
    it('loads extended user preferences', () => {
      const storedPreferences = {
        mode: 'dark',
        contrast: 'high',
        reducedMotion: true,
        customColors: { '--color-primary': '#ff0000' },
        fontSize: 'large',
        lastUpdated: Date.now(),
      };

      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === THEME_STORAGE_KEYS.USER_PREFERENCES) {
          return JSON.stringify(storedPreferences);
        }
        return null;
      });

      const preferences = themeStorage.loadUserPreferences();

      expect(preferences).toEqual(expect.objectContaining(storedPreferences));
    });

    it('falls back to basic config when no extended preferences exist', () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        switch (key) {
          case THEME_STORAGE_KEYS.USER_PREFERENCES:
            return null;
          case THEME_STORAGE_KEYS.MODE:
            return 'dark';
          case THEME_STORAGE_KEYS.CONTRAST:
            return 'high';
          case THEME_STORAGE_KEYS.REDUCED_MOTION:
            return 'true';
          default:
            return null;
        }
      });

      const preferences = themeStorage.loadUserPreferences();

      expect(preferences).toEqual({
        mode: 'dark',
        contrast: 'high',
        reducedMotion: true,
      });
    });
  });

  describe('clearThemeData', () => {
    it('removes all theme-related localStorage keys', () => {
      themeStorage.clearThemeData();

      Object.values(THEME_STORAGE_KEYS).forEach(key => {
        expect(mockLocalStorage.removeItem).toHaveBeenCalledWith(key);
      });
    });
  });

  describe('exportThemeData', () => {
    it('exports theme data as JSON string', () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        switch (key) {
          case THEME_STORAGE_KEYS.MODE:
            return 'dark';
          case THEME_STORAGE_KEYS.USER_PREFERENCES:
            return JSON.stringify({ mode: 'dark', customColors: {} });
          case THEME_STORAGE_KEYS.CUSTOM_PROPERTIES:
            return JSON.stringify({ '--color-primary': '#ff0000' });
          default:
            return null;
        }
      });

      const exportedData = themeStorage.exportThemeData();
      const parsedData = JSON.parse(exportedData);

      expect(parsedData).toHaveProperty('config');
      expect(parsedData).toHaveProperty('preferences');
      expect(parsedData).toHaveProperty('customProperties');
      expect(parsedData).toHaveProperty('exportedAt');
    });
  });

  describe('importThemeData', () => {
    it('imports theme data from JSON string', () => {
      const themeData = {
        config: { mode: 'dark', contrast: 'high', reducedMotion: true },
        preferences: { mode: 'dark', customColors: {} },
        customProperties: { '--color-primary': '#ff0000' },
      };

      const result = themeStorage.importThemeData(JSON.stringify(themeData));

      expect(result).toBe(true);
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        THEME_STORAGE_KEYS.MODE,
        'dark'
      );
    });

    it('returns false for invalid JSON', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

      const result = themeStorage.importThemeData('invalid json');

      expect(result).toBe(false);
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Failed to import theme data'),
        expect.any(Error)
      );

      consoleSpy.mockRestore();
    });
  });

  describe('migrateFromOldStorage', () => {
    it('migrates data from old storage keys', () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        switch (key) {
          case 'dark-mode':
            return 'true';
          case 'high-contrast':
            return 'true';
          case 'reduced-motion':
            return 'true';
          default:
            return null;
        }
      });

      const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});

      themeStorage.migrateFromOldStorage();

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        THEME_STORAGE_KEYS.MODE,
        'dark'
      );
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('dark-mode');
      expect(consoleSpy).toHaveBeenCalledWith(
        'Theme data migrated from old storage format'
      );

      consoleSpy.mockRestore();
    });
  });
});

describe('convenience functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  it('saveThemeConfig calls storage manager', () => {
    const config: ThemeConfig = {
      mode: 'dark',
      contrast: 'normal',
      reducedMotion: false,
    };

    saveThemeConfig(config);

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      THEME_STORAGE_KEYS.MODE,
      'dark'
    );
  });

  it('loadThemeConfig calls storage manager', () => {
    const config = loadThemeConfig();
    expect(config).toEqual(DEFAULT_THEME_CONFIG);
  });
});

describe('system preferences detection', () => {
  it('detects dark mode preference', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === '(prefers-color-scheme: dark)') {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    const preferences = getSystemPreferences();
    expect(preferences.mode).toBe('dark');
  });

  it('detects high contrast preference', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === '(prefers-contrast: high)') {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    const preferences = getSystemPreferences();
    expect(preferences.contrast).toBe('high');
  });

  it('detects reduced motion preference', () => {
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === '(prefers-reduced-motion: reduce)') {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    const preferences = getSystemPreferences();
    expect(preferences.reducedMotion).toBe(true);
  });

  it('handles matchMedia errors gracefully', () => {
    window.matchMedia = jest.fn().mockImplementation(() => {
      throw new Error('matchMedia error');
    });

    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

    const preferences = getSystemPreferences();

    expect(preferences).toEqual({});
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Failed to detect system preferences'),
      expect.any(Error)
    );

    consoleSpy.mockRestore();
  });
});

describe('theme validation', () => {
  it('validates correct theme config', () => {
    const config: ThemeConfig = {
      mode: 'dark',
      contrast: 'high',
      reducedMotion: true,
    };

    expect(validateThemeConfig(config)).toBe(true);
  });

  it('rejects invalid theme config', () => {
    const invalidConfigs = [
      null,
      undefined,
      'string',
      { mode: 'invalid' },
      { contrast: 'invalid' },
      { reducedMotion: 'invalid' },
      { mode: 'dark' }, // missing properties
    ];

    invalidConfigs.forEach(config => {
      expect(validateThemeConfig(config)).toBe(false);
    });
  });

  it('sanitizes invalid theme config', () => {
    const invalidConfig = {
      mode: 'invalid',
      contrast: 'invalid',
      reducedMotion: 'invalid',
    };

    const sanitized = sanitizeThemeConfig(invalidConfig);

    expect(sanitized).toEqual(DEFAULT_THEME_CONFIG);
  });

  it('preserves valid parts of partially invalid config', () => {
    const partiallyInvalidConfig = {
      mode: 'dark',
      contrast: 'invalid',
      reducedMotion: true,
    };

    const sanitized = sanitizeThemeConfig(partiallyInvalidConfig);

    expect(sanitized).toEqual({
      mode: 'dark',
      contrast: 'normal',
      reducedMotion: true,
    });
  });
});

describe('Polish business theme presets', () => {
  it('applies professional preset', () => {
    applyThemePreset('professional');

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      THEME_STORAGE_KEYS.USER_PREFERENCES,
      expect.stringContaining('"mode":"light"')
    );
  });

  it('applies accessible preset', () => {
    applyThemePreset('accessible');

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      THEME_STORAGE_KEYS.USER_PREFERENCES,
      expect.stringContaining('"contrast":"high"')
    );
  });

  it('applies dark professional preset', () => {
    applyThemePreset('darkProfessional');

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      THEME_STORAGE_KEYS.USER_PREFERENCES,
      expect.stringContaining('"mode":"dark"')
    );
  });
});

describe('SSR compatibility', () => {
  const originalWindow = global.window;

  beforeAll(() => {
    // @ts-ignore
    delete global.window;
  });

  afterAll(() => {
    global.window = originalWindow;
  });

  it('returns default config for SSR', () => {
    const config = getInitialThemeConfig();
    expect(config).toEqual(DEFAULT_THEME_CONFIG);
  });

  it('returns empty preferences for SSR', () => {
    const preferences = getSystemPreferences();
    expect(preferences).toEqual({});
  });
});