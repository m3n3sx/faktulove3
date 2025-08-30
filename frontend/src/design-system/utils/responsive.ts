// Responsive Utilities
import React from 'react';
import { breakpoints, mediaQueries, containerMaxWidths, gridColumns } from '../tokens/breakpoints';

// Responsive value type
export type ResponsiveValue<T> = T | {
  xs?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  '2xl'?: T;
};

// Responsive utility functions
export const responsiveUtils = {
  // Get responsive CSS for a property
  getResponsiveCSS: <T extends string | number>(
    property: string,
    value: ResponsiveValue<T>
  ): Record<string, any> => {
    if (typeof value !== 'object' || value === null) {
      return { [property]: value };
    }
    
    const css: Record<string, any> = {};
    
    // Base value (mobile first)
    if (value.xs !== undefined) {
      css[property] = value.xs;
    }
    
    // Responsive values
    Object.entries(value).forEach(([breakpoint, val]) => {
      if (breakpoint !== 'xs' && val !== undefined) {
        const mediaQuery = mediaQueries[breakpoint as keyof typeof mediaQueries];
        if (!css[mediaQuery]) {
          css[mediaQuery] = {};
        }
        css[mediaQuery][property] = val;
      }
    });
    
    return css;
  },
  
  // Get container max-width for breakpoint
  getContainerMaxWidth: (breakpoint: keyof typeof containerMaxWidths): string => {
    return containerMaxWidths[breakpoint];
  },
  
  // Get grid columns for breakpoint
  getGridColumns: (breakpoint: keyof typeof gridColumns): number => {
    return gridColumns[breakpoint];
  },
  
  // Check if current viewport matches breakpoint
  matchesBreakpoint: (breakpoint: keyof typeof breakpoints): boolean => {
    if (typeof window === 'undefined') return false;
    
    const breakpointValue = parseInt(breakpoints[breakpoint]);
    return window.innerWidth >= breakpointValue;
  },
  
  // Get current breakpoint
  getCurrentBreakpoint: (): keyof typeof breakpoints => {
    if (typeof window === 'undefined') return 'xs';
    
    const width = window.innerWidth;
    
    if (width >= parseInt(breakpoints['2xl'])) return '2xl';
    if (width >= parseInt(breakpoints.xl)) return 'xl';
    if (width >= parseInt(breakpoints.lg)) return 'lg';
    if (width >= parseInt(breakpoints.md)) return 'md';
    if (width >= parseInt(breakpoints.sm)) return 'sm';
    return 'xs';
  },
} as const;

// React hook for responsive values
export const useResponsiveValue = <T>(value: ResponsiveValue<T>): T => {
  const [currentValue, setCurrentValue] = React.useState<T>(() => {
    if (typeof value !== 'object' || value === null) {
      return value;
    }
    
    // Return mobile value by default
    return (value as any).xs || (Object.values(value)[0] as T);
  });
  
  React.useEffect(() => {
    if (typeof value !== 'object' || value === null) {
      setCurrentValue(value);
      return;
    }
    
    const updateValue = () => {
      const currentBreakpoint = responsiveUtils.getCurrentBreakpoint();
      const breakpointOrder: (keyof typeof breakpoints)[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];
      
      // Find the appropriate value for current breakpoint
      let selectedValue: T | undefined;
      
      for (let i = breakpointOrder.indexOf(currentBreakpoint); i >= 0; i--) {
        const bp = breakpointOrder[i];
        if ((value as any)[bp] !== undefined) {
          selectedValue = (value as any)[bp];
          break;
        }
      }
      
      if (selectedValue !== undefined) {
        setCurrentValue(selectedValue);
      }
    };
    
    updateValue();
    window.addEventListener('resize', updateValue);
    
    return () => {
      window.removeEventListener('resize', updateValue);
    };
  }, [value]);
  
  return currentValue;
};

// React hook for breakpoint matching
export const useBreakpoint = (breakpoint: keyof typeof breakpoints): boolean => {
  const [matches, setMatches] = React.useState(() => 
    responsiveUtils.matchesBreakpoint(breakpoint)
  );
  
  React.useEffect(() => {
    const updateMatches = () => {
      setMatches(responsiveUtils.matchesBreakpoint(breakpoint));
    };
    
    updateMatches();
    window.addEventListener('resize', updateMatches);
    
    return () => {
      window.removeEventListener('resize', updateMatches);
    };
  }, [breakpoint]);
  
  return matches;
};

// React hook for current breakpoint
export const useCurrentBreakpoint = (): keyof typeof breakpoints => {
  const [currentBreakpoint, setCurrentBreakpoint] = React.useState(() => 
    responsiveUtils.getCurrentBreakpoint()
  );
  
  React.useEffect(() => {
    const updateBreakpoint = () => {
      setCurrentBreakpoint(responsiveUtils.getCurrentBreakpoint());
    };
    
    updateBreakpoint();
    window.addEventListener('resize', updateBreakpoint);
    
    return () => {
      window.removeEventListener('resize', updateBreakpoint);
    };
  }, []);
  
  return currentBreakpoint;
};

// Responsive grid utilities
export const gridUtils = {
  // Generate responsive grid classes
  getGridClasses: (columns: ResponsiveValue<number>): string => {
    if (typeof columns === 'number') {
      return `grid-cols-${columns}`;
    }
    
    const classes: string[] = [];
    
    Object.entries(columns).forEach(([breakpoint, cols]) => {
      if (cols !== undefined) {
        const prefix = breakpoint === 'xs' ? '' : `${breakpoint}:`;
        classes.push(`${prefix}grid-cols-${cols}`);
      }
    });
    
    return classes.join(' ');
  },
  
  // Generate responsive gap classes
  getGapClasses: (gap: ResponsiveValue<number>): string => {
    if (typeof gap === 'number') {
      return `gap-${gap}`;
    }
    
    const classes: string[] = [];
    
    Object.entries(gap).forEach(([breakpoint, gapValue]) => {
      if (gapValue !== undefined) {
        const prefix = breakpoint === 'xs' ? '' : `${breakpoint}:`;
        classes.push(`${prefix}gap-${gapValue}`);
      }
    });
    
    return classes.join(' ');
  },
} as const;

// Container utilities for Polish business layouts
export const containerUtils = {
  // Standard container classes
  getContainerClasses: (size: 'sm' | 'md' | 'lg' | 'xl' | 'full' = 'xl'): string => {
    const baseClasses = 'mx-auto px-4 sm:px-6 lg:px-8';
    
    switch (size) {
      case 'sm':
        return `${baseClasses} max-w-3xl`;
      case 'md':
        return `${baseClasses} max-w-5xl`;
      case 'lg':
        return `${baseClasses} max-w-7xl`;
      case 'xl':
        return `${baseClasses} max-w-screen-xl`;
      case 'full':
        return `${baseClasses} max-w-full`;
      default:
        return `${baseClasses} max-w-screen-xl`;
    }
  },
  
  // Invoice-specific container
  getInvoiceContainerClasses: (): string => {
    return 'mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl';
  },
  
  // Dashboard container
  getDashboardContainerClasses: (): string => {
    return 'mx-auto px-4 sm:px-6 lg:px-8 max-w-screen-2xl';
  },
} as const;

// Polish business responsive patterns
export const polishBusinessResponsive = {
  // Invoice table responsive behavior
  invoiceTableBreakpoints: {
    mobile: 'max-md:hidden',
    tablet: 'md:table-cell',
    desktop: 'lg:table-cell',
  },
  
  // Form layout responsive patterns
  formResponsive: {
    singleColumn: 'grid-cols-1',
    twoColumn: 'grid-cols-1 md:grid-cols-2',
    threeColumn: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    autoFit: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
  },
  
  // Navigation responsive patterns
  navigationResponsive: {
    mobileHidden: 'hidden md:block',
    mobileOnly: 'block md:hidden',
    desktopSidebar: 'hidden lg:block lg:w-64',
    mobileSidebar: 'block lg:hidden',
  },
} as const;



export type ResponsiveUtilsType = typeof responsiveUtils;
export type GridUtilsType = typeof gridUtils;
export type ContainerUtilsType = typeof containerUtils;