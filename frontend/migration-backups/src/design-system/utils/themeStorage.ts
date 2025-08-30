// Theme Storage Utilities
import { ThemeConfig, ThemeMode, ContrastMode } from '../providers/ThemeProvider';

// Storage keys
export const THEME_STORAGE_KEYS = {
  MODE: 'faktulove-theme-mode',
  CONTRAST: 'faktulove-theme-contrast',
  REDUCED_MOTION: 'faktulove-theme-reduced-motion',
  CUSTOM_PROPERTIES: 'faktulove-theme-custom-properties',
  USER_PREFERENCES: 'faktulove-theme-user-preferences',
} as const;

// Default theme configuration
export const DEFAULT_THEME_CONFIG: ThemeConfig = {
  mode: 'auto',
  contrast: 'normal',
  reducedMotion: false,
};

// Extended user preferences
export interface UserThemePreferences extends ThemeConfig {
  customColors?: Record<string, string>;
  fontSize?: 'small' | 'medium' | 'large';
  compactMode?: boolean;
  animations?: boolean;
  lastUpdated?: number;
}

// Theme storage manager
export class ThemeStorageManager {
  private static instance: ThemeStorageManager;
  private isClient: boolean;
  
  private constructor() {
    this.isClient = typeof window !== 'undefined';
  }
  
  public static getInstance(): ThemeStorageManager {
    if (!ThemeStorageManager.instance) {
      ThemeStorageManager.instance = new ThemeStorageManager();
    }
    return ThemeStorageManager.instance;
  }
  
  // Basic theme config operations
  public saveThemeConfig(config: ThemeConfig): void {
    if (!this.isClient) return;
    
    try {
      localStorage.setItem(THEME_STORAGE_KEYS.MODE, config.mode);
      localStorage.setItem(THEME_STORAGE_KEYS.CONTRAST, config.contrast);
      localStorage.setItem(THEME_STORAGE_KEYS.REDUCED_MOTION, config.reducedMotion.toString());
    } catch (error) {
      console.warn('Failed to save theme config to localStorage:', error);
    }
  }
  
  public loadThemeConfig(): ThemeConfig {
    if (!this.isClient) return DEFAULT_THEME_CONFIG;
    
    try {
      const mode = localStorage.getItem(THEME_STORAGE_KEYS.MODE) as ThemeMode;
      const contrast = localStorage.getItem(THEME_STORAGE_KEYS.CONTRAST) as ContrastMode;
      const reducedMotion = localStorage.getItem(THEME_STORAGE_KEYS.REDUCED_MOTION) === 'true';
      
      return {
        mode: mode || DEFAULT_THEME_CONFIG.mode,
        contrast: contrast || DEFAULT_THEME_CONFIG.contrast,
        reducedMotion: reducedMotion || DEFAULT_THEME_CONFIG.reducedMotion,
      };
    } catch (error) {
      console.warn('Failed to load theme config from localStorage:', error);
      return DEFAULT_THEME_CONFIG;
    }
  }
  
  // Extended user preferences operations
  public saveUserPreferences(preferences: UserThemePreferences): void {
    if (!this.isClient) return;
    
    try {
      const preferencesWithTimestamp = {
        ...preferences,
        lastUpdated: Date.now(),
      };
      
      localStorage.setItem(
        THEME_STORAGE_KEYS.USER_PREFERENCES,
        JSON.stringify(preferencesWithTimestamp)
      );
      
      // Also save basic config for backward compatibility
      this.saveThemeConfig({
        mode: preferences.mode,
        contrast: preferences.contrast,
        reducedMotion: preferences.reducedMotion,
      });
    } catch (error) {
      console.warn('Failed to save user preferences to localStorage:', error);
    }
  }
  
  public loadUserPreferences(): UserThemePreferences {
    if (!this.isClient) return DEFAULT_THEME_CONFIG;
    
    try {
      const stored = localStorage.getItem(THEME_STORAGE_KEYS.USER_PREFERENCES);
      if (!stored) {
        // Fallback to basic config if no extended preferences exist
        return this.loadThemeConfig();
      }
      
      const preferences = JSON.parse(stored) as UserThemePreferences;
      
      // Validate and merge with defaults
      return {
        ...DEFAULT_THEME_CONFIG,
        ...preferences,
      };
    } catch (error) {
      console.warn('Failed to load user preferences from localStorage:', error);
      return this.loadThemeConfig();
    }
  }
  
