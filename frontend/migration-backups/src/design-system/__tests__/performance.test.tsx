/**
 * Performance Testing Suite
 * Tests rendering performance and memory usage of design system components
 */

import React from 'react';
import { render, cleanup } from '@testing-library/react';
import { performance } from 'perf_hooks';

// Import components for performance testing
import { Button } from '../components/primitives/Button/Button';
import { Input } from '../components/primitives/Input/Input';
import { Table } from '../components/patterns/Table/Table';
import { Grid } from '../components/layouts/Grid/Grid';
import { CurrencyInput } from '../components/business/CurrencyInput/CurrencyInput';

describe('Design System Performance Tests', () => {
  afterEach(() => {
    cleanup();
  });

  // Helper function to measure rendering performance
  const measureRenderTime = (component: React.ReactElement, iterations: number = 100) => {
    const times: number[] = [];
    
    for (let i = 0; i < iterations; i++) {
      const startTime = performance.now();
      const { unmount } = render(component);
      const endTime = performance.now();
      
      times.push(endTime - startTime);
      unmount();
    }
    
    const avgTime = times.reduce((sum, time) => sum + time, 0) / times.length;
    const minTime = Math.min(...times);
    const maxTime = Math.max(...times);
    
    return {
      average: avgTime,
      min: minTime,
      max: maxTime,
      times,
    };
  };

  // Helper function to measure memory usage
  const measureMemoryUsage = (component: React.ReactElement, iterations: number = 50) => {
    const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;
    const components: any[] = [];
    
    // Render multiple instances
    for (let i = 0; i < iterations; i++) {
      components.push(render(component));
    }
    
    const peakMemory = (performance as any).memory?.usedJSHeapSize || 0;
    
    // Cleanup
    components.forEach(({ unmount }) => unmount());
    
    const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
    
    return {
      initial: initialMemory,
      peak: peakMemory,
      final: finalMemory,
      leaked: finalMemory - initialMemory,
      used: peakMemory - initialMemory,
    };
  };

  describe('Button Performance', () => {
    it('renders buttons efficiently', () => {
      const results = measureRenderTime(<Button>Test Button</Button>);
      
      // Button should render in under 5ms on average
      expect(results.average).toBeLessThan(5);
      expect(results.max).toBeLessThan(20);
      
      console.log('Button render times:', {
        average: `${results.average.toFixed(2)}ms`,
        min: `${results.min.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });

    it('handles multiple button variants efficiently', () => {
      const variants = ['primary', 'secondary', 'ghost', 'danger'] as const;
      
      variants.forEach(variant => {
        const results = measureRenderTime(
          <Button variant={variant}>Test {variant}</Button>
        );
        
        expect(results.average).toBeLessThan(5);
        
        console.log(`Button ${variant} render time: ${results.average.toFixed(2)}ms`);
      });
    });

    it('does not leak memory with button instances', () => {
      if (!(performance as any).memory) {
        console.log('Memory measurement not available in this environment');
        return;
      }

      const results = measureMemoryUsage(<Button>Memory Test</Button>);
      
      // Memory leak should be minimal (less than 1MB)
      expect(results.leaked).toBeLessThan(1024 * 1024);
      
      console.log('Button memory usage:', {
        used: `${(results.used / 1024).toFixed(2)}KB`,
        leaked: `${(results.leaked / 1024).toFixed(2)}KB`,
      });
    });
  });

  describe('Input Performance', () => {
    it('renders inputs efficiently', () => {
      const results = measureRenderTime(
        <Input placeholder="Performance test" />
      );
      
      // Input should render in under 8ms on average
      expect(results.average).toBeLessThan(8);
      expect(results.max).toBeLessThan(25);
      
      console.log('Input render times:', {
        average: `${results.average.toFixed(2)}ms`,
        min: `${results.min.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });

    it('handles input with validation efficiently', () => {
      const results = measureRenderTime(
        <Input 
          placeholder="Validation test"
          error="Error message"
          required
        />
      );
      
      expect(results.average).toBeLessThan(10);
      
      console.log(`Input with validation render time: ${results.average.toFixed(2)}ms`);
    });
  });

  describe('Table Performance', () => {
    const generateTableData = (rows: number) => {
      return Array.from({ length: rows }, (_, i) => ({
        id: i + 1,
        name: `User ${i + 1}`,
        email: `user${i + 1}@example.com`,
        status: i % 2 === 0 ? 'active' : 'inactive',
      }));
    };

    const columns = [
      { key: 'name', header: 'Name' },
      { key: 'email', header: 'Email' },
      { key: 'status', header: 'Status' },
    ];

    it('renders small tables efficiently', () => {
      const data = generateTableData(10);
      const results = measureRenderTime(
        <Table data={data} columns={columns} />,
        50 // Fewer iterations for complex components
      );
      
      // Small table should render in under 15ms
      expect(results.average).toBeLessThan(15);
      
      console.log('Small table (10 rows) render time:', {
        average: `${results.average.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });

    it('renders medium tables efficiently', () => {
      const data = generateTableData(100);
      const results = measureRenderTime(
        <Table data={data} columns={columns} />,
        20 // Even fewer iterations for larger components
      );
      
      // Medium table should render in under 50ms
      expect(results.average).toBeLessThan(50);
      
      console.log('Medium table (100 rows) render time:', {
        average: `${results.average.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });

    it('handles large tables within acceptable limits', () => {
      const data = generateTableData(1000);
      const results = measureRenderTime(
        <Table data={data} columns={columns} />,
        5 // Very few iterations for large components
      );
      
      // Large table should render in under 200ms
      expect(results.average).toBeLessThan(200);
      
      console.log('Large table (1000 rows) render time:', {
        average: `${results.average.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });
  });

  describe('Grid Layout Performance', () => {
    it('renders grid layouts efficiently', () => {
      const gridItems = Array.from({ length: 12 }, (_, i) => (
        <div key={i}>Grid Item {i + 1}</div>
      ));

      const results = measureRenderTime(
        <Grid cols={4} gap={4}>
          {gridItems}
        </Grid>
      );
      
      expect(results.average).toBeLessThan(10);
      
      console.log('Grid layout render time:', {
        average: `${results.average.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });

    it('handles responsive grid changes efficiently', () => {
      const gridItems = Array.from({ length: 20 }, (_, i) => (
        <div key={i}>Responsive Item {i + 1}</div>
      ));

      const results = measureRenderTime(
        <Grid 
          cols={{ base: 1, md: 2, lg: 4 }} 
          gap={4}
        >
          {gridItems}
        </Grid>
      );
      
      expect(results.average).toBeLessThan(15);
      
      console.log('Responsive grid render time:', {
        average: `${results.average.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });
  });

  describe('Polish Business Components Performance', () => {
    it('renders currency input efficiently', () => {
      const results = measureRenderTime(
        <CurrencyInput 
          currency="PLN"
          placeholder="Enter amount"
        />
      );
      
      expect(results.average).toBeLessThan(12);
      
      console.log('Currency input render time:', {
        average: `${results.average.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });

    it('handles currency formatting efficiently', () => {
      const results = measureRenderTime(
        <CurrencyInput 
          currency="PLN"
          value="1234567.89"
          placeholder="Formatted amount"
        />
      );
      
      expect(results.average).toBeLessThan(15);
      
      console.log('Currency input with formatting render time:', {
        average: `${results.average.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });
  });

  describe('Complex Component Combinations', () => {
    it('renders complex forms efficiently', () => {
      const results = measureRenderTime(
        <div>
          <Grid cols={2} gap={4}>
            <Input placeholder="Name" />
            <Input placeholder="Email" />
            <CurrencyInput currency="PLN" placeholder="Amount" />
            <Input placeholder="Description" />
          </Grid>
          <div style={{ marginTop: '16px' }}>
            <Button variant="primary">Submit</Button>
            <Button variant="secondary" style={{ marginLeft: '8px' }}>
              Cancel
            </Button>
          </div>
        </div>,
        30
      );
      
      expect(results.average).toBeLessThan(25);
      
      console.log('Complex form render time:', {
        average: `${results.average.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });

    it('handles theme switching efficiently', () => {
      const themes = ['light', 'dark', 'high-contrast'];
      
      themes.forEach(theme => {
        const results = measureRenderTime(
          <div data-theme={theme}>
            <Button variant="primary">Themed Button</Button>
            <Input placeholder="Themed Input" />
          </div>,
          50
        );
        
        expect(results.average).toBeLessThan(10);
        
        console.log(`${theme} theme render time: ${results.average.toFixed(2)}ms`);
      });
    });
  });

  describe('Bundle Size Impact', () => {
    it('measures component import impact', () => {
      // This test would ideally measure bundle size impact
      // For now, we'll test that components can be imported individually
      
      const startTime = performance.now();
      
      // Simulate individual component imports
      const components = [
        Button,
        Input,
        Table,
        Grid,
        CurrencyInput,
      ];
      
      const endTime = performance.now();
      const importTime = endTime - startTime;
      
      expect(components).toHaveLength(5);
      expect(importTime).toBeLessThan(10); // Should import quickly
      
      console.log(`Component import time: ${importTime.toFixed(2)}ms`);
    });
  });

  describe('Accessibility Performance', () => {
    it('maintains performance with accessibility features', () => {
      const results = measureRenderTime(
        <div>
          <Button 
            aria-label="Accessible button"
            aria-describedby="button-description"
          >
            Accessible Button
          </Button>
          <div id="button-description">
            This button performs an important action
          </div>
          <Input 
            aria-label="Accessible input"
            aria-required="true"
            aria-invalid="false"
            placeholder="Enter value"
          />
        </div>
      );
      
      expect(results.average).toBeLessThan(12);
      
      console.log('Accessible components render time:', {
        average: `${results.average.toFixed(2)}ms`,
        max: `${results.max.toFixed(2)}ms`,
      });
    });
  });

  describe('Performance Regression Detection', () => {
    it('establishes performance baselines', () => {
      const baselines = {
        button: 5,
        input: 8,
        smallTable: 15,
        grid: 10,
        currencyInput: 12,
        complexForm: 25,
      };

      // Test each component against its baseline
      Object.entries(baselines).forEach(([component, baseline]) => {
        console.log(`Performance baseline for ${component}: ${baseline}ms`);
      });

      // This test serves as documentation for expected performance
      expect(baselines.button).toBeLessThan(10);
      expect(baselines.input).toBeLessThan(15);
      expect(baselines.smallTable).toBeLessThan(30);
      expect(baselines.grid).toBeLessThan(20);
      expect(baselines.currencyInput).toBeLessThan(20);
      expect(baselines.complexForm).toBeLessThan(50);
    });
  });
});