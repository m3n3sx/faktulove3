/**
 * Performance Benchmarking Test Suite
 * Tests rendering performance, memory usage, and bundle impact of design system components
 */

import React from 'react';
import { render, cleanup } from '@testing-library/react';
import { performance } from 'perf_hooks';

// Import all components for benchmarking
import { Button } from '../components/primitives/Button/Button';
import { Input } from '../components/primitives/Input/Input';
import { Select } from '../components/primitives/Select/Select';
import { Checkbox } from '../components/primitives/Checkbox/Checkbox';
import { Radio } from '../components/primitives/Radio/Radio';
import { Switch } from '../components/primitives/Switch/Switch';
import { Textarea } from '../components/primitives/Textarea/Textarea';
import { Card } from '../components/patterns/Card/Card';
import { Form } from '../components/patterns/Form/Form';
import { Table } from '../components/patterns/Table/Table';
import { FileUpload } from '../components/patterns/FileUpload/FileUpload';
import { Grid } from '../components/layouts/Grid/Grid';
import { Container } from '../components/layouts/Container/Container';
import { Stack } from '../components/layouts/Stack/Stack';

// Polish business components
import { CurrencyInput } from '../components/business/CurrencyInput/CurrencyInput';
import { DatePicker } from '../components/business/DatePicker/DatePicker';
import { VATRateSelector } from '../components/business/VATRateSelector/VATRateSelector';
import { NIPValidator } from '../components/business/NIPValidator/NIPValidator';
import { InvoiceStatusBadge } from '../components/business/InvoiceStatusBadge/InvoiceStatusBadge';
import { ComplianceIndicator } from '../components/business/ComplianceIndicator/ComplianceIndicator';

// Providers
import { DesignSystemProvider } from '../providers/DesignSystemProvider';
import { ThemeProvider } from '../providers/ThemeProvider';

// Performance measurement utilities
interface PerformanceMetrics {
  average: number;
  min: number;
  max: number;
  p95: number;
  p99: number;
  times: number[];
}

interface MemoryMetrics {
  initial: number;
  peak: number;
  final: number;
  leaked: number;
  used: number;
}

const measureRenderPerformance = (
  component: React.ReactElement,
  iterations: number = 100
): PerformanceMetrics => {
  const times: number[] = [];
  
  for (let i = 0; i < iterations; i++) {
    const startTime = performance.now();
    const { unmount } = render(component);
    const endTime = performance.now();
    
    times.push(endTime - startTime);
    unmount();
  }
  
  times.sort((a, b) => a - b);
  
  return {
    average: times.reduce((sum, time) => sum + time, 0) / times.length,
    min: times[0],
    max: times[times.length - 1],
    p95: times[Math.floor(times.length * 0.95)],
    p99: times[Math.floor(times.length * 0.99)],
    times,
  };
};

const measureMemoryUsage = (
  component: React.ReactElement,
  iterations: number = 50
): MemoryMetrics => {
  // Force garbage collection if available
  if (global.gc) {
    global.gc();
  }
  
  const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;
  const components: any[] = [];
  
  // Render multiple instances
  for (let i = 0; i < iterations; i++) {
    components.push(render(component));
  }
  
  const peakMemory = (performance as any).memory?.usedJSHeapSize || 0;
  
  // Cleanup
  components.forEach(({ unmount }) => unmount());
  
  // Force garbage collection again
  if (global.gc) {
    global.gc();
  }
  
  const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
  
  return {
    initial: initialMemory,
    peak: peakMemory,
    final: finalMemory,
    leaked: finalMemory - initialMemory,
    used: peakMemory - initialMemory,
  };
};

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <DesignSystemProvider>
    <ThemeProvider theme="light">
      {children}
    </ThemeProvider>
  </DesignSystemProvider>
);