  // Custom CSS properties operations
  public saveCustomProperties(properties: Record<string, string>): void {
    if (!this.isClient) return;
    
    try {
      localStorage.setItem(
        THEME_STORAGE_KEYS.CUSTOM_PROPERTIES,
        JSON.stringify(properties)
      );
    } catch (error) {
      console.warn('Failed to save custom properties to localStorage:', error);
    }
  }
  
  public loadCustomProperties(): Record<string, string> {
    if (!this.isClient) return {};
    
    try {
      const stored = localStorage.getItem(THEME_STORAGE_KEYS.CUSTOM_PROPERTIES);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.warn('Failed to load custom properties from localStorage:', error);
      return {};
    }
  }
  
  // Utility methods
  public clearThemeData(): void {
    if (!this.isClient) return;
    
    try {
      Object.values(THEME_STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key);
      });
    } catch (error) {
      console.warn('Failed to clear theme data from localStorage:', error);
    }
  }
  
  public exportThemeData(): string {
    if (!this.isClient) return '{}';
    
    try {
      const themeData = {
        config: this.loadThemeConfig(),
        preferences: this.loadUserPreferences(),
        customProperties: this.loadCustomProperties(),
        exportedAt: new Date().toISOString(),
      };
      
      return JSON.stringify(themeData, null, 2);
    } catch (error) {
      console.warn('Failed to export theme data:', error);
      return '{}';
    }
  }
  
  public importThemeData(jsonData: string): boolean {
    if (!this.isClient) return false;
    
    try {
      const themeData = JSON.parse(jsonData);
      
      if (themeData.config) {
        this.saveThemeConfig(themeData.config);
      }
      
      if (themeData.preferences) {
        this.saveUserPreferences(themeData.preferences);
      }
      
      if (themeData.customProperties) {
        this.saveCustomProperties(themeData.customProperties);
      }
      
      return true;
    } catch (error) {
      console.warn('Failed to import theme data:', error);
      return false;
    }
  }
  
  // Migration utilities
  public migrateFromOldStorage(): void {
    if (!this.isClient) return;
    
    try {
      // Check for old theme storage keys and migrate
      const oldKeys = [
        'theme-mode',
        'dark-mode',
        'high-contrast',
        'reduced-motion',
      ];
      
      const migrationData: Partial<ThemeConfig> = {};
      let hasMigrationData = false;
      
      oldKeys.forEach(key => {
        const value = localStorage.getItem(key);
        if (value) {
          hasMigrationData = true;
          
          switch (key) {
            case 'theme-mode':
            case 'dark-mode':
              if (value === 'true' || value === 'dark') {
                migrationData.mode = 'dark';
              } else if (value === 'false' || value === 'light') {
                migrationData.mode = 'light';
              }
              break;
            case 'high-contrast':
              if (value === 'true') {
                migrationData.contrast = 'high';
              }
              break;
            case 'reduced-motion':
              if (value === 'true') {
                migrationData.reducedMotion = true;
              }
              break;
          }
          
          // Remove old key
          localStorage.removeItem(key);
        }
      });
      
      // Save migrated data
      if (hasMigrationData) {
        const currentConfig = this.loadThemeConfig();
        const mergedConfig = { ...currentConfig, ...migrationData };
        this.saveThemeConfig(mergedConfig);
        
        console.log('Theme data migrated from old storage format');
      }
    } catch (error) {
      console.warn('Failed to migrate theme data from old storage:', error);
    }
  }
}

// Singleton instance
export const themeStorage = ThemeStorageManager.getInstance();

// Convenience functions
export const saveThemeConfig = (config: ThemeConfig): void => {
  themeStorage.saveThemeConfig(config);
};

export const loadThemeConfig = (): ThemeConfig => {
  return themeStorage.loadThemeConfig();
};

export const saveUserPreferences = (preferences: UserThemePreferences): void => {
  themeStorage.saveUserPreferences(preferences);
};

export const loadUserPreferences = (): UserThemePreferences => {
  return themeStorage.loadUserPreferences();
};

export const clearThemeData = (): void => {
  themeStorage.clearThemeData();
};

export const exportThemeData = (): string => {
  return themeStorage.exportThemeData();
};

export const importThemeData = (jsonData: string): boolean => {
  return themeStorage.importThemeData(jsonData);
};

// React hooks for theme storage
export const useThemeStorage = () => {
  return {
    save: saveThemeConfig,
    load: loadThemeConfig,
    savePreferences: saveUserPreferences,
    loadPreferences: loadUserPreferences,
    clear: clearThemeData,
    export: exportThemeData,
    import: importThemeData,
  };
};

// Theme loading utilities for SSR
export const getInitialThemeConfig = (): ThemeConfig => {
  // For SSR, return default config
  if (typeof window === 'undefined') {
    return DEFAULT_THEME_CONFIG;
  }
  
  // For client-side, load from storage
  return loadThemeConfig();
};

export const getSystemPreferences = (): Partial<ThemeConfig> => {
  if (typeof window === 'undefined') {
    return {};
  }
  
  const preferences: Partial<ThemeConfig> = {};
  
  try {
    // Check system dark mode preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      preferences.mode = 'dark';
    } else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
      preferences.mode = 'light';
    }
    
    // Check system high contrast preference
    if (window.matchMedia('(prefers-contrast: high)').matches) {
      preferences.contrast = 'high';
    }
    
    // Check system reduced motion preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      preferences.reducedMotion = true;
    }
  } catch (error) {
    console.warn('Failed to detect system preferences:', error);
  }
  
  return preferences;
};

// Theme validation utilities
export const validateThemeConfig = (config: any): config is ThemeConfig => {
  if (!config || typeof config !== 'object') {
    return false;
  }
  
  const validModes: ThemeMode[] = ['light', 'dark', 'auto'];
  const validContrasts: ContrastMode[] = ['normal', 'high'];
  
  return (
    validModes.includes(config.mode) &&
    validContrasts.includes(config.contrast) &&
    typeof config.reducedMotion === 'boolean'
  );
};

export const sanitizeThemeConfig = (config: any): ThemeConfig => {
  if (validateThemeConfig(config)) {
    return config;
  }
  
  return {
    mode: ['light', 'dark', 'auto'].includes(config?.mode) ? config.mode : DEFAULT_THEME_CONFIG.mode,
    contrast: ['normal', 'high'].includes(config?.contrast) ? config.contrast : DEFAULT_THEME_CONFIG.contrast,
    reducedMotion: typeof config?.reducedMotion === 'boolean' ? config.reducedMotion : DEFAULT_THEME_CONFIG.reducedMotion,
  };
};

// Polish business theme presets
export const POLISH_BUSINESS_THEME_PRESETS = {
  professional: {
    mode: 'light' as ThemeMode,
    contrast: 'normal' as ContrastMode,
    reducedMotion: false,
    customColors: {
      '--color-primary-600': '#2563eb', // Professional blue
      '--color-success-600': '#059669', // Polish business green
    },
  },
  
  accessible: {
    mode: 'light' as ThemeMode,
    contrast: 'high' as ContrastMode,
    reducedMotion: true,
    customColors: {
      '--color-text-primary': '#000000',
      '--color-background-primary': '#ffffff',
    },
  },
  
  darkProfessional: {
    mode: 'dark' as ThemeMode,
    contrast: 'normal' as ContrastMode,
    reducedMotion: false,
    customColors: {
      '--color-primary-500': '#3b82f6', // Adjusted for dark mode
    },
  },
} as const;

export type PolishBusinessThemePreset = keyof typeof POLISH_BUSINESS_THEME_PRESETS;

export const applyThemePreset = (preset: PolishBusinessThemePreset): void => {
  const presetConfig = POLISH_BUSINESS_THEME_PRESETS[preset];
  const userPreferences: UserThemePreferences = {
    ...presetConfig,
    lastUpdated: Date.now(),
  };
  
  saveUserPreferences(userPreferences);
};

export default themeStorage;