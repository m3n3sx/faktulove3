import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, useTheme, ThemeMode, ContrastMode } from '../ThemeProvider';

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

// Test component that uses the theme
const TestComponent: React.FC = () => {
  const {
    config,
    setMode,
    setContrast,
    setReducedMotion,
    toggleMode,
    toggleContrast,
    isDark,
    isHighContrast,
  } = useTheme();

  return (
    <div>
      <div data-testid="theme-mode">{config.mode}</div>
      <div data-testid="theme-contrast">{config.contrast}</div>
      <div data-testid="theme-reduced-motion">{config.reducedMotion.toString()}</div>
      <div data-testid="is-dark">{isDark.toString()}</div>
      <div data-testid="is-high-contrast">{isHighContrast.toString()}</div>
      
      <button data-testid="set-light" onClick={() => setMode('light')}>
        Set Light
      </button>
      <button data-testid="set-dark" onClick={() => setMode('dark')}>
        Set Dark
      </button>
      <button data-testid="set-auto" onClick={() => setMode('auto')}>
        Set Auto
      </button>
      <button data-testid="toggle-mode" onClick={toggleMode}>
        Toggle Mode
      </button>
      
      <button data-testid="set-normal-contrast" onClick={() => setContrast('normal')}>
        Set Normal Contrast
      </button>
      <button data-testid="set-high-contrast" onClick={() => setContrast('high')}>
        Set High Contrast
      </button>
      <button data-testid="toggle-contrast" onClick={toggleContrast}>
        Toggle Contrast
      </button>
      
      <button data-testid="set-reduced-motion" onClick={() => setReducedMotion(true)}>
        Enable Reduced Motion
      </button>
      <button data-testid="unset-reduced-motion" onClick={() => setReducedMotion(false)}>
        Disable Reduced Motion
      </button>
    </div>
  );
};