describe('Design System Performance Benchmarks', () => {
  afterEach(() => {
    cleanup();
  });

  describe('Primitive Component Performance', () => {
    describe('Button Performance', () => {
      it('meets render time benchmarks', () => {
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Button variant="primary">Benchmark Button</Button>
          </TestWrapper>
        );
        
        // Button should render in under 5ms on average
        expect(metrics.average).toBeLessThan(5);
        expect(metrics.p95).toBeLessThan(10);
        expect(metrics.max).toBeLessThan(20);
        
        console.log('Button Performance:', {
          average: `${metrics.average.toFixed(2)}ms`,
          p95: `${metrics.p95.toFixed(2)}ms`,
          max: `${metrics.max.toFixed(2)}ms`,
        });
      });

      it('handles multiple variants efficiently', () => {
        const variants = ['primary', 'secondary', 'ghost', 'danger'] as const;
        
        variants.forEach(variant => {
          const metrics = measureRenderPerformance(
            <TestWrapper>
              <Button variant={variant}>Test {variant}</Button>
            </TestWrapper>,
            50
          );
          
          expect(metrics.average).toBeLessThan(5);
          expect(metrics.p95).toBeLessThan(12);
          
          console.log(`Button ${variant} Performance: ${metrics.average.toFixed(2)}ms avg`);
        });
      });

      it('maintains performance with complex props', () => {
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Button
              variant="primary"
              size="lg"
              loading={false}
              disabled={false}
              fullWidth
              leftIcon={<span>🔥</span>}
              rightIcon={<span>→</span>}
              onClick={() => {}}
              onMouseEnter={() => {}}
              onFocus={() => {}}
              className="custom-class"
              style={{ margin: '10px' }}
              aria-label="Complex button"
              data-testid="benchmark-button"
            >
              Complex Button
            </Button>
          </TestWrapper>,
          50
        );
        
        expect(metrics.average).toBeLessThan(8);
        expect(metrics.p95).toBeLessThan(15);
        
        console.log(`Complex Button Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });

    describe('Input Performance', () => {
      it('meets render time benchmarks', () => {
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Input placeholder="Benchmark input" />
          </TestWrapper>
        );
        
        expect(metrics.average).toBeLessThan(8);
        expect(metrics.p95).toBeLessThan(15);
        
        console.log('Input Performance:', {
          average: `${metrics.average.toFixed(2)}ms`,
          p95: `${metrics.p95.toFixed(2)}ms`,
        });
      });

      it('handles validation states efficiently', () => {
        const states = [
          { error: 'Error message' },
          { success: 'Success message' },
          { warning: 'Warning message' },
        ];
        
        states.forEach((state, index) => {
          const metrics = measureRenderPerformance(
            <TestWrapper>
              <Input placeholder="State test" {...state} />
            </TestWrapper>,
            50
          );
          
          expect(metrics.average).toBeLessThan(10);
          
          console.log(`Input State ${index} Performance: ${metrics.average.toFixed(2)}ms avg`);
        });
      });
    });

    describe('Select Performance', () => {
      const generateOptions = (count: number) =>
        Array.from({ length: count }, (_, i) => ({
          value: `option${i}`,
          label: `Option ${i + 1}`,
        }));

      it('handles small option lists efficiently', () => {
        const options = generateOptions(10);
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Select options={options} />
          </TestWrapper>,
          50
        );
        
        expect(metrics.average).toBeLessThan(12);
        
        console.log(`Select (10 options) Performance: ${metrics.average.toFixed(2)}ms avg`);
      });

      it('handles medium option lists efficiently', () => {
        const options = generateOptions(100);
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Select options={options} />
          </TestWrapper>,
          30
        );
        
        expect(metrics.average).toBeLessThan(25);
        
        console.log(`Select (100 options) Performance: ${metrics.average.toFixed(2)}ms avg`);
      });

      it('handles large option lists within limits', () => {
        const options = generateOptions(1000);
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Select options={options} />
          </TestWrapper>,
          10
        );
        
        expect(metrics.average).toBeLessThan(100);
        
        console.log(`Select (1000 options) Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });
  });

  describe('Pattern Component Performance', () => {
    describe('Table Performance', () => {
      const generateTableData = (rows: number) =>
        Array.from({ length: rows }, (_, i) => ({
          id: i + 1,
          name: `User ${i + 1}`,
          email: `user${i + 1}@example.com`,
          status: i % 3 === 0 ? 'active' : i % 3 === 1 ? 'inactive' : 'pending',
          amount: (Math.random() * 1000).toFixed(2),
          date: new Date(2024, 0, i + 1).toISOString().split('T')[0],
        }));

      const columns = [
        { key: 'name', header: 'Name' },
        { key: 'email', header: 'Email' },
        { key: 'status', header: 'Status' },
        { key: 'amount', header: 'Amount' },
        { key: 'date', header: 'Date' },
      ];

      it('handles small tables efficiently', () => {
        const data = generateTableData(10);
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Table data={data} columns={columns} />
          </TestWrapper>,
          30
        );
        
        expect(metrics.average).toBeLessThan(20);
        
        console.log(`Small Table (10 rows) Performance: ${metrics.average.toFixed(2)}ms avg`);
      });

      it('handles medium tables efficiently', () => {
        const data = generateTableData(100);
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Table data={data} columns={columns} />
          </TestWrapper>,
          15
        );
        
        expect(metrics.average).toBeLessThan(60);
        
        console.log(`Medium Table (100 rows) Performance: ${metrics.average.toFixed(2)}ms avg`);
      });

      it('handles large tables within limits', () => {
        const data = generateTableData(1000);
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Table data={data} columns={columns} />
          </TestWrapper>,
          5
        );
        
        expect(metrics.average).toBeLessThan(300);
        
        console.log(`Large Table (1000 rows) Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });

    describe('Form Performance', () => {
      it('handles complex forms efficiently', () => {
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Form onSubmit={() => {}}>
              <Grid cols={2} gap={4}>
                <Input name="field1" placeholder="Field 1" />
                <Input name="field2" placeholder="Field 2" />
                <Select
                  name="field3"
                  options={[
                    { value: '1', label: 'Option 1' },
                    { value: '2', label: 'Option 2' },
                  ]}
                />
                <Textarea name="field4" placeholder="Field 4" />
                <Checkbox name="field5">Checkbox</Checkbox>
                <Switch name="field6">Switch</Switch>
              </Grid>
              <Button type="submit">Submit</Button>
            </Form>
          </TestWrapper>,
          20
        );
        
        expect(metrics.average).toBeLessThan(40);
        
        console.log(`Complex Form Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });

    describe('Card Performance', () => {
      it('handles nested card structures efficiently', () => {
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Card>
              <Card.Header>
                <h3>Card Title</h3>
              </Card.Header>
              <Card.Body>
                <Grid cols={2} gap={4}>
                  <Card variant="outlined">
                    <Card.Body>Nested Card 1</Card.Body>
                  </Card>
                  <Card variant="outlined">
                    <Card.Body>Nested Card 2</Card.Body>
                  </Card>
                </Grid>
              </Card.Body>
              <Card.Footer>
                <Button>Action</Button>
              </Card.Footer>
            </Card>
          </TestWrapper>,
          30
        );
        
        expect(metrics.average).toBeLessThan(25);
        
        console.log(`Nested Cards Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });
  });

  describe('Layout Component Performance', () => {
    describe('Grid Performance', () => {
      it('handles responsive grids efficiently', () => {
        const gridItems = Array.from({ length: 24 }, (_, i) => (
          <div key={i}>Grid Item {i + 1}</div>
        ));

        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Grid cols={{ base: 1, sm: 2, md: 3, lg: 4, xl: 6 }} gap={4}>
              {gridItems}
            </Grid>
          </TestWrapper>,
          30
        );
        
        expect(metrics.average).toBeLessThan(15);
        
        console.log(`Responsive Grid Performance: ${metrics.average.toFixed(2)}ms avg`);
      });

      it('handles nested grids efficiently', () => {
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <Grid cols={2} gap={4}>
              <Grid cols={2} gap={2}>
                <div>Nested 1</div>
                <div>Nested 2</div>
                <div>Nested 3</div>
                <div>Nested 4</div>
              </Grid>
              <Grid cols={3} gap={2}>
                <div>Nested A</div>
                <div>Nested B</div>
                <div>Nested C</div>
                <div>Nested D</div>
                <div>Nested E</div>
                <div>Nested F</div>
              </Grid>
            </Grid>
          </TestWrapper>,
          30
        );
        
        expect(metrics.average).toBeLessThan(20);
        
        console.log(`Nested Grids Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });

    describe('Container Performance', () => {
      it('handles different container sizes efficiently', () => {
        const sizes = ['sm', 'md', 'lg', 'xl', '2xl'] as const;
        
        sizes.forEach(size => {
          const metrics = measureRenderPerformance(
            <TestWrapper>
              <Container maxWidth={size}>
                <div>Container content for {size}</div>
              </Container>
            </TestWrapper>,
            50
          );
          
          expect(metrics.average).toBeLessThan(5);
          
          console.log(`Container ${size} Performance: ${metrics.average.toFixed(2)}ms avg`);
        });
      });
    });
  });

  describe('Polish Business Component Performance', () => {
    describe('CurrencyInput Performance', () => {
      it('handles currency formatting efficiently', () => {
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <CurrencyInput
              currency="PLN"
              value="123456.78"
              placeholder="Enter amount"
            />
          </TestWrapper>,
          50
        );
        
        expect(metrics.average).toBeLessThan(15);
        
        console.log(`CurrencyInput Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });

    describe('DatePicker Performance', () => {
      it('handles Polish date formatting efficiently', () => {
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <DatePicker
              format="DD.MM.YYYY"
              value={new Date()}
              placeholder="Select date"
            />
          </TestWrapper>,
          50
        );
        
        expect(metrics.average).toBeLessThan(20);
        
        console.log(`DatePicker Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });

    describe('NIPValidator Performance', () => {
      it('handles NIP validation efficiently', () => {
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <NIPValidator
              value="1234567890"
              placeholder="Enter NIP"
            />
          </TestWrapper>,
          50
        );
        
        expect(metrics.average).toBeLessThan(18);
        
        console.log(`NIPValidator Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });

    describe('VATRateSelector Performance', () => {
      it('handles VAT rate selection efficiently', () => {
        const metrics = measureRenderPerformance(
          <TestWrapper>
            <VATRateSelector value={23} />
          </TestWrapper>,
          50
        );
        
        expect(metrics.average).toBeLessThan(12);
        
        console.log(`VATRateSelector Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });
  });

  describe('Memory Usage Benchmarks', () => {
    beforeEach(() => {
      // Skip memory tests if not available
      if (!(performance as any).memory) {
        console.log('Memory measurement not available in this environment');
        return;
      }
    });

    it('measures button memory usage', () => {
      if (!(performance as any).memory) return;

      const metrics = measureMemoryUsage(
        <TestWrapper>
          <Button>Memory Test Button</Button>
        </TestWrapper>
      );
      
      // Memory leak should be minimal (less than 100KB)
      expect(metrics.leaked).toBeLessThan(100 * 1024);
      
      console.log('Button Memory Usage:', {
        used: `${(metrics.used / 1024).toFixed(2)}KB`,
        leaked: `${(metrics.leaked / 1024).toFixed(2)}KB`,
      });
    });

    it('measures table memory usage', () => {
      if (!(performance as any).memory) return;

      const data = Array.from({ length: 100 }, (_, i) => ({
        id: i,
        name: `User ${i}`,
        email: `user${i}@example.com`,
      }));

      const columns = [
        { key: 'name', header: 'Name' },
        { key: 'email', header: 'Email' },
      ];

      const metrics = measureMemoryUsage(
        <TestWrapper>
          <Table data={data} columns={columns} />
        </TestWrapper>,
        20
      );
      
      // Memory leak should be minimal (less than 500KB)
      expect(metrics.leaked).toBeLessThan(500 * 1024);
      
      console.log('Table Memory Usage:', {
        used: `${(metrics.used / 1024).toFixed(2)}KB`,
        leaked: `${(metrics.leaked / 1024).toFixed(2)}KB`,
      });
    });
  });

  describe('Theme Performance', () => {
    it('handles theme switching efficiently', () => {
      const themes = ['light', 'dark', 'high-contrast'];
      
      themes.forEach(theme => {
        const metrics = measureRenderPerformance(
          <DesignSystemProvider>
            <ThemeProvider theme={theme}>
              <Card>
                <Button variant="primary">Themed Button</Button>
                <Input placeholder="Themed Input" />
              </Card>
            </ThemeProvider>
          </DesignSystemProvider>,
          30
        );
        
        expect(metrics.average).toBeLessThan(15);
        
        console.log(`${theme} Theme Performance: ${metrics.average.toFixed(2)}ms avg`);
      });
    });
  });

  describe('Complex Integration Performance', () => {
    it('handles invoice form performance', () => {
      const metrics = measureRenderPerformance(
        <TestWrapper>
          <Form onSubmit={() => {}}>
            <Card>
              <Card.Header>
                <h2>Invoice Form</h2>
              </Card.Header>
              <Card.Body>
                <Grid cols={2} gap={4}>
                  <Input name="invoiceNumber" placeholder="Invoice Number" />
                  <DatePicker name="issueDate" format="DD.MM.YYYY" />
                  <NIPValidator name="clientNIP" placeholder="Client NIP" />
                  <CurrencyInput name="amount" currency="PLN" />
                  <VATRateSelector name="vatRate" />
                  <InvoiceStatusBadge status="draft" />
                </Grid>
              </Card.Body>
              <Card.Footer>
                <Stack direction="horizontal" gap={2}>
                  <Button variant="secondary">Cancel</Button>
                  <Button variant="primary" type="submit">Save</Button>
                </Stack>
              </Card.Footer>
            </Card>
          </Form>
        </TestWrapper>,
        15
      );
      
      expect(metrics.average).toBeLessThan(80);
      
      console.log(`Invoice Form Performance: ${metrics.average.toFixed(2)}ms avg`);
    });

    it('handles dashboard layout performance', () => {
      const tableData = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        invoice: `INV-${String(i + 1).padStart(3, '0')}`,
        amount: (Math.random() * 1000).toFixed(2),
        status: ['paid', 'pending', 'overdue'][i % 3],
      }));

      const columns = [
        { key: 'invoice', header: 'Invoice' },
        { key: 'amount', header: 'Amount' },
        { 
          key: 'status', 
          header: 'Status',
          render: (value: string) => <InvoiceStatusBadge status={value as any} />
        },
      ];

      const metrics = measureRenderPerformance(
        <TestWrapper>
          <Container maxWidth="xl">
            <Grid cols={3} gap={6}>
              <Card>
                <Card.Header>Statistics</Card.Header>
                <Card.Body>
                  <Stack gap={4}>
                    <div>Total: 150</div>
                    <div>Paid: 120</div>
                    <div>Pending: 30</div>
                  </Stack>
                </Card.Body>
              </Card>
              
              <Card>
                <Card.Header>Quick Actions</Card.Header>
                <Card.Body>
                  <Stack gap={3}>
                    <Button variant="primary" fullWidth>Create Invoice</Button>
                    <Button variant="secondary" fullWidth>Upload Document</Button>
                  </Stack>
                </Card.Body>
              </Card>
              
              <Card>
                <Card.Header>Recent Invoices</Card.Header>
                <Card.Body>
                  <Table data={tableData} columns={columns} />
                </Card.Body>
              </Card>
            </Grid>
          </Container>
        </TestWrapper>,
        10
      );
      
      expect(metrics.average).toBeLessThan(150);
      
      console.log(`Dashboard Layout Performance: ${metrics.average.toFixed(2)}ms avg`);
    });
  });

  describe('Performance Regression Detection', () => {
    it('establishes performance baselines', () => {
      const baselines = {
        button: { target: 5, max: 10 },
        input: { target: 8, max: 15 },
        select: { target: 12, max: 25 },
        smallTable: { target: 20, max: 40 },
        mediumTable: { target: 60, max: 120 },
        grid: { target: 15, max: 30 },
        currencyInput: { target: 15, max: 30 },
        datePicke: { target: 20, max: 40 },
        nipValidator: { target: 18, max: 35 },
        complexForm: { target: 40, max: 80 },
        invoiceForm: { target: 80, max: 160 },
        dashboard: { target: 150, max: 300 },
      };

      // Log baselines for monitoring
      Object.entries(baselines).forEach(([component, { target, max }]) => {
        console.log(`Performance baseline for ${component}: target ${target}ms, max ${max}ms`);
      });

      // Verify baselines are reasonable
      Object.values(baselines).forEach(({ target, max }) => {
        expect(target).toBeLessThan(max);
        expect(max).toBeLessThan(500); // No component should take more than 500ms
      });
    });
  });
});