describe('ThemeProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
    
    // Reset document classes
    document.documentElement.className = '';
    document.documentElement.style.cssText = '';
  });

  it('renders children correctly', () => {
    render(
      <ThemeProvider>
        <div data-testid="child">Test Child</div>
      </ThemeProvider>
    );

    expect(screen.getByTestId('child')).toBeInTheDocument();
  });

  it('provides default theme configuration', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-mode')).toHaveTextContent('auto');
    expect(screen.getByTestId('theme-contrast')).toHaveTextContent('normal');
    expect(screen.getByTestId('theme-reduced-motion')).toHaveTextContent('false');
  });

  it('loads configuration from localStorage', () => {
    mockLocalStorage.getItem.mockImplementation((key) => {
      switch (key) {
        case 'faktulove-theme-mode':
          return 'dark';
        case 'faktulove-theme-contrast':
          return 'high';
        case 'faktulove-theme-reduced-motion':
          return 'true';
        default:
          return null;
      }
    });

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');
    expect(screen.getByTestId('theme-contrast')).toHaveTextContent('high');
    expect(screen.getByTestId('theme-reduced-motion')).toHaveTextContent('true');
  });

  it('uses default props when provided', () => {
    render(
      <ThemeProvider defaultMode="dark" defaultContrast="high" defaultReducedMotion={true}>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');
    expect(screen.getByTestId('theme-contrast')).toHaveTextContent('high');
    expect(screen.getByTestId('theme-reduced-motion')).toHaveTextContent('true');
  });

  it('updates theme mode and saves to localStorage', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTestId('set-dark'));

    expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('faktulove-theme-mode', 'dark');
  });

  it('updates contrast mode and saves to localStorage', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTestId('set-high-contrast'));

    expect(screen.getByTestId('theme-contrast')).toHaveTextContent('high');
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('faktulove-theme-contrast', 'high');
  });

  it('updates reduced motion and saves to localStorage', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTestId('set-reduced-motion'));

    expect(screen.getByTestId('theme-reduced-motion')).toHaveTextContent('true');
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('faktulove-theme-reduced-motion', 'true');
  });

  it('toggles theme mode correctly', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Initial: auto -> light
    fireEvent.click(screen.getByTestId('toggle-mode'));
    expect(screen.getByTestId('theme-mode')).toHaveTextContent('light');

    // light -> dark
    fireEvent.click(screen.getByTestId('toggle-mode'));
    expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');

    // dark -> auto
    fireEvent.click(screen.getByTestId('toggle-mode'));
    expect(screen.getByTestId('theme-mode')).toHaveTextContent('auto');
  });

  it('toggles contrast mode correctly', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Initial: normal -> high
    fireEvent.click(screen.getByTestId('toggle-contrast'));
    expect(screen.getByTestId('theme-contrast')).toHaveTextContent('high');

    // high -> normal
    fireEvent.click(screen.getByTestId('toggle-contrast'));
    expect(screen.getByTestId('theme-contrast')).toHaveTextContent('normal');
  });

  it('calculates isDark correctly for different modes', () => {
    // Mock system preference for dark mode
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === '(prefers-color-scheme: dark)') {
        return mockMatchMedia(true);
      }
      return mockMatchMedia(false);
    });

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Auto mode with system dark preference
    expect(screen.getByTestId('is-dark')).toHaveTextContent('true');

    // Explicit light mode
    fireEvent.click(screen.getByTestId('set-light'));
    expect(screen.getByTestId('is-dark')).toHaveTextContent('false');

    // Explicit dark mode
    fireEvent.click(screen.getByTestId('set-dark'));
    expect(screen.getByTestId('is-dark')).toHaveTextContent('true');
  });

  it('calculates isHighContrast correctly', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Normal contrast
    expect(screen.getByTestId('is-high-contrast')).toHaveTextContent('false');

    // High contrast
    fireEvent.click(screen.getByTestId('set-high-contrast'));
    expect(screen.getByTestId('is-high-contrast')).toHaveTextContent('true');
  });

  it('applies CSS classes to document element', async () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Set dark mode
    fireEvent.click(screen.getByTestId('set-dark'));

    await waitFor(() => {
      expect(document.documentElement.classList.contains('theme-dark')).toBe(true);
      expect(document.documentElement.classList.contains('theme-light')).toBe(false);
    });

    // Set light mode
    fireEvent.click(screen.getByTestId('set-light'));

    await waitFor(() => {
      expect(document.documentElement.classList.contains('theme-dark')).toBe(false);
      expect(document.documentElement.classList.contains('theme-light')).toBe(true);
    });

    // Set high contrast
    fireEvent.click(screen.getByTestId('set-high-contrast'));

    await waitFor(() => {
      expect(document.documentElement.classList.contains('theme-high-contrast')).toBe(true);
    });

    // Enable reduced motion
    fireEvent.click(screen.getByTestId('set-reduced-motion'));

    await waitFor(() => {
      expect(document.documentElement.classList.contains('theme-reduced-motion')).toBe(true);
    });
  });

  it('sets color-scheme CSS property', async () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Set dark mode
    fireEvent.click(screen.getByTestId('set-dark'));

    await waitFor(() => {
      expect(document.documentElement.style.colorScheme).toBe('dark');
    });

    // Set light mode
    fireEvent.click(screen.getByTestId('set-light'));

    await waitFor(() => {
      expect(document.documentElement.style.colorScheme).toBe('light');
    });
  });

  it('responds to system preference changes', async () => {
    const darkModeQuery = mockMatchMedia(false);
    window.matchMedia = jest.fn().mockImplementation((query) => {
      if (query === '(prefers-color-scheme: dark)') {
        return darkModeQuery;
      }
      return mockMatchMedia(false);
    });

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Initially light (auto mode with system light preference)
    expect(screen.getByTestId('is-dark')).toHaveTextContent('false');

    // Simulate system preference change to dark
    darkModeQuery.matches = true;
    fireEvent(darkModeQuery, new Event('change'));

    await waitFor(() => {
      expect(screen.getByTestId('is-dark')).toHaveTextContent('true');
    });
  });

  it('throws error when useTheme is used outside provider', () => {
    const TestComponentWithoutProvider = () => {
      useTheme();
      return null;
    };

    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestComponentWithoutProvider />);
    }).toThrow('useTheme must be used within a ThemeProvider');

    consoleSpy.mockRestore();
  });

  it('handles localStorage errors gracefully', () => {
    mockLocalStorage.setItem.mockImplementation(() => {
      throw new Error('localStorage error');
    });

    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Should not throw, but should log warning
    fireEvent.click(screen.getByTestId('set-dark'));

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Failed to save theme config')
    );

    consoleSpy.mockRestore();
  });
